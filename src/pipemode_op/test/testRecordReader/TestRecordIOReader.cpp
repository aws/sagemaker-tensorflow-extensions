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

#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <fstream>
#include <string>
#include <vector>
#include <RecordReader.hpp>
#include <RecordIOReader.hpp>
#include "common.hpp"
#include "TestRecordIOReader.hpp"

using sagemaker::tensorflow::RecordIOReaderTest;
using sagemaker::tensorflow::RecordIOReader;


RecordIOReaderTest::RecordIOReaderTest() {}

RecordIOReaderTest::~RecordIOReaderTest() {}

void RecordIOReaderTest::SetUp() {}

void RecordIOReaderTest::TearDown() {}

std::string ToRecordIO(const std::string& data) {
    std::vector<char> vec(8);

    vec[0] = 0xa;
    vec[1] = 0x23;
    vec[2] = 0xd7;
    vec[3] = 0xce;

    std::uint32_t length = data.size();
    char* plength = reinterpret_cast<char*>(&length);

    vec[4] = *(plength + 0);
    vec[5] = *(plength + 1);
    vec[6] = *(plength + 2);
    vec[7] = *(plength + 3);

    vec.insert(vec.end(), data.begin(), data.end());
    std::uint32_t padding = (4 - (length % 4)) % 4;
    for (int i = 0; i < padding; i++) {
        vec.push_back(' ');
    }

    std::string encoding;
    encoding.insert(encoding.begin(), vec.begin(), vec.end());
    return encoding;
}

std::unique_ptr<RecordIOReader> MakeRecordIOReader(std::string path,
    std::size_t read_size) {
    return std::unique_ptr<RecordIOReader>(new RecordIOReader(path, read_size, std::chrono::seconds(120)));
}


TEST_F(RecordIOReaderTest, InvalidMagicNumber) {
    std::unique_ptr<RecordIOReader> ptr = MakeRecordIOReader(CreateChannel(CreateTemporaryDirectory(),
        "elizabeth", "not a magic number", 0), 4);
    std::string storage;
    EXPECT_THROW({
        ptr->ReadRecord(&storage);},
        std::runtime_error);
}

TEST_F(RecordIOReaderTest, TestReadSingleRecord) {
    std::string input = "Elizabeth Is 10 months Old";
    std::string encoded = ToRecordIO(input);
    std::unique_ptr<RecordIOReader> ptr = MakeRecordIOReader(
        CreateChannel(CreateTemporaryDirectory(), "elizabeth", encoded, 0), 4);
    std::string storage;
    ptr->ReadRecord(&storage);
    EXPECT_EQ(input, storage);
}


TEST_F(RecordIOReaderTest, TestReadMultipleRecords) {
    std::string channel_dir = CreateTemporaryDirectory();
    std::string input = "abcd";
    std::string multi_record;
    for (int i = 0; i < 2; i++) {
        multi_record += ToRecordIO(input + std::to_string(i));
    }
    std::unique_ptr<RecordIOReader> ptr = MakeRecordIOReader(
        CreateChannel(CreateTemporaryDirectory(), "elizabeth", multi_record, 0), 4);
    for (int i = 0; i < 2; i++) {
        std::string result;
        ptr->ReadRecord(&result);
        EXPECT_EQ(input + std::to_string(i), result);
    }
}

TEST_F(RecordIOReaderTest, TestLargeRecords) {
    std::string channel_dir = CreateTemporaryDirectory();
    std::string input;
    for (int i = 0; i < 2000000; i++) {
        input.push_back('S');
    }
    std::string multi_record;
    for (int i = 0; i < 2; i++) {
        multi_record += ToRecordIO(input);
    }
    std::unique_ptr<RecordIOReader> ptr = MakeRecordIOReader(
        CreateChannel(CreateTemporaryDirectory(), "elizabeth", multi_record, 0), 65536);

    for (int i = 0; i < 2; i++) {
        std::string result;
        ptr->ReadRecord(&result);
        EXPECT_EQ(input, result);
    }
}

TEST_F(RecordIOReaderTest, TestManyRecords) {
    std::string channel_dir = CreateTemporaryDirectory();
    std::string input;
    for (int i = 0; i < 2; i++) {
        input.push_back('S');
    }
    std::string multi_record;
    for (int i = 0; i < 2000000; i++) {
        multi_record += ToRecordIO(input);
    }
    std::unique_ptr<RecordIOReader> ptr = MakeRecordIOReader(
        CreateChannel(CreateTemporaryDirectory(), "elizabeth", multi_record, 0), 65536);

    for (int i = 0; i < 2000000; i++) {
        std::string result;
        ptr->ReadRecord(&result);
        EXPECT_EQ(input, result);
    }
}
