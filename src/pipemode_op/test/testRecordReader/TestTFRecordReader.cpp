// Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License"). You
// may not use this file except in compliance with the License. A copy of
// the License is located at
//
//     http://aws.amazon.com/apache2.0/
//
// or in the "license" file accompanying this file. This file is
// distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
// ANY KIND, either express or implied. See the License for the specific
// language governing permissions and limitations under the License.

#include <stdexcept>
#include <string>
#include <iostream>
#include <memory>
#include "TFRecordReader.hpp"
#include "TestTFRecordReader.hpp"
#include "common.hpp"
#include "tensorflow/core/platform/tstring.h"

using sagemaker::tensorflow::TFRecordReader;
using sagemaker::tensorflow::TFRecordReaderTest;
using tensorflow::tstring;

#include "tensorflow/core/lib/hash/crc32c.h"

TFRecordReaderTest::TFRecordReaderTest() {}

TFRecordReaderTest::~TFRecordReaderTest() {}

void TFRecordReaderTest::SetUp() {}

void TFRecordReaderTest::TearDown() {}

std::unique_ptr<TFRecordReader> MakeTFRecordReader(std::string path,
    std::size_t read_size, uint32_t max_corrupted_records_to_skip = 0) {
    return std::unique_ptr<TFRecordReader>(
        new TFRecordReader(path, read_size, std::chrono::seconds(1), max_corrupted_records_to_skip));
}

std::unique_ptr<TFRecordReader> MakeTFRecordReader(std::string path) {
    return MakeTFRecordReader(path, 100);
}

std::string ToTFRecord(const std::string& data) {
    std::string result;
    char header[12];
    std::uint64_t length = data.size();
    char* length_ptr = reinterpret_cast<char*>(&length);
    for (int i = 0; i < 8; i++) {
        header[i] = length_ptr[i];
    }
    std::uint32_t masked_crc = tensorflow::crc32c::Mask(tensorflow::crc32c::Value(header, 8));
    char* masked_crc_ptr = reinterpret_cast<char*>(&masked_crc);
    for (int i = 0; i < 4; i++) {
        header[i + 8] = masked_crc_ptr[i];
    }
    for (int i = 0; i < 12; i++) {
        result.push_back(header[i]);
    }
    result += data;
    auto data_crc = tensorflow::crc32c::Mask(tensorflow::crc32c::Value(data.c_str(), length));
    masked_crc_ptr = reinterpret_cast<char*>(&data_crc);
    for (int i = 0; i < 4; i++) {
        result.push_back(masked_crc_ptr[i]);
    }
    return result;
}


TEST_F(TFRecordReaderTest, ReadRecord) {
    std::string encoded = ToTFRecord("hello");
    std::unique_ptr<TFRecordReader> reader = MakeTFRecordReader(
        CreateChannel(CreateTemporaryDirectory(), "elizabeth", encoded, 0), 4);
    tensorflow::tstring record;
    reader->ReadRecord(&record);
    EXPECT_EQ("hello", record);
    EXPECT_FALSE(reader->ReadRecord(&record));
}

TEST_F(TFRecordReaderTest, ReadRecordFails) {
    std::unique_ptr<TFRecordReader> reader = MakeTFRecordReader(
        CreateChannel(CreateTemporaryDirectory(), "elizabeth", "not a record", 0), 4);
    tensorflow::tstring record;
    EXPECT_THROW({
        reader->ReadRecord(&record);},
        std::runtime_error);
}

TEST_F(TFRecordReaderTest, ReadMultipleRecords) {
    std::string rec1 = ToTFRecord("hello");
    std::string rec2 = ToTFRecord("world");
    std::string encoded = rec1 + rec2;
    std::unique_ptr<TFRecordReader> reader = MakeTFRecordReader(
        CreateChannel(CreateTemporaryDirectory(), "elizabeth", encoded, 0), 4);
    tensorflow::tstring record;
    reader->ReadRecord(&record);
    EXPECT_EQ("hello", record);
    reader->ReadRecord(&record);
    EXPECT_EQ("world", record);
    EXPECT_FALSE(reader->ReadRecord(&record));
}

TEST_F(TFRecordReaderTest, FailOnCorruptRecord) {
    // this test fails as soon as a corrupt record is encountered in the record stream
    std::string rec1 = ToTFRecord("hello");
    std::string rec2 = ToTFRecord("world");
    std::string corrupted = rec2;
    corrupted[corrupted.length() - 1] = 'x';
    std::string encoded = rec1 + corrupted;
    std::unique_ptr<TFRecordReader> reader = MakeTFRecordReader(
        CreateChannel(CreateTemporaryDirectory(), "elizabeth", encoded, 0), 4);
    tensorflow::tstring record;
    reader->ReadRecord(&record);
    EXPECT_EQ("hello", record);
    EXPECT_THROW({
        reader->ReadRecord(&record);},
        std::runtime_error);
}

TEST_F(TFRecordReaderTest, SkipCorruptRecords) {
    // in this test we confiigure the reader to tolerate upto 3 consecutive corrupt records
    // and then insert 3 corrupt records into the record stream and see that we skip and
    // parse the next kosher record, however, immediately following it we have 4 corrupt
    // records which will fail parsing the rest of the stream
    uint32_t max_corrupt_records_to_skip = 3;
    std::string rec1 = ToTFRecord("hello");
    std::string rec2 = ToTFRecord("world");
    std::string corrupted = rec2;
    corrupted[corrupted.length() - 1] = 'x';
    std::string encoded = rec1;
    for (int i = 0; i < max_corrupt_records_to_skip; i++) {
        encoded.append(corrupted);
    }
    encoded.append(rec2);
    for (int i = 0; i < max_corrupt_records_to_skip + 1; i++) {
        encoded.append(corrupted);
    }

    std::unique_ptr<TFRecordReader> reader = MakeTFRecordReader(
        CreateChannel(CreateTemporaryDirectory(), "elizabeth", encoded, 0), 4, max_corrupt_records_to_skip);
    tensorflow::tstring record;
    reader->ReadRecord(&record);
    EXPECT_EQ("hello", record);
     // swallow the upto max_corrupt_records_to_skip corrupted recs and successfully parse the next one:
    reader->ReadRecord(&record);
    EXPECT_EQ("world", record);

    // but the next set of corrupted records exceed max_corrupt_records_to_skip, so we get an error:
    EXPECT_THROW({
        reader->ReadRecord(&record);},
        std::runtime_error);
}
