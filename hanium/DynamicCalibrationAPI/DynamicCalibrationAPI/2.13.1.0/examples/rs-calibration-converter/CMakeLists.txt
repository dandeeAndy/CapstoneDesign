
# Set minimum required CMake version
cmake_minimum_required(VERSION 3.1.0)

# Name the project
project (rs-calibration-converter)

link_directories(${DCAPI_LIBRARY_DIR} ${LIBRS_LIBRARY_DIR})

# Source files
    set(RS_CAL_CONVERTER_CPP
            rs-calibration-converter.cpp
            ../Common/rs_utils.cpp
)

# Add the sources to the target
add_executable(${PROJECT_NAME} ${RS_CAL_CONVERTER_CPP})
set_target_properties(${PROJECT_NAME} PROPERTIES OUTPUT_NAME "rs-calibration-converter")

target_include_directories(${PROJECT_NAME} PUBLIC ${DCAPI_INCLUDE_DIR} ../Common ${LIBRS_INCLUDE_DIR} ${SAFECLIB_INCLUDE_DIR})

if (MSVC)
target_link_libraries(${PROJECT_NAME} DSDynamicCalibrationAPI.LIB)
else()
target_link_libraries(${PROJECT_NAME} -lDSDynamicCalibrationAPI ${LIBRS_LIBS} ${CMAKE_DL_LIBS})
endif()
