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
#include <string>
#include <fstream>
#include <PipeStateManager.hpp>
#include "TestPipeStateManager.hpp"

using sagemaker::tensorflow::PipeStateManager;
using sagemaker::tensorflow::PipeStateManagerTest;

PipeStateManagerTest::PipeStateManagerTest() {}

PipeStateManagerTest::~PipeStateManagerTest() {}

void PipeStateManagerTest::SetUp() {}

void PipeStateManagerTest::TearDown() {}

std::string CreateTemporaryDirectory() {
    char mkdTemplate[] = "/tmp/tmpdir.XXXXXX";
    return std::string(mkdtemp(mkdTemplate));
}

TEST_F(PipeStateManagerTest, Initial) {
    std::string temp_dir = CreateTemporaryDirectory();
    PipeStateManager m(temp_dir, "some_channel");
    EXPECT_EQ(0, m.GetPipeIndex());
}

TEST_F(PipeStateManagerTest, TestInc) {
    std::string temp_dir = CreateTemporaryDirectory();
    PipeStateManager m(temp_dir, "some_channel");
    m.IncrementPipeIndex();
    EXPECT_EQ(1, m.GetPipeIndex());
}

TEST_F(PipeStateManagerTest, TestRecreate) {
    std::string temp_dir = CreateTemporaryDirectory();
    PipeStateManager m(temp_dir, "some_channel");
    m.IncrementPipeIndex();
    PipeStateManager m1(temp_dir, "some_channel");
    EXPECT_EQ(1, m1.GetPipeIndex());
}

TEST_F(PipeStateManagerTest, TestTwoChannels) {
    std::string temp_dir = CreateTemporaryDirectory();
    PipeStateManager m(temp_dir, "some_channel");
    PipeStateManager m1(temp_dir, "some_other_channel");
    m1.IncrementPipeIndex();
    EXPECT_EQ(0, m.GetPipeIndex());
    EXPECT_EQ(1, m1.GetPipeIndex());
}
