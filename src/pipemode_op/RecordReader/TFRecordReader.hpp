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

#ifndef SRC_PIPEMODE_OP_RECORDREADER_TFRECORDREADER_HPP_
#define SRC_PIPEMODE_OP_RECORDREADER_TFRECORDREADER_HPP_

#include <string>
#include "RecordReader.hpp"

using sagemaker::tensorflow::tstring;

namespace sagemaker {
namespace tensorflow {

/**
   A RecordReader that reads tfrecord encoded records.

   Instances of this class read records encoded using the tfrecord
   format, as defined in: https://www.tensorflow.org/api_guides/python/python_io
 */
class TFRecordReader : public RecordReader {
    using RecordReader::RecordReader;

 public:
    bool ReadRecord(tensorflow::tstring* storage) override;
};

}  // namespace tensorflow
}  // namespace sagemaker
#endif  // SRC_PIPEMODE_OP_RECORDREADER_TFRECORDREADER_HPP_
