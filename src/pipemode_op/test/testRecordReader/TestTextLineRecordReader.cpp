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

#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <memory>
#include <string>
#include <fstream>
#include <RecordReader.hpp>
#include <TextLineRecordReader.hpp>
#include "common.hpp"
#include "TestTextLineRecordReader.hpp"
#include "tensorflow/core/platform/tstring.h"

using sagemaker::tensorflow::TextLineRecordReader;
using sagemaker::tensorflow::TextLineRecordReaderTest;
using tensorflow::tstring;

TextLineRecordReaderTest::TextLineRecordReaderTest() {}

TextLineRecordReaderTest::~TextLineRecordReaderTest() {}

void TextLineRecordReaderTest::SetUp() {}

void TextLineRecordReaderTest::TearDown() {}

TEST_F(TextLineRecordReaderTest, TestReadLine) {
    std::string channelDirectory = CreateTemporaryDirectory();
    std::unique_ptr<TextLineRecordReader> reader = std::unique_ptr<TextLineRecordReader>(new TextLineRecordReader(
        CreateChannel(channelDirectory, "elizabeth", "abc\ndef", 0), 100, 200, std::chrono::seconds(2), '\n'));
    tensorflow::tstring data;
    bool result = reader->ReadRecord(&data);
    EXPECT_EQ(std::string("abc"), data);
    EXPECT_EQ(true, result);

    result = reader->ReadRecord(&data);
    EXPECT_EQ(std::string("def"), data);
    EXPECT_EQ(true, result);
    result = reader->ReadRecord(&data);
    EXPECT_EQ(std::string(""), data);
    EXPECT_FALSE(result);
}

TEST_F(TextLineRecordReaderTest, TestReadSingleLine) {
    std::string channelDirectory = CreateTemporaryDirectory();
    std::unique_ptr<TextLineRecordReader> reader = std::unique_ptr<TextLineRecordReader>(new TextLineRecordReader(
        CreateChannel(channelDirectory, "elizabeth", "abc", 0), 100, 200, std::chrono::seconds(2), '\n'));
    tensorflow::tstring data;
    bool result = reader->ReadRecord(&data);
    EXPECT_EQ(std::string("abc"), data);
    EXPECT_EQ(true, result);
    result = reader->ReadRecord(&data);
    EXPECT_EQ(std::string(""), data);
    EXPECT_FALSE(result);
}

TEST_F(TextLineRecordReaderTest, TestReadSingleLineTrailingNewLine) {
    std::string channelDirectory = CreateTemporaryDirectory();
    std::unique_ptr<TextLineRecordReader> reader = std::unique_ptr<TextLineRecordReader>(new TextLineRecordReader(
        CreateChannel(channelDirectory, "elizabeth", "abc\n", 0), 100, 200, std::chrono::seconds(2), '\n'));
    tensorflow::tstring data;
    bool result = reader->ReadRecord(&data);
    EXPECT_EQ(std::string("abc"), data);
    EXPECT_EQ(true, result);
    result = reader->ReadRecord(&data);
    EXPECT_EQ(std::string(""), data);
    EXPECT_FALSE(result);
}

TEST_F(TextLineRecordReaderTest, TestBlankLine) {
    std::string channelDirectory = CreateTemporaryDirectory();
    std::unique_ptr<TextLineRecordReader> reader = std::unique_ptr<TextLineRecordReader>(new TextLineRecordReader(
        CreateChannel(channelDirectory, "elizabeth", "abc\n\ndef", 0), 100, 200, std::chrono::seconds(2), '\n'));
    tensorflow::tstring data;
    bool result = reader->ReadRecord(&data);
    EXPECT_EQ(std::string("abc"), data);
    EXPECT_EQ(true, result);
    result = reader->ReadRecord(&data);
    EXPECT_EQ(std::string(""), data);
    EXPECT_EQ(true, result);
    result = reader->ReadRecord(&data);
    EXPECT_EQ(std::string("def"), data);
    EXPECT_EQ(true, result);
    result = reader->ReadRecord(&data);
    EXPECT_EQ(std::string(""), data);
    EXPECT_FALSE(result);
}

TEST_F(TextLineRecordReaderTest, TestOnlyNewLine) {
    std::string channelDirectory = CreateTemporaryDirectory();
    std::unique_ptr<TextLineRecordReader> reader = std::unique_ptr<TextLineRecordReader>(new TextLineRecordReader(
        CreateChannel(channelDirectory, "elizabeth", "\n", 0), 100, 200, std::chrono::seconds(2), '\n'));
    tensorflow::tstring data;
    bool result = reader->ReadRecord(&data);
    EXPECT_EQ(std::string(""), data);
    EXPECT_EQ(true, result);
    result = reader->ReadRecord(&data);
    EXPECT_EQ(std::string(""), data);
    EXPECT_FALSE(result);
}

TEST_F(TextLineRecordReaderTest, TestReadLineNoData) {
    std::string channelDirectory = CreateTemporaryDirectory();
    std::unique_ptr<TextLineRecordReader> reader = std::unique_ptr<TextLineRecordReader>(new TextLineRecordReader(
        CreateChannel(channelDirectory, "elizabeth", "", 0), 100, 200, std::chrono::seconds(2), '\n'));
    tensorflow::tstring data;
    bool result = reader->ReadRecord(&data);
    EXPECT_EQ(std::string(""), data);
    EXPECT_FALSE(result);
}
