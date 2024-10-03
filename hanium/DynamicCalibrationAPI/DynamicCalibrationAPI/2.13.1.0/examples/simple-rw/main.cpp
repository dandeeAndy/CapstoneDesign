/*
**********************************************************************************************************
*                                                                                                       **
* INTEL CONFIDENTIAL                                                                                    **
* Copyright (2018 - 2020) Intel Corporation.                                                            **
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
#include <memory> // for std::shared_ptr

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
// This example demos usage of the raw calibration data read/write interfaces which is part of Dynamic Calibration API
//

void check_error(rs2_error* e)
{
    if (e)
    {
        printf("rs_error was raised when calling %s(%s):\n", rs2_get_failed_function(e), rs2_get_failed_args(e));
        printf("    %s\n", rs2_get_error_message(e));
    }
}

int main(int argc, char * argv[])
{
    rs2_error* e = 0;

    // Create a context object. This object owns the handles to all connected realsense devices.
    rs2::context *ctx = new rs2::context();

    /* Get a list of all the connected devices. */
    auto devices = ctx->query_devices();

    int dev_count = devices.size();
    printf("There are %d connected RealSense devices.\n", dev_count);
    if (0 == dev_count)
        return 1;

    // Get the first connected device
    // The returned object should be released with rs2_delete_device(...)
    rs2::device dev = devices[0];

    // Check if Advanced-Mode is enabled
    if (dev.is<rs400::advanced_mode>())
    {
        rs400::advanced_mode advanced = dev.as<rs400::advanced_mode>();
        if (!advanced.is_enabled())
        {
            advanced.toggle_advanced_mode(true);
        }
    }

    cout << "  Device PID: " << dev.get_info(RS2_CAMERA_INFO_PRODUCT_ID) << endl;
    cout << "  Device name: " << dev.get_info(RS2_CAMERA_INFO_NAME) << endl;
    cout << "  Serial number: " << dev.get_info(RS2_CAMERA_INFO_SERIAL_NUMBER) << endl;
    cout << "  Firmware version: " << dev.get_info(RS2_CAMERA_INFO_FIRMWARE_VERSION) << endl;
    cout << endl;

    // initialize the Dynamic Calibration API in custom calibration mode
    DynamicCalibrationAPI::DSDynamicCalibration *m_dcApi = new DSDynamicCalibration();

    // dev should be a pointer to rs2::device from librealsense
    int ret = m_dcApi->Initialize(&dev, DynamicCalibrationAPI::DSDynamicCalibration::CAL_MODE_USER_CUSTOM);
    if (ret != DC_SUCCESS)
    {
        delete m_dcApi;
        delete ctx;
        return DC_ERROR_FAIL;
    }

    int status = DC_SUCCESS;

    DS5CoefficientsParamsTable tableCoff = { 0xFF };
    uint8_t* table = (uint8_t*)&tableCoff;

    // read the coefficient calibration table data back from the device
    cout << endl << "Reading data back from device ..." << endl;
    ret = m_dcApi->ReadCalibrationRawData(table, DynamicCalibrationAPI::DSDynamicCalibration::CAL_TABLE_COEFF);

    if (ret == DC_SUCCESS)
    {
        dump_to_console(table, sizeof(DS5CoefficientsParamsTable));
        status = 0;
    }
    else
    {
        cout << "Failed to read data (error: " << ret << ")" << endl;
        status = 1;
    }


    // Th following code showcases how to write raw calibration data back to device
    // cout << "Writing to device ..." << endl;

    // ret = m_dcApi->WriteCalibrationRawData((uint8_t*) &coeffTable, DynamicCalibrationAPI::DSDynamicCalibration::CAL_TABLE_COEFF);

    // if (ret == DC_SUCCESS)
    // {
    //     cout << "data successfully write to device " << endl;
    //     status = DC_SUCCESS;
    // }
    // else
    // {
    //     cout << "Failed to write data to device: error " << ret << endl;
    //     status = ret;
    // }

    delete m_dcApi;
    delete ctx;

    return 0;
}
