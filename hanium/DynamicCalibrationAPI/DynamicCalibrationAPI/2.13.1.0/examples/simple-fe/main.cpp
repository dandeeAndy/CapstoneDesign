/*
**********************************************************************************************************
*                                                                                                       **
* INTEL CONFIDENTIAL                                                                                    **
* Copyright (2018 - 2022) Intel Corporation.                                                            **
* This software and the related documents are Intel copyrighted materials, and your use of them is      **
* governed by the express license under which they were provided to you ("License"). Unless the License **
* provides otherwise, you may not use, modify, copy, publish, distribute, disclose or transmit this     **
* software or the related documents without Intel's prior written permission.                           **
* This software and the related documents are provided as is, with no express or implied warranties,    **
* other than those that are expressly stated in the License.                                            **
*                                                                                                       **
**********************************************************************************************************
*/

#include <iomanip>
#include <iostream>
#include <fstream>
#include <string>
#include <cstring>
#include <thread>

#include "librealsense2/rs.hpp"
#include "librealsense2/rs_advanced_mode.hpp"

#include "DSDynamicCalibration.h"

using namespace std;
using namespace rs2;
using namespace DynamicCalibrationAPI; 


// example use only for print a buffer content to console
void dump_to_console(uint8_t* buffer, uint32_t size)
{
    // save original settings
    ios_base::fmtflags origFlags = cout.flags();
    streamsize         origPrec = cout.precision();
    char               origFill = cout.fill();

    cout << "buffer size: " << size << " bytes" << endl;
    cout << hex << std::uppercase;

    // print header
    cout << endl << "Offset (h)";

    for (int i = 0; i < 16; i++)
    {
        cout << " " << noshowbase << setw(2) << setfill('0') << (int)i;
    }

    cout << endl;

    for (int i = 0; i < 58; i++)
    {
        cout << "-";
    }

    uint16_t c = 0;
    uint16_t more = size;

    // print the buffer content in hex, byte by byte, 16 bytes per line
    while (more)
    {
        uint16_t offset = c - c % 16;

        if (c % 16 == 0)
        {
            cout << endl << setw(6) << setfill('0') << (int)offset << " ==>";
        }

        cout << " " << noshowbase << setw(2) << setfill('0') << (int)buffer[c];

        c++;
        more--;
    }

    cout << endl << endl;

    // restore original settings
    cout.flags(origFlags);
    cout.precision(origPrec);
    cout.fill(origFill);
}

//
// New D430 + Tracking Module devices include fisheye but its not calibrated, so user will need to calibrate the fisheye before
// using it. A custom calibration r/w interface is provided to write/read user fisheye calibration data to the device
//
// This example demos usage of the Fisheye custom calibration data read/write interfaces which is part of Dynamic Calibration API
//

int main(int argc, char * argv[]) try
{
    cout << "simple fisheye custom data r/w sample for Intel RealSense D400, Version: " << DS_DYNAMIC_CALIBRATION_VERSION << endl << endl;

    // rs context
    rs2::context *ctx = new context();

    // query devices on host
    auto devices = ctx->query_devices();

    if (devices.size() == 0)
    {
        std::cout << "No Intel RealSense device connected." << std::endl;
        if(ctx) delete ctx;
        return 0;
    }

    // only the first device got picked, so connect only one device when try this example
    // for supporting multiple devices, please refer to the CustomRW example 
    rs2::device mydev = devices[0];

    // to use the custom calibration read/write api, the device should be in advanced mode
    if (mydev.is<rs400::advanced_mode>())
    {
        rs400::advanced_mode advanced = mydev.as<rs400::advanced_mode>();
        if (!advanced.is_enabled())
        {
            advanced.toggle_advanced_mode(true);
        }
    }

    // print a few basic information about the device
    cout << "  Device PID: " << mydev.get_info(RS2_CAMERA_INFO_PRODUCT_ID) << endl;
    cout << "  Device name: " << mydev.get_info(RS2_CAMERA_INFO_NAME) << endl;
    cout << "  Serial number: " << mydev.get_info(RS2_CAMERA_INFO_SERIAL_NUMBER) << endl;
    cout << "  Firmware version: " << mydev.get_info(RS2_CAMERA_INFO_FIRMWARE_VERSION) << endl;
    cout << endl;


    // initialize the Dynamic Calibration API in custom calibration mode
    DynamicCalibrationAPI::DSDynamicCalibration *m_dcApi = new DSDynamicCalibration();

    // mydev should be a pointer to rs2::device from librealsense
    int ret = m_dcApi->Initialize(&mydev, DynamicCalibrationAPI::DSDynamicCalibration::CAL_MODE_USER_CUSTOM);
    if (ret != DC_SUCCESS)
    {
        if (m_dcApi) delete m_dcApi;
        if (ctx) delete ctx;
        return DC_ERROR_FAIL;
    }

    int status = DC_SUCCESS;
    uint8_t feCustom[DC_MM_FE_CUSTOM_DATA_SIZE];

    // the custom data area has DC_MM_FE_CUSTOM_DATA_SIZE (136 bytes) of storage space. User can 
    // define their data own format and write to the device and retrieve it later from
    // the device

    // on a new device, the storage is not initialzed, so should write data before perform
    // read. reading before writing any data will fail.

    memset((void*)&feCustom, 0xFF, sizeof(feCustom));

    // writing some random numbers just for example
    feCustom[20] = 0xA;
    feCustom[106] = 0x3;

    // Workaround for writing failing issue on Linux: wait for a few seconds before writing
    cout << "Writing to device ..." << endl;
    std::this_thread::sleep_for(std::chrono::milliseconds(5000));

    ret = m_dcApi->WriteFECustomData((uint8_t*) &feCustom);

    if (ret == DC_SUCCESS)
    {
        cout << "fisheye custom data successfully write to device " << endl;
        status = EXIT_SUCCESS;
    }
    else
    {
        cout << "Failed to write fisheye custom data to device: error " << ret << endl;
        status = EXIT_FAILURE;
    }

    // read the custom data back from the device
    cout << endl << "Reading data back from device ..." << endl;
    ret = m_dcApi->ReadFECustomData(feCustom);

    if (ret == DC_SUCCESS)
    {
        dump_to_console(feCustom, sizeof(feCustom));
        status = EXIT_SUCCESS;
    }
    else
    {
        cout << "Failed to read motion module custom data." << endl;
        status = EXIT_FAILURE;
    }

    if (m_dcApi) delete m_dcApi;
    if(ctx) delete ctx;

    return status;
}
catch (const rs2::error & e)
{
    std::cerr << "error calling " << e.get_failed_function() << "(" << e.get_failed_args() << "):\n    " << e.what() << std::endl;
    return EXIT_FAILURE;
}
catch (const std::exception& e)
{
    std::cerr << e.what() << std::endl;
    return EXIT_FAILURE;
}
