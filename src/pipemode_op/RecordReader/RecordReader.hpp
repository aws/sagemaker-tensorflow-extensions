#ifndef SRC_PIPEMODE_OP_RECORDREADER_RECORDREADER_HPP_
#define SRC_PIPEMODE_OP_RECORDREADER_RECORDREADER_HPP_

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
#include <stdexcept>
#include <exception>
#include <thread>
#include <chrono>

namespace sagemaker {
namespace tensorflow {

#define DEFAULT_CAPACITY 1048576
#define DEFAULT_READ_SIZE 65536
#define DEFAULT_FILE_CREATION_TIMEOUT std::chrono::seconds(120)

/**
   An abstract record reader. Records are byte sequences read from a file. 

   Instances of this class read bytes from an open file into a read-ahead
   buffer. The buffer has a fixed capacity and a fixed number of bytes
   are repeatedly read from the open file to fill the buffer. Sub-classes
   may access this read ahead buffer to retrieve bytes read from the file.

   Instances of this class are not thread-safe.
  */
class RecordReader {
 public:
    /**
       Constructs a new RecordReader that reads records from a file.
    
       param [in] file_path: The path and name of the file to open.
       param [in] buffer_capacity: The size of the read ahead buffer, in bytes.
       param [in] read_size: The number of bytes to read from the open file when
                             filling the read-ahead buffer.
       param [in] file_creation_timeout: The number of seconds to wait for the file
                                         being read to exist.
     */
    RecordReader(const std::string& file_path, const std::size_t buffer_capacity, const std::size_t read_size,
                 const std::chrono::seconds file_creation_timeout);

    /**
       Constructs a new RecordReader that reads records from a file. Uses default values
       for buffer_capacity and read_size.
       
       param [in] file_path: The path and name of the file to open.
     */
    explicit RecordReader(const std::string& file_path) : RecordReader(file_path, DEFAULT_CAPACITY, DEFAULT_READ_SIZE,
        DEFAULT_FILE_CREATION_TIMEOUT) {}

    RecordReader(const RecordReader&) = delete;
    RecordReader& operator=(const RecordReader&) = delete;
    RecordReader(RecordReader&&) = delete;
    RecordReader& operator=(RecordReader&&) = delete;

    /**
       Closes the file opened by this RecordReader.
     */
    ~RecordReader();

    /**
       Reads a record from the underlying file and stores the record data in the 
       specified string pointer. The specified string is resized to accomodate the record.

       param [out] storage The string where the record is written to.
       return true if a record could be read, false otherwise.
     */
    virtual bool ReadRecord(std::string* storage) = 0;

 protected:
    /**
       Attempt to fill the read-ahead buffer. After this method returns, if the buffer
       is not full, then the EOF has been reached.
     */
    void FillBuffer();

    /**
       Read bytes from the file into a byte array. This method self-calls FillBuffer 
       as necessary to fill the read-ahead buffer before moving the read bytes into data.

       param [out] data The byte array to write into.
       param [in] nbytes The number of bytes to read.

       return the number of bytes read
     */
    std::size_t Read(void* data, std::size_t nbytes);

    /**
       Read a line characters from the underlying file, storing the result
       in data. Existing characters in data are removed and the line data is written
       into data starting at index 0.

       This method self-calls FillBuffer as necessary to fill the read-ahead buffer before
       moving the read bytes into data.

       param [in] data The string to read the line into.
       param [in] delim The record breaking delimiter

       return true if a line of data was read, false otherwise.
      */
    bool ReadLine(std::string* data, const char delim);

    /**
       Wait for the file this RecordReader is reading to be created.
     */
    void WaitForFile();

 private:
    // The file descriptor of the file being read
    int fd_;

    // The path of the file being read
    const std::string file_path_;

    // The read-ahead buffer
    char* buffer_;

    // The maximum number of bytes that can be stored in the read-ahead buffer
    std::size_t capacity_;

    // The current number of bytes stored in the read-ahead buffer
    std::size_t volume_;

    // The location of the next byte to read from the read-ahead buffer
    std::size_t offset_;

    // The number of bytes to read from the open file when filling the read-ahead
    // buffer
    std::size_t read_size_;

    // The number of seconds to wait for the file being read to exist. Measured from
    // the first invocation of Read. Defaults to 120 seconds.
    std::chrono::seconds file_creation_timeout_;
};
}  // namespace tensorflow
}  // namespace sagemaker

#endif  // SRC_PIPEMODE_OP_RECORDREADER_RECORDREADER_HPP_
