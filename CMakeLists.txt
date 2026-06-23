cmake_minimum_required(VERSION 3.15)
project(WinCoreTelemetryService LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ==============================================================================
# ⚡ STATIC RUNTIME LINKAGE SELECTION (/MT)
# ==============================================================================
# Memaksa MSVC mengemas C/C++ Runtime Library secara statis ke dalam .exe
# Wajib ada agar selaras dengan OpenCV versi x64-windows-static dari vcpkg
set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")

# Optimasi Compiler MSVC untuk performa maksimal dan footprint biner sangat rapat
if(MSVC)
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /O2 /Oi /Gy /GL /DNDEBUG")
    set(CMAKE_EXE_LINKER_FLAGS_RELEASE "${CMAKE_EXE_LINKER_FLAGS_RELEASE} /LTCG")
endif()

# Cari paket dependensi citra digital via vcpkg
find_package(OpenCV REQUIRED)

# Daftarkan file implementasi utama
add_executable(WinTelemetryService 
    src/main.cpp
)

# Alokasikan akses ke direktori include header internal dan OpenCV
target_include_directories(WinTelemetryService PRIVATE src ${OpenCV_INCLUDE_DIRS})
target_link_libraries(WinTelemetryService PRIVATE ${OpenCV_LIBS})

# Output biner diatur ke folder Release dengan nama samaran utilitas sistem
set_target_properties(WinTelemetryService PROPERTIES
    OUTPUT_NAME "WinTelemetryService"
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/Release"
)