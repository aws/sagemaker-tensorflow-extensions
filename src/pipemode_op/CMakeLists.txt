cmake_minimum_required(VERSION 3.10)
enable_language(CXX)

set(CMAKE_CXX_STANDARD 11)
set(CURL_LIBRARY "-lcurl") 

find_package(CURL REQUIRED) 

project(TFPipeModeDataset)

enable_testing()

add_subdirectory(PipeStateManager)
add_subdirectory(RecordReader)
add_subdirectory(Dataset)
add_subdirectory(test)
