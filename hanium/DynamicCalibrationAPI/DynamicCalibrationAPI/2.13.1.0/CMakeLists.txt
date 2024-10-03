
# Set minimum required CMake version
cmake_minimum_required(VERSION 3.1.0)

# Integrity
if (${CMAKE_SOURCE_DIR} STREQUAL ${CMAKE_BINARY_DIR})
MESSAGE( FATAL_ERROR "In-source builds not allowed. Please specify a build directory!")
endif()

set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})


if (CMAKE_SYSTEM_PROCESSOR MATCHES "(amd64) | (AMD64)")
    set (CPU_INTEL TRUE)
else()
    set (CPU_INTEL FALSE)
endif()

SET(__D400_USE_LIBREALSENSE__ TRUE)

# Name the project
project (rs-dynamic-calibration-api-samples)

# Enable C++11
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED TRUE)

if(COMPILER_SUPPORTS_CXX11)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
elseif(COMPILER_SUPPORTS_CXX0X)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++0x")
endif()

if(MSVC)
    if(BUILD_WITH_STATIC_CRT)
      set(CMAKE_CXX_FLAGS_RELEASE "/MT")
    else()
      set(CMAKE_CXX_FLAGS_RELEASE "/MD")
    endif()

    add_definitions(-D_WIN32)
elseif(ANDROID)
    SET (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pipe -fPIC -pie -llog -pedantic -std=gnu++11 -O2 -W -Wl,--no-undefined -fopenmp -ldl --sysroot C:/Intel/ds/src/opencv/android-ndk-r15c/platforms/android-19/arch-arm")
    set (NDK_LIB_PATH C:/Intel/ds/src/opencv/android-ndk-r15c/platforms/android-19/arch-arm/usr/lib)
else()
    EXEC_PROGRAM(uname ARGS -p OUTPUT_VARIABLE CMAKE_SYSTEM_PROCCESSOR)
    message(STATUS "CMAKE_SYSTEM_PROCCESSOR=${CMAKE_SYSTEM_PROCCESSOR}")

    SET (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pipe -pedantic -std=gnu++11 -W -Wl,--no-undefined -fopenmp -ldl")
endif()

#option(BUILD_SHARED_LIBS "Build shared library" ON)
SET (BUILD_SHARED_LIBS ON)
set(CMAKE_CONFIGURATION_TYPES "Release" CACHE STRING INTERNAL FORCE )

#if(__D400_USE_LIBREALSENSE__)
SET (LIBRS_DIR "${CMAKE_CURRENT_SOURCE_DIR}/librealsense")
SET (LIBRS_INCLUDE_DIR ${LIBRS_DIR}/include)

message(STATUS "BUILD_SHARED_LIBS=${BUILD_SHARED_LIBS}")

if(BUILD_SHARED_LIBS)
    if(MSVC)
        SET (LIBRS_LIBRARY_DIR ${LIBRS_DIR}/lib/x64)
    elseif(ANDROID)
        SET (LIBRS_LIBRARY_DIR ${LIBRS_DIR}/lib/android/armeabi-v7a)
    else()
        if(${CMAKE_SYSTEM_PROCCESSOR} MATCHES "aarch64|AARCH64")
            SET (LIBRS_LIBRARY_DIR ${LIBRS_DIR}/lib/linux/aarch64)
        else()
            SET (LIBRS_LIBRARY_DIR ${LIBRS_DIR}/lib/linux/x86_64)
        endif()
    endif()
else()
    if(MSVC)
        SET (LIBRS_LIBRARY_DIR ${LIBRS_DIR}/lib/static/x64)
    elseif(ANDROID)
        SET (LIBRS_LIBRARY_DIR ${LIBRS_DIR}/lib/android/armeabi-v7a)
    else()
        if(${CMAKE_SYSTEM_PROCCESSOR} MATCHES "aarch64|AARCH64")
            SET (LIBRS_LIBRARY_DIR ${LIBRS_DIR}/lib/static/linux/aarch64)
        else()
            SET (LIBRS_LIBRARY_DIR ${LIBRS_DIR}/lib/static/linux/x86_64)
        endif()
    endif()
endif()

SET (LIBRS_LIBS realsense2)
#endif()

set (DCAPI_INCLUDE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/Include")
set (DCAPI_LIBRARY_DIR "${CMAKE_CURRENT_SOURCE_DIR}/lib")

if(MSVC)
else()
#FIND_PACKAGE (zlib)
#FIND_PACKAGE (libpng)
#FIND_PACKAGE (ittnotify)
set (OTHER_LIBS gomp dl z ${CMAKE_DL_LIBS})
endif()

message(STATUS "LIBRS_INCLUDE_DIR=${LIBRS_INCLUDE_DIR}")
message(STATUS "LIBRS_LIBRARY_DIR=${LIBRS_LIBRARY_DIR}")
message(STATUS "DCAPI_INCLUDE_DIR=${DCAPI_INCLUDE_DIR}")
message(STATUS "DCAPI_LIBRARY_DIR=${DCAPI_LIBRARY_DIR}")

#add_subdirectory(rs2-crw)
#add_subdirectory(DSDynamicCalibrationAPI)
add_subdirectory(examples)

set(default_build_type "Release")

