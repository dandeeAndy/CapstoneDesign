
# Set minimum required CMake version
cmake_minimum_required(VERSION 3.1.0)

# Name the project
project (simple-rw)

link_directories(${DCAPI_LIBRARY_DIR} ${LIBRS_LIBRARY_DIR})

# Source files
    set(SIMPLE_RW_CPP
            main.cpp
            ../Common/Rs400DeviceSimple.cpp
        )

# Add the sources to the target
add_executable(${PROJECT_NAME} ${SIMPLE_RW_CPP})
set_target_properties(${PROJECT_NAME} PROPERTIES OUTPUT_NAME "simplerw")

target_include_directories(${PROJECT_NAME} PUBLIC ${DCAPI_INCLUDE_DIR} ../Common ${LIBRS_INCLUDE_DIR})

if (MSVC)
target_link_libraries(${PROJECT_NAME} DSDynamicCalibrationAPI.DLL ${LIBRS_LIBS})
else()
target_link_libraries(${PROJECT_NAME} -lDSDynamicCalibrationAPI ${LIBRS_LIBS} ${CMAKE_DL_LIBS})
endif()
