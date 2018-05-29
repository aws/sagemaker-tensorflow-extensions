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
#include <string>
#include <fstream>
#include <RecordReader.hpp>
#include <RecordIOReader.hpp>
#include "common.hpp"
#include "TestRecordReader.hpp"

using sagemaker::tensorflow::RecordReader;
using sagemaker::tensorflow::RecordReaderTest;

RecordReaderTest::RecordReaderTest() {}

RecordReaderTest::~RecordReaderTest() {}

void RecordReaderTest::SetUp() {}

void RecordReaderTest::TearDown() {}

class TestReader : RecordReader {
 public:
        using RecordReader::RecordReader;

        bool ReadRecord(std::string* storage) override {
            return false;
        }

        // make Read public for testing
        std::size_t WrapRead(void* buffer, std::size_t size) {
            return Read(buffer, size);
        }

        // make WaitForFile public for testing
        void WrapWaitForFile() {
            WaitForFile();
        }
};

std::unique_ptr<TestReader> MakeReader(std::string channelDirectory) {
    return std::unique_ptr<TestReader>(new TestReader(
        CreateChannel(channelDirectory, "elizabeth", "abc", 0)));
}

std::unique_ptr<TestReader> MakeReader(std::string channelDirectory, std::chrono::seconds timeout) {
    return std::unique_ptr<TestReader>(new TestReader(
        CreateChannel(channelDirectory, "elizabeth", "abc", 0), 100, timeout));
}

TEST_F(RecordReaderTest, CanOpenFile) {
    std::string channelDirectory = CreateTemporaryDirectory();
    MakeReader(channelDirectory);
}

TEST_F(RecordReaderTest, ReadPipe) {
    std::string channelDirectory = CreateTemporaryDirectory();
    std::unique_ptr<TestReader> reader = MakeReader(channelDirectory);
    char buffer[4];  // 3 + 1 for the \0
    buffer[3] = '\0';
    size_t readNum = reader->WrapRead(static_cast<void*>(buffer), 4);
    EXPECT_STREQ("abc", buffer);
    EXPECT_EQ(3, readNum);
}

TEST_F(RecordReaderTest, ReadPipeAfterEOF) {
    std::string channelDirectory = CreateTemporaryDirectory();
    std::unique_ptr<TestReader> reader = MakeReader(channelDirectory);
    char buffer[4];
    buffer[3] = '\0';
    size_t readNum = reader->WrapRead(static_cast<void*>(buffer), 4);
    EXPECT_STREQ("abc", buffer);
    readNum = reader->WrapRead(static_cast<void*>(buffer), 1);
    EXPECT_EQ(0, readNum);
}

TEST_F(RecordReaderTest, WaitForFile) {
    std::string channelDirectory = CreateTemporaryDirectory();
    std::unique_ptr<TestReader> reader = MakeReader(channelDirectory, std::chrono::seconds(2));
    reader->WrapWaitForFile();
}

TEST_F(RecordReaderTest, WaitForFileFails) {
    std::string channelDirectory = CreateTemporaryDirectory();
    auto timeout = std::chrono::seconds(2);
    std::unique_ptr<TestReader> reader = std::unique_ptr<TestReader>(
        new TestReader(channelDirectory + "/missing.file", 200, timeout));
    EXPECT_THROW({
        reader->WrapWaitForFile();},
        std::runtime_error);
}
