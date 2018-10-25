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

#include <nsync.h>
#include <sys/stat.h>

#include <chrono>
#include <iostream>
#include <string>
#include <thread>

#include "tensorflow/core/framework/common_shape_fns.h"
#include "tensorflow/core/framework/op.h"
#include "tensorflow/core/framework/op_def_builder.h"
#include "tensorflow/core/framework/shape_inference.h"
#include "tensorflow/core/framework/dataset.h"

#include "PipeStateManager.hpp"
#include "RecordIOReader.hpp"
#include "TextLineRecordReader.hpp"
#include "TFRecordReader.hpp"

using sagemaker::tensorflow::PipeStateManager;
using sagemaker::tensorflow::RecordIOReader;
using sagemaker::tensorflow::RecordReader;
using sagemaker::tensorflow::TextLineRecordReader;
using sagemaker::tensorflow::TFRecordReader;

using tensorflow::DatasetBase;
using tensorflow::SerializationContext;
using tensorflow::DatasetContext;
using tensorflow::DatasetIterator;
using tensorflow::DatasetOpKernel;
using tensorflow::DataTypeVector;
using tensorflow::DEVICE_CPU;
using tensorflow::DT_STRING;
using tensorflow::DatasetBase;
using tensorflow::IteratorBase;
using tensorflow::IteratorContext;
using tensorflow::IteratorStateReader;
using tensorflow::IteratorStateWriter;
using tensorflow::mutex;
using tensorflow::mutex_lock;
using tensorflow::Node;
using tensorflow::OpKernelContext;
using tensorflow::PartialTensorShape;
using tensorflow::Status;
using tensorflow::Tensor;
using tensorflow::TensorShape;

std::string BuildPipeName(const std::string& channel_directory,
    const std::string& channel_name, const uint32_t pipe_index) {
    std::string pipe_name = channel_name + "_" + std::to_string(pipe_index);
    std::string channel_path = channel_directory;
    if (channel_path[channel_path.length() - 1] != '/') {
        channel_path += '/';
    }
    channel_path += pipe_name;
    return channel_path;
}

/**
   A TensorFlow DatasetOpKernel that creates Datasets that read records
   from a SageMaker PipeMode Linux named pipe.

   A PipemodeDatasetOp requires the following arguments:
   - state_directory [string]: A directory to store pipe index state
   - channel [string]: The name of the SageMaker channel to read
   - channel_directory [string]: The folder where SageMaker pipe mode fifos are created
  */
class PipeModeDatasetOp : public DatasetOpKernel {
 public:
    using DatasetOpKernel::DatasetOpKernel;

    void MakeDataset(OpKernelContext* ctx, DatasetBase** output) override {
        std::string record_format;
        std::string state_directory;
        std::string channel_directory;
        std::string channel;
        bool benchmark;
        OP_REQUIRES_OK(ctx, ParseScalarArgument<std::string>(ctx, "record_format",
                                                        &record_format));
        OP_REQUIRES_OK(ctx, ParseScalarArgument<std::string>(ctx, "state_directory",
                                                        &state_directory));
        OP_REQUIRES_OK(ctx, ParseScalarArgument<std::string>(ctx, "channel_directory",
                                                        &channel_directory));
        OP_REQUIRES_OK(ctx, ParseScalarArgument<std::string>(ctx, "channel",
                                                        &channel));
        OP_REQUIRES(ctx, record_format == "RecordIO" || record_format == "TFRecord" || record_format == "TextLine",
            tensorflow::errors::InvalidArgument("Invalid record format: " + record_format));
        OP_REQUIRES_OK(ctx, ParseScalarArgument<bool>(ctx, "benchmark",
                                                        &benchmark));
        *output = new Dataset(ctx, record_format, state_directory, channel_directory, channel, benchmark);
    }

 private:
    class Dataset : public DatasetBase {
     public:
        explicit Dataset(OpKernelContext* ctx, const std::string& record_format, const std::string& state_directory,
            const std::string& channel_directory, const std::string& channel, bool benchmark):
            DatasetBase(DatasetContext(ctx)),
            record_format_(record_format),
            channel_directory_(channel_directory),
            pipe_state_manager_(state_directory, channel),
            channel_(channel),
            benchmark_(benchmark) {}

        std::unique_ptr<IteratorBase> MakeIteratorInternal(const std::string& prefix) const override {
            auto new_prefix = prefix + "::PipeMode-" + channel_ + "-"
                + std::to_string(pipe_state_manager_.GetPipeIndex());
            auto ptr = std::unique_ptr<IteratorBase>(
                new Iterator({this, new_prefix}, record_format_, channel_directory_, channel_, benchmark_,
                    pipe_state_manager_.GetPipeIndex()));
            pipe_state_manager_.IncrementPipeIndex();
            return ptr;
        }

        const DataTypeVector& output_dtypes() const override {
            static DataTypeVector* dtypes = new DataTypeVector({DT_STRING});
            return *dtypes;
        }

        const std::vector<PartialTensorShape>& output_shapes() const override {
            static std::vector<PartialTensorShape>* shapes =
            new std::vector<PartialTensorShape>({{}});
            return *shapes;
        }

        std::string DebugString() const override { return "PipeModeDatasetOp::Dataset"; }

     protected:
        Status AsGraphDefInternal(SerializationContext* ctx,
                                  DatasetGraphDefBuilder* b,
                                  Node** output) const override {
            throw std::runtime_error("Conversion to GraphDef is not supported.");
        }

     private:
        std::string record_format_;
        std::string channel_directory_;
        std::string channel_;
        PipeStateManager pipe_state_manager_;
        bool benchmark_;

        class Iterator : public DatasetIterator<Dataset> {
         public:
            explicit Iterator(const Params& params, const std::string& record_format,
                const std::string& channel_directory, const std::string& channel, const bool benchmark,
                const uint32_t pipe_index)
                : DatasetIterator<Dataset>(params), read_time_(0), read_bytes_(0),
                    benchmark_(benchmark) {
                    std::string pipe_path = BuildPipeName(channel_directory, channel, pipe_index);
                    if (record_format == "RecordIO") {
                        record_reader_ = std::unique_ptr<RecordReader>(new RecordIOReader(pipe_path));
                    } else if (record_format == "TFRecord") {
                        record_reader_ = std::unique_ptr<RecordReader>(new TFRecordReader(pipe_path));
                    } else {  // required to be TextLine
                        record_reader_ = std::unique_ptr<RecordReader>(new TextLineRecordReader(pipe_path));
                    }
                }

            Status GetNextInternal(IteratorContext* ctx,
                                 std::vector<Tensor>* out_tensors,
                                 bool* end_of_sequence) override {
                *end_of_sequence = false;
                Tensor result_tensor(DT_STRING, TensorShape({}));
                std::string* storage = &result_tensor.scalar<std::string>()();
                try {
                    mutex_lock l(mu_);
                    auto start = std::chrono::high_resolution_clock::now();
                    if (record_reader_->ReadRecord(storage)) {
                        out_tensors->emplace_back(std::move(result_tensor));
                    } else {
                        *end_of_sequence = true;
                    }
                    auto end = std::chrono::high_resolution_clock::now();
                    read_time_ = read_time_ + std::chrono::duration_cast<std::chrono::nanoseconds>(end - start);
                    read_bytes_ += storage->size();
                } catch(std::runtime_error& err) {
                    return Status(tensorflow::error::INTERNAL, err.what());
                }
                return Status::OK();
            }
            ~Iterator() {
                if (benchmark_) {
                    int64_t read_time_ms = std::chrono::duration_cast<std::chrono::milliseconds>(read_time_).count();
                    std::cout << "PipeModeDatasetOp::Dataset::Iterator read_time_ms: " << read_time_ms << std::endl;
                    std::cout << "PipeModeDatasetOp::Dataset::Iterator read_bytes: " << read_bytes_  << std::endl;
                    auto read_giga_bytes = read_bytes_ / std::pow(1024, 3);
                    double read_seconds = read_time_ms / 1000.0;
                    std::cout << "PipeModeDatasetOp::Dataset::Iterator read_GB/s: "
                        << read_giga_bytes / read_seconds << std::endl;
                }
            }

         private:
            bool benchmark_;
            mutex mu_;
            std::unique_ptr<RecordReader> record_reader_
                GUARDED_BY(mu_);
            std::chrono::nanoseconds read_time_;
            std::uint64_t read_bytes_;
        };
    };
};

REGISTER_KERNEL_BUILDER(Name("PipeModeDataset").Device(DEVICE_CPU),
                        PipeModeDatasetOp);
REGISTER_OP("PipeModeDataset")
    .Input("benchmark: bool")
    .Input("record_format: string")
    .Input("state_directory: string")
    .Input("channel: string")
    .Input("channel_directory: string")
    .Output("handle: variant")
    .SetIsStateful()
    .SetShapeFn(tensorflow::shape_inference::ScalarShape);
