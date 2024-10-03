
# Set minimum required CMake version
cmake_minimum_required(VERSION 3.1.0)

# Name the project
project (CustomRW)

link_directories(${DCAPI_LIBRARY_DIR} ${LIBRS_LIBRARY_DIR})

# Source files
    set(RS_CUSTOMRW_CPP
            Main.cpp
            ../Common/Rs400DeviceSimple.cpp
            ../Common/rs_utils.cpp
        )

# Add the sources to the target
add_executable(CustomRW ${RS_CUSTOMRW_CPP})
set_target_properties(CustomRW PROPERTIES OUTPUT_NAME "CustomRW")

target_include_directories(${PROJECT_NAME} PUBLIC ${DCAPI_INCLUDE_DIR} ../Common ${LIBRS_INCLUDE_DIR} ${SAFECLIB_INCLUDE_DIR})

if (MSVC)
target_link_libraries(${PROJECT_NAME} DSDynamicCalibrationAPI.DLL ${LIBRS_LIBS})
else()
target_link_libraries(${PROJECT_NAME} -lDSDynamicCalibrationAPI ${LIBRS_LIBS} ${CMAKE_DL_LIBS})
endif()
