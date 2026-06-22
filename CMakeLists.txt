cmake_minimum_required(VERSION 3.15)
project(FishingStealthEngine LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ==============================================================================
# ⚡ PERBAIKAN UTAMA: STATIC RUNTIME LINKAGE SELECTION (/MT)
# ==============================================================================
# Memaksa MSVC mengemas C/C++ Runtime Library secara statis ke dalam .exe
# Wajib ada agar klop dengan OpenCV versi x64-windows-static dari vcpkg
set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")

# Optimasi Compiler MSVC untuk performa maksimal dan biner ringkas
if(MSVC)
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /O2 /Oi /Gy /GL /DNDEBUG")
    set(CMAKE_EXE_LINKER_FLAGS_RELEASE "${CMAKE_EXE_LINKER_FLAGS_RELEASE} /LTCG")
endif()

# Cari paket OpenCV via vcpkg
find_package(OpenCV REQUIRED)

# Daftarkan seluruh file implementasi source code
add_executable(FishingEngine 
    src/main.cpp
)

# Berikan akses ke direktori include header internal dan OpenCV
target_include_directories(FishingEngine PRIVATE src ${OpenCV_INCLUDE_DIRS})
target_link_libraries(FishingEngine PRIVATE ${OpenCV_LIBS})

# Output biner diatur ke folder Release
set_target_properties(FishingEngine PROPERTIES
    OUTPUT_NAME "FishingEngine"
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/Release"
)
