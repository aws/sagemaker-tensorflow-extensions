#include <string>
#include "common.hpp"

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

std::string CreateTemporaryDirectory() {
    char mkdTemplate[] = "/tmp/tmpdir.XXXXXX";
    return std::string(mkdtemp(mkdTemplate));
}

std::string CreateChannel(const std::string& channel_directory, const std::string& channel_name,
    const std::string data, unsigned int index) {

    std::string pipe_name = channel_name + "_" + std::to_string(index);
    std::string channel_path = channel_directory;
    if (channel_path[channel_path.length() - 1] != '/') {
        channel_path += '/';
    }
    channel_path += pipe_name;
    std::ofstream writer(channel_path, std::ios::binary);
    writer.write(data.data(), data.size());
    return channel_path;
}
