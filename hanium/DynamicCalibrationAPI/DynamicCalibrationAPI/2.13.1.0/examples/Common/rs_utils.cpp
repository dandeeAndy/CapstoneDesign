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

#include <iostream>
#include <string.h>

#include <iomanip>
#include <iostream>
#include <fstream>
#include <string>
#include <cstring>

#include "rs_utils.h"
#include "DSShared.h"

using namespace std;


string dump_buffer_to_console(uint8_t* buffer, uint32_t size)
{
        std::ostringstream ss;

	// save original settings
	ios_base::fmtflags origFlags = ss.flags();
	streamsize         origPrec = ss.precision();
	char               origFill = ss.fill();

	ss << "buffer size: " << size << " bytes" << endl;
	ss << hex << std::uppercase;

    // print header
	ss << endl << "Offset (h)";

	for (int i = 0; i < 16; i++)
	{
	    ss << " " << noshowbase << setw(2) << setfill('0') << (int) i;
	}

	ss << endl;

	for (int i = 0; i < 58; i++)
	{
		ss << "-";
	}

    uint16_t c = 0;
    uint16_t more = size;

    // print the buffer content in hex, byte by byte, 16 bytes per line
	while (more)
	{
		uint16_t offset = c - c % 16;

		if ( c % 16 == 0)
		{
			ss << endl << setw(6) << setfill('0') << (int) offset << " ==>";
		}

		ss << " " << noshowbase << setw(2) << setfill('0') << (int) buffer[c];

		c++;
		more--;
	}

	ss << endl << endl;

	// restore original settings
	ss.flags(origFlags);
	ss.precision(origPrec);
	ss.fill(origFill);

        return ss.str();
}



string rs_convert_err_to_string(int errCode)
{
	std::string error_msg = "Error (";
	stringstream stream;

	error_msg += to_string(errCode);
	error_msg += "): ";

	switch (errCode)
	{
	case DC_ERROR_FW_VERSION_OLD:
		error_msg += "Firmware on device is outdated.";
		break;

	case DC_ERROR_TIME_OUT:
		error_msg += "calibration has been cancelled due to timeout! \n";
		error_msg += "If you prefer, try longer timeout in seconds using the -o option ";
		error_msg += "on the command line or the advanced settings in GUI.\n";
		error_msg += "It's likely the device is severely shifted and hard for dynamic calibrator to recover. \n";
		error_msg += "Please try latest technician calibration tool.";
		break;

	case DC_ERROR_CAMERA_NOT_PLUGGED:
		error_msg = "no device detected, please connect camera to calibrate.";
		break;

	case DC_ERROR_GIMBAL_NOT_START:
		error_msg += "unable to start Gimbal";
		break;

	case DC_ERROR_TABLE_WRITE_FAILED:
		error_msg += "calibration table update failed.\n";
		break;

	case DC_ERROR_SET_INTERMEDIATE_CALIB_TABLE:
		error_msg += "intermediate calibration table update failed.\n";
		break;

	case DC_ERROR_RECTIFICATION_PHASE:
		error_msg += "rectification phase was not completed properly. Can't continue to scale phase.\n";
		break;

	case DC_ERROR_SCALE_PHASE_START_FAILED:
		error_msg += "failed to start scale phase.\n";
		break;

	case DC_ERROR_WRONG_PHASE:
		error_msg += "wrong phase, expect scale phase.\n";
		break;

	case DC_ERROR_GET_TARGETED_CALIBRATION_CORRECTION:
		error_msg += "GetTargetedCalibrationCorrection failed. Calibration on device not changed.\n";
		break;

	case DC_ERROR_RESOLUTION_NOT_SUPPORTED_V2:
		error_msg += "calibration coefficient table does not support maximum resolution mode.";
		error_msg += "\nPlease use 1280x720 resolution instead and try again.\n";
		break;

	case DC_ERROR_TABLE_NOT_VALID_RESOLUTION:
		error_msg += "image resolution in calibration table on device is invalid.\n";
		error_msg += "Please re-calibrate the device with latest OEM ";
		error_msg += "Calibration Tool and try again.\n";
		break;

	case DC_ERROR_TABLE_NOT_SUPPORTED:
		error_msg += "calibration tables on device are not supported, ";
		error_msg += "Please try again with latest Dynamic Calibrator software. \n";
		error_msg += "If you are already using latest software, please re-calibrate the device ";
		error_msg += "with latest OEM Calibration tools and try again.\n";
		break;

	case DC_ERROR_TABLE_NOT_VALID_COEFF:
		error_msg += "coefficient calibration table (0x19) on device is not valid, the device may be corrupted.";
		error_msg += "Please check the device and use CustomRW tool to restore to factory gold settings and try again.\n";
		break;

	case DC_ERROR_TABLE_NOT_VALID_DEPTH:
		error_msg += "depth calibration table (0x1f) on device is not valid, the device may be corrupted.";
		error_msg += "Please check the device and use CustomRW tool to restore to factory gold settings and try again.\n";
		break;

	case DC_ERROR_TABLE_NOT_VALID_RGB:
		error_msg += "rgb calibration table (0x20) on device is not valid, the device may be corrupted.";
		error_msg += "Please check the device and use CustomRW tool to restore to factory gold settings and try again.\n";
		break;

	case DC_ERROR_TABLE_READ_FAILED_COEFF:
		error_msg += "failed to read coefficient calibration table (0x19) from device.";
		error_msg += "Please check the device and use CustomRW tool to restore to factory gold settings and try again.\n";
		break;

	case DC_ERROR_TABLE_READ_FAILED_DEPTH:
		error_msg += "failed to read depth calibration table (0x1f) from device.";
		error_msg += "Please check the device and use CustomRW tool to restore to factory gold settings and try again.\n";
		break;

	case DC_ERROR_TABLE_READ_FAILED_RGB:
		error_msg += "failed to read rgb calibration table (0x20) from device.";
		error_msg += "Please check the device and use CustomRW tool to restore to factory gold settings and try again.\n";
		break;

	case DC_ERROR_DEVICE_TIMEOUT:
		error_msg += "no frames received from device for 5 seconds, timed out. A common cause is loose USB connection. Please check the device and try again.";
		break;

	case DC_ERROR_RGB_NOT_SUPPORTED_ON_DEVICE:
		error_msg += "no rgb is detected on device. Please check hardware and firmware and make sure rgb is enabled before running calibration.";
		break;

	case DC_ERROR_CUSTOM_INVALID_CAL_TABLE:
		error_msg += "one or more of the calibration tables are not valid.";
		break;

	case DC_ERROR_CUSTOM_INVALID_PARAMS:
		error_msg += "one or more of the output variables are not valid.";
		break;

	case DC_ERROR_CUSTOM_INVALID_LEFTRIGHT_RESOLUTION:
		error_msg += "left and right camera resolution is not supported.";
		break;

	case DC_ERROR_CUSTOM_LEFT_INTRINSICS_UNREASONABLE:
		error_msg += "left camera intrinsics unreasonable.";
		break;

	case DC_ERROR_CUSTOM_RIGHT_INTRINSICS_UNREASONABLE:
		error_msg += "right camera intrinsics unreasonable.";
		break;

    case DC_ERROR_DEVICE_USB2:
        error_msg += "The selected camera is currently running in USB2 mode. Intel RealSense Dynamic Calibrator only supports USB3 devices. Please check the camera and make sure it's plugged into a USB3 port or hub. If no obvious issue is found with the connection, please disconnect, reconnect the camera and try again.";
        break;

	case DC_ERROR_INVALID_RGB_CALIBRATION_RESOLUTION:
		error_msg += "RGB calibration resolution width or height is zero or not valid.";
		break;

    case DC_ERROR_SET_STREAMING_MEDIA_MODE_FAILED:
        error_msg += "Streaming profile is not supported or configuration failed.";
        break;

	default:
		error_msg += "Unknown";
		break;
	}

	if (errCode >= DC_ERROR_TABLE_NOT_SUPPORTED && errCode <= DC_ERROR_TABLE_READ_FAILED_RGB)
	{
		error_msg += "check CustomRW tool.\n";
	}

	return error_msg;
}