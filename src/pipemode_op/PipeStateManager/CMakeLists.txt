file(GLOB_RECURSE sources ./*.cpp ./*.hpp)

add_library(PipeStateManager STATIC ${sources})

target_compile_options(PipeStateManager PUBLIC "-D_GLIBCXX_USE_CXX11_ABI=0")
target_compile_options(PipeStateManager PUBLIC "-fPIC")
target_compile_options(PipeStateManager PUBLIC "-g")

target_include_directories(PipeStateManager PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)