#ifndef SRC_PIPEMODE_OP_RECORDREADER_RECORDIOREADER_HPP_
#define SRC_PIPEMODE_OP_RECORDREADER_RECORDIOREADER_HPP_

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

#include <string>
#include "RecordReader.hpp"
#include "tensorflow/core/platform/tstring.h"

using tensorflow::tstring;

namespace sagemaker {
namespace tensorflow {

/**
   A RecordReader that reads RecordIO encoded records.

   Instances of this class use the MXNet RecordIO format, defined here: 
   https://mxnet.incubator.apache.org/architecture/note_data_loading.html
 */
class RecordIOReader : public RecordReader {
    using RecordReader::RecordReader;

 public:
    bool ReadRecord(::tensorflow::tstring* storage) override;
};

}  // namespace tensorflow
}  // namespace sagemaker
#endif  // SRC_PIPEMODE_OP_RECORDREADER_RECORDIOREADER_HPP_
