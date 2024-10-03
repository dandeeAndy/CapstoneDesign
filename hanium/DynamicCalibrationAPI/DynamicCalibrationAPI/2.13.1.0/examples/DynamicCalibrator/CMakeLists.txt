
# Set minimum required CMake version
cmake_minimum_required(VERSION 3.1.0)

# Name the project
project (DynamicCalibrator)

# Source files
    set(RS_CALIBRATOR_CPP
        Main.cpp
        MainView.cpp
        CliView.cpp
        GuiView.cpp           
        RgbCalibration.cpp
        Scale.cpp
        ProcessDynCalibration.cpp
        CaptureManager.cpp 
        Gimbal.cpp
        ../Common/Rs400Device.cpp
        ../Common/rs_utils.cpp
	../../3rdparty/imgui/imgui.cpp
	../../3rdparty/imgui/imgui_draw.cpp
	../../3rdparty/imgui/imgui_impl_glut.cpp
        )
        
if(MSVC)
    set(RS_GIMBAL_CPP SerialPortImplWin.cpp)
else()
    set(RS_GIMBAL_CPP
        SerialPortImplLinux.cpp
        )
endif()

if (MSVC)
link_directories(${DCAPI_LIBRARY_DIR} ${LIBRS_LIBRARY_DIR} ../../3rdparty/glut/lib ../../3rdparty/zlib/lib)
else()
link_directories(${DCAPI_LIBRARY_DIR} ${LIBRS_LIBRARY_DIR})
endif()

# Add the sources to the target
add_executable(${PROJECT_NAME} ${RS_CALIBRATOR_CPP} ${RS_GIMBAL_CPP})
set_target_properties(${PROJECT_NAME} PROPERTIES OUTPUT_NAME "DynamicCalibrator")

target_include_directories(${PROJECT_NAME} PUBLIC ${DCAPI_INCLUDE_DIR} ${LIBRS_INCLUDE_DIR} ../Common ../../3rdparty/imgui ../../3rdparty/glut/include ../../3rdparty/zlib/include)

if (MSVC)
target_link_libraries(${PROJECT_NAME} DSDynamicCalibrationAPI.DLL ${LIBRS_LIBS} freeglut zlib)
else()
target_link_libraries(${PROJECT_NAME} -lDSDynamicCalibrationAPI ${LIBRS_LIBS} glut GL GLU ${CMAKE_DL_LIBS})
endif()


if(MSVC)
# copy the .dll file to the same folder as the executable
add_custom_command(
    TARGET ${PROJECT_NAME} POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_directory
    ${DCAPI_LIBRARY_DIR}
    $<TARGET_FILE_DIR:${PROJECT_NAME}>)

add_custom_command(
    TARGET ${PROJECT_NAME} POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_directory
    ${LIBRS_LIBRARY_DIR}
    $<TARGET_FILE_DIR:${PROJECT_NAME}>)

add_custom_command(
    TARGET ${PROJECT_NAME} POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_directory
    ${CMAKE_CURRENT_SOURCE_DIR}/../../3rdparty/glut/lib
    $<TARGET_FILE_DIR:${PROJECT_NAME}>)
endif()
