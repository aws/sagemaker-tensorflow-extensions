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
     /**
       Constructs a new RecordReader that reads records from a file.

       param [in] file_path: The path and name of the file to open.
       param [in] read_size: The preferred number of bytes to read from the open file
                             during invocation of Read.
       param [in] file_creation_timeout: The number of seconds to wait for the file
                                         being read to exist.
     */
    TFRecordReader(const std::string& file_path, const std::size_t read_size,
                 const std::chrono::seconds file_creation_timeout,
                 const uint32_t max_corrupted_records_to_skip):
                 RecordReader(file_path, read_size, file_creation_timeout),
                 max_corrupted_records_to_skip_(max_corrupted_records_to_skip) {}

     /**
       Constructs a new TFRecordReader that reads records from a file.

       param [in] file_path: The path and name of the file to open.
       param [in] max_corrupted_records_to_skip: the number of corrupted records
                             encountered in sequence that it's ok to skip.
     */
    TFRecordReader(const std::string& file_path,
                   const uint32_t max_corrupted_records_to_skip = 0):
                 RecordReader(file_path),
                 max_corrupted_records_to_skip_(max_corrupted_records_to_skip) {}

    bool ReadRecord(std::string* storage) override;

 private:
    std::uint32_t max_corrupted_records_to_skip_;
};

}  // namespace tensorflow
}  // namespace sagemaker
#endif  // SRC_PIPEMODE_OP_RECORDREADER_TFRECORDREADER_HPP_
