
#ifndef SRC_PIPEMODE_OP_TEST_TESTRECORDREADER_TESTTFRECORDREADER_HPP_
#define SRC_PIPEMODE_OP_TEST_TESTRECORDREADER_TESTTFRECORDREADER_HPP_

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

#include "gtest/gtest.h"
#include "gmock/gmock.h"

namespace sagemaker {
namespace tensorflow {
class TFRecordReaderTest : public ::testing::Test {
 protected:
    TFRecordReaderTest();

    virtual ~TFRecordReaderTest();

    virtual void SetUp();

    virtual void TearDown();
};
}  // namespace tensorflow
}  // namespace sagemaker
#endif  // SRC_PIPEMODE_OP_TEST_TESTRECORDREADER_TESTTFRECORDREADER_HPP_
