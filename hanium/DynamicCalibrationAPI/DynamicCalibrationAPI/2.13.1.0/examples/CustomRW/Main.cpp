/*
**********************************************************************************************************
*                                                                                                       **
* INTEL CONFIDENTIAL                                                                                    **
* Copyright (2018 - 2022) Intel Corporation.                                                            **
* This software and the related documents are Intel copyrighted materials, and your use of them is      **
* governed by the express license under which they were provided to you("License").Unless the License   **
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

#ifndef _WIN32
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#endif

#include "librealsense2/rs.hpp"
#include "librealsense2/rs_advanced_mode.hpp"
#include "DSDynamicCalibration.h"
#include "DSCalData.h"

#include "CalibParamXmlWrite.h"
#include "CommandLine.h"

#include "Rs400DeviceSimple.h"
#include "rs_utils.h"

using namespace std;
using namespace devicewrapper;

using namespace DynamicCalibrationAPI;
using namespace CalibParamXmlWrite;

//
// This example demos usage of the calibration parameter read/write APIs for calibration with user custom algo
//
// In most cases, users will use the Dynamic Calibration API and its embeded Intel algorithm
// to calibrate the D400 series devices. Some advanced users may prefer to developer their
// own custom calibration algorithm to fit their specific needs. The calibration parameter
// read/write APIs can be used to meet this custom calibration usage.
//
// In those custom calibration use cases, the user is responsible to come up the correct calibration
// parameters with their own algorithm, and two APIs are available to write and read back those
// high level calibration paramaters to/from the device. Dynamic Calibration API will handle internal
// calibration data formats and device operations.
//
// WriteCustomCalibrationParameters
// ReadCalibrationParameters
//
// The ReadCalibrationParameters can be used to read back paramters from D400 series devices in all cases,
// including calibration with Intel algorithm and user custom algorithm.
//


struct Options
{
	bool bShowHelp{ false };
	bool bShowCameraList{ false };

	bool bShowVer{ false };
	string deviceSN{};

	bool bResetToGold{ false };
	bool bRead{ false };
	bool bWrite{ false };

	bool bRaw{ false };
	string tableType{};

	bool bFile{ false };
	string dumpFile{};

	bool bFeCustom{ false };
	bool bForceRgb{ false };
	bool bExtra{ false };

	bool ParseCmdOptions(int argc, char * argv[], string& HelpMessage)
	{
		// Parse command line options
		CommandLine cl(argc, argv);

		cl.addOption(bShowHelp, "--help", "-?", "display list of command line options");
		cl.addOption(bShowCameraList, "--list", "-l", "display list of connected cameras");

		cl.addOption(bShowVer, "--version", "-v", "show dynamic calibration version info");
		cl.addOption(deviceSN, "device serial number", "--sn", "-sn", "if multiple cameras connected to the current system, choose one of the cameras to modify by specifying its serial number");

		cl.addOption(bResetToGold, "--reset-to-gold", "-g", "Reset calibration on device to default gold factory settings");
		cl.addOption(bRead, "--read", "-r", "Read calibration data");
		cl.addOption(bWrite, "--write", "-w", "Write calibration data");

		cl.addOption(tableType, "19, 1f, 20, or ff", "-raw", "-raw", "dump calibration table raw binary content");
		cl.addOption(dumpFile, "file name", "--file", "-f", "use the specified file for calibration data input or output");

		cl.addOption(bFeCustom, "", "-fe", "fisheye custom data (limited, available ONLY on selected device SKU)");

		cl.addOption(bForceRgb, "--force-rgb", "-rgb", "force read/write rgb calibration data even if device does not have rgb sensor (for 3rd party rgb custom calibration)");
		cl.addOption(bExtra, "--extra", "-ex", "print extra calibration information to console");

		int invalidoptions = cl.checkAllArgsUsed();

		if (!tableType.empty())
		{
			bRaw = true;
		}

		if (!dumpFile.empty())
		{
			bFile = true;
		}

		HelpMessage = cl.getHelpMessage();

		// -1: error, 0: success
		return (invalidoptions == -1 || cl.numArgs() == 0) ? false : true;
	}
};


void DisplayCameraList(Rs400DeviceSimple dev)
{
    std::vector<camera_info> cameras = dev.ListCameras();
    size_t device_count = cameras.size();
    if (!device_count)
    {
        cout << "No device detected. Is it plugged in?" << endl;
        return;
    }

    cout << left << setw(40) << "Device Name"
         << setw(15) << "Serial Number"
         << setw(20) << "Firmware Version"
         << setw(10) << "Type"
         << setw(40) << "PHYSICAL PORT"
         << endl;

    for (int i = 0; i < (int)device_count; ++i)
    {
        cout << left << setw(40) << cameras[i].name
             << setw(15) << cameras[i].serial
             << setw(20) << cameras[i].fw_ver
             << setw(10) << cameras[i].usb_type
	     << setw(40) << cameras[i].physical_port
             << endl;
    }
}

void ShowUsageExamples(char * execmd)
{
	cout << endl;
	cout << "Usages:" << endl;
	cout << "Example #1: reset device calibration to gold settings" << endl;
	cout << "    " << execmd << " -g" << endl;
	cout << endl;
	cout << "Example #2: read device calibration and display to terminal in xml format" << endl;
	cout << "    " << execmd << " -r" << endl;
	cout << endl;
	cout << "Example #3: read device calibration into a text file in xml format" << endl;
	cout << "    " << execmd << " -r -f mydevice.xml" << endl;
	cout << endl;
	cout << "Example #4: write custom calibration from a text file in xml format into the device" << endl;
	cout << "    " << execmd << " -w -f mycustomdata.xml" << endl;
	cout << endl;
	cout << "Example #5: read raw calibration table from device and display to the terminal, supported table id 19, 1F, and 20, for example," << endl;
	cout << "    " << execmd << " -r -raw 19" << endl;
	cout << endl;
	cout << "Example #6: read raw calibration table from device and save into a binary file, supported table id 19, 1F, and 20, for example," << endl;
	cout << "    " << execmd << " -r -raw 19 -f mytable-19.bin" << endl;
	cout << endl;
	cout << "Example #7: write raw calibration table from binary file into the device, supported table id 19, 1F, and 20, for example," << endl;
	cout << "    " << execmd << " -w -raw 19 -f mytable-19.bin" << endl;
	cout << endl;
	cout << "Example #8: read custom fisheye data from device and display to the terminal" << endl;
	cout << "    " << execmd << " -r -fe" << endl;
	cout << endl;
	cout << "Example #9: read custom fisheye data from device and save into a binary file" << endl;
	cout << "    " << execmd << " -r -fe -f myfe.bin" << endl;
	cout << endl;
	cout << "Example #10: write custom fisheye data from binary file into the device" << endl;
	cout << "    " << execmd << " -w -fe -f myfe.bin" << endl;
	cout << endl;
	cout << "Example #11: read calibration data from device and print extra calibration information" << endl;
	cout << "    " << execmd << " -r -ex" << endl;

	cout << endl;
}

void print_intrinsics(DC_Intrinsics intrinsics)
{
	cout << "width: " << intrinsics.width << endl;
	cout << "height: " << intrinsics.height << endl;
	cout << "principal point ppx: " << intrinsics.ppx << endl;
	cout << "principal point ppy: " << intrinsics.ppy << endl;
	cout << "focal length fx: " << intrinsics.fx << endl;
	cout << "focal length fy: " << intrinsics.fy << endl;
	cout << "distortion coefficients: " << setprecision(10) << intrinsics.coeffs[0] << " " << intrinsics.coeffs[1] << " " << intrinsics.coeffs[2] << " " << intrinsics.coeffs[3] << " " << intrinsics.coeffs[4] << " " << endl;
	cout << "distortion model: BROWN CONRADY" << endl;
}

int main(int argc, char * argv[]) try
{
	DSDynamicCalibration::CalibrationTableType tabletype = DSDynamicCalibration::CAL_TABLE_COEFF;

	cout << "CustomRW for Intel RealSense D400, Version: " << DS_DYNAMIC_CALIBRATION_VERSION << endl << endl;

	Options CmdLineOptions;
	string HelpMessage;

	bool optionsOK = CmdLineOptions.ParseCmdOptions(argc, argv, HelpMessage);

	if (!optionsOK || CmdLineOptions.bShowHelp)
	{
		cout << HelpMessage << endl;
		ShowUsageExamples(argv[0]);
		return optionsOK ? EXIT_SUCCESS : EXIT_FAILURE;
	}

	if (CmdLineOptions.bShowVer)
	{
		cout << DS_DYNAMIC_CALIBRATION_VERSION << endl;
		return EXIT_SUCCESS;
	}

	Rs400DeviceSimple g_rsDevice;

        if (CmdLineOptions.bShowCameraList)
        {
            DisplayCameraList(g_rsDevice);
            return EXIT_SUCCESS;
        }

	if (CmdLineOptions.bWrite)
	{
	    if (!CmdLineOptions.dumpFile.empty())
	    {
            if (!file_exist(CmdLineOptions.dumpFile.c_str()))
            {
                cout << "Error: cannot find input file " << CmdLineOptions.dumpFile << endl;
                return EXIT_FAILURE;
            }
        }
        else
        {
            cout << "Error: no input file is provided to write." << endl;
            return EXIT_FAILURE;
        }
    }

	if (CmdLineOptions.bRaw)
	{
		if (CmdLineOptions.tableType.compare("19") == 0)
		{
			tabletype = DSDynamicCalibration::CAL_TABLE_COEFF;
		}
		else if (CmdLineOptions.tableType.compare("1f") == 0 || CmdLineOptions.tableType.compare("1F") == 0)
		{
			tabletype = DSDynamicCalibration::CAL_TABLE_DEPTH;
		}
		else if (CmdLineOptions.tableType.compare("20") == 0)
		{
			tabletype = DSDynamicCalibration::CAL_TABLE_RGB;
		}
		else if (CmdLineOptions.tableType.compare("ff") == 0 || CmdLineOptions.tableType.compare("FF") == 0)
		{
			tabletype = DSDynamicCalibration::CAL_TABLE_ALL;
		}
		else
		{
			cout << "Error: invalid calibration table type specified: " << CmdLineOptions.tableType << endl;
			cout << "Please choose from the following:" << endl;
			cout << " 19 for calibration coefficient table" << endl;
			cout << " 1f for depth table" << endl;
			cout << " 20 for RGB table" << endl;
			cout << " ff for Vision Calibration Table" << endl;

			return EXIT_FAILURE;
		}
	}


	try
	{
		if (!g_rsDevice.InitializeCamera(CmdLineOptions.deviceSN))
		{
			cout << "Error: cannot find or open device with serial number " << CmdLineOptions.deviceSN << endl;

			return EXIT_FAILURE;
		}
	}
	catch (...)
	{
		cout << "Error: cannot find or open device with serial number " << CmdLineOptions.deviceSN << endl;
		return EXIT_FAILURE;
	}

	camera_info info = g_rsDevice.Get_Active_CameraInfo();

	cout << "  Device PID: " << info.pid << endl;
	cout << "  Device name: " << info.name << endl;
	cout << "  Serial number: " << info.serial << endl;
	cout << "  Firmware version: " << info.fw_ver << endl;
    cout << "  Type: " << info.usb_type << endl;
	cout << "  Physical port: " << info.physical_port << endl;
	cout << endl;

    // handle to realsense rs2::device
    void *g_pDevice = g_rsDevice.GetDeviceHandle();

    if (g_pDevice == NULL)
    {
        cout << "Error: invalid realsense rs2::device handle" << endl;
        return EXIT_FAILURE;
    }

    if (g_rsDevice.supports_rgb_on_left())
    {
        CmdLineOptions.bForceRgb = true;
    }

	int ret = DC_SUCCESS;

	// Initialize Dynamic Calibration API to custom calibration mode
	DynamicCalibrationAPI::DSDynamicCalibration *m_dcApi = new DSDynamicCalibration();

	if (CmdLineOptions.bForceRgb)
	{
		ret = m_dcApi->Initialize(g_pDevice, DynamicCalibrationAPI::DSDynamicCalibration::CAL_MODE_USER_CUSTOM, -1);
	}
	else
	{
		ret = m_dcApi->Initialize(g_pDevice, DynamicCalibrationAPI::DSDynamicCalibration::CAL_MODE_USER_CUSTOM);
	}

	if (ret != DC_SUCCESS)
	{
		cout << rs_convert_err_to_string(ret) << endl;
		return DC_ERROR_FAIL;
	}

	int status = DC_SUCCESS;

	if (CmdLineOptions.bResetToGold)
	{
		ret = m_dcApi->ResetDeviceCalibration();

		if (ret == DC_SUCCESS)
		{
			cout << "Calibration on device successfully reset to default gold factory settings." << endl;
			status = EXIT_SUCCESS;
		}
		else
		{
			cout << "Calibration failed to restore to default." << endl;
			status = EXIT_FAILURE;
		}

		if(m_dcApi) delete m_dcApi;
		return status;
	}


	if (CmdLineOptions.bFeCustom)
	{
		uint8_t feCustom[DC_MM_FE_CUSTOM_DATA_SIZE];

		if (CmdLineOptions.bRead)
		{
			ret = m_dcApi->ReadFECustomData(feCustom);

			if (ret == DC_SUCCESS)
			{
				if (!CmdLineOptions.dumpFile.empty())
				{
					ofstream myFile(CmdLineOptions.dumpFile, ios::out | ios::binary);
					myFile.write((const char*)feCustom, sizeof(feCustom));
					myFile.close();

					cout << "fe custom data on device successfully read into file " << CmdLineOptions.dumpFile << endl;
				}
				else
				{
					cout << dump_buffer_to_console(feCustom, sizeof(feCustom));
				}

				status = EXIT_SUCCESS;
			}
			else
			{
				cout << "Failed to read fisheye custom data." << endl;
				status = EXIT_FAILURE;
			}

			if (m_dcApi) delete m_dcApi;
			return status;
		}
		else if (CmdLineOptions.bWrite && !CmdLineOptions.dumpFile.empty())
		{
			ifstream myFile(CmdLineOptions.dumpFile, ios::out | ios::binary);
			myFile.read((char*)feCustom, sizeof(feCustom));
			myFile.close();

            // Workaround for writing failing issue on Linux: wait for a few seconds before writing
            std::this_thread::sleep_for(std::chrono::milliseconds(5000));

			ret = m_dcApi->WriteFECustomData(feCustom);

			if (ret == DC_SUCCESS)
			{
				cout << "fe custom data successfully write to device " << endl;
				status = EXIT_SUCCESS;
			}
			else
			{
				cout << "Failed to write fe custom data to device." << endl;
				status = EXIT_FAILURE;
			}

			if (m_dcApi) delete m_dcApi;
			return status;
		}
		else
		{
			cout << "fe other cases" << endl;

			if (m_dcApi) delete m_dcApi;
			return status;
		}

	}

	if (CmdLineOptions.bRaw)
	{
		uint8_t* table = NULL;
		int tablesize = 0;

		DS5CoefficientsParamsTable tableCoff = { 0xFF };
		DS5DepthCalibrationParamsTable tableDepth = { 0xFF };
		DS5RgbCalibrationParamsTable tableRgb = { 0xFF };

		switch (tabletype)
		{
		case DSDynamicCalibration::CAL_TABLE_COEFF:
			tablesize = sizeof(DS5CoefficientsParamsTable);
			break;

		case DSDynamicCalibration::CAL_TABLE_DEPTH:
			tablesize = sizeof(DS5DepthCalibrationParamsTable);
			break;

		case DSDynamicCalibration::CAL_TABLE_RGB:
			tablesize = sizeof(DS5RgbCalibrationParamsTable);
			break;

		case DSDynamicCalibration::CAL_TABLE_ALL:
			tablesize = 1024;
			break;
		}

		table = (uint8_t*) malloc(tablesize);
		memset(table, 0, tablesize);

		if (CmdLineOptions.bRead)
		{
			ret = m_dcApi->ReadCalibrationRawData(table, tabletype);

			if (ret == DC_SUCCESS)
			{
				if (!CmdLineOptions.dumpFile.empty())
				{
					ofstream myFile(CmdLineOptions.dumpFile, ios::out | ios::binary);
					myFile.write((const char*)table, tablesize);
					myFile.close();
					cout << "calibration on device successfully read into file " << CmdLineOptions.dumpFile << endl;
				}
				else
				{
					cout << dump_buffer_to_console(table, tablesize);
				}

				status = EXIT_SUCCESS;
			}
			else
			{
				cout << rs_convert_err_to_string(ret) << endl;
				status = EXIT_FAILURE;
			}

			if (m_dcApi) delete m_dcApi;
			return status;
		}
		else if (CmdLineOptions.bWrite && !CmdLineOptions.dumpFile.empty())
		{
			ifstream myFile(CmdLineOptions.dumpFile, ios::out | ios::binary);
			myFile.read((char*)table, tablesize);
			myFile.close();

			ret = m_dcApi->WriteCalibrationRawData(table, tabletype);

			if (ret == DC_SUCCESS)
			{
				cout << "calibration successfully written to device " << endl;
				status = EXIT_SUCCESS;
			}
			else
			{
				cout << "Failed to write calibration data to device." << endl;
				status = EXIT_FAILURE;
			}

			if (m_dcApi) delete m_dcApi;
			return status;
		}
		else
		{
			cout << "Either -r or -w option should be provided to read/write raw calibration table data" << endl;
		}

		free(table);
	}
	else
	{


		//
		// The expected calibration parameters for D400 series devices are defined as following:
		//   resolutionLeftRight: The resolution of the left and right camera, specified as[width; height]
		//   focalLengthLeft : The focal length of the left camera, specified as[fx; fy] in pixels
		//   principalPointLeft : The principal point of the left camera, specified as[px; py] in pixels
		//   distortionLeft : The distortion of the left camera, specified as Brown's distortion model [k1; k2; p1; p2; k3]
		//
		//   focalLengthRight : The focal length of the right camera, specified as[fx; fy] in pixels
		//   principalPointRight : The principal point of the right camera, specified as[px; py] in pixels
		//   distortionRight : The distortion of the right camera, specified as Brown's distortion model [k1; k2; p1; p2; k3]
		//   rotationLeftRight : The rotation from the right camera coordinate system to the left camera coordinate system, specified as a 3x3 rotation matrix
		//   translationLeftRight : The translation from the right camera coordinate system to the left camera coordinate system, specified as a 3x1 vector in milimeters
		//
		//   hasRGB : Whether RGB camera calibration parameters are supplied
		//   resolutionRGB : The resolution of the RGB camera, specified as[width; height]
		//   focalLengthRGB : The focal length of the RGB camera, specified as[fx; fy] in pixels
		//   principalPointRGB : The principal point of the RGB camera, specified as[px; py] in pixels
		//   distortionRGB : The distortion of the RGB camera, specified as Brown's distortion model [k1; k2; p1; p2; k3]
		//   rotationLeftRGB : The rotation from the RGB camera coordinate system to the left camera coordinate system, specified as a 3x3 rotation matrix
		//   translationLeftRGB : The translation from the RGB camera coordinate system to the left camera coordinate system, specified as a 3x1 vector in milimeters
		//
		bool hasRGB;
		int resolutionLeftRight[2], resolutionRGB[2];
		double focalLengthLeft[2], focalLengthRight[2], focalLengthRGB[2];
		double principalPointLeft[2], principalPointRight[2], principalPointRGB[2];
		double distortionLeft[5], distortionRight[5], distortionRGB[5];
		double rotationLeftRight[9], rotationLeftRGB[9];
		double translationLeftRight[3], translationLeftRGB[3];

		// Perform calibration with user custom algo here including
		//   calibration stream setup and frame capture
		//   calibration computation with custom algo
		//   obtain optimized calibration parameters
		//
		// ***** A LOT OF YOUR CODE HERE for custom calibration *****
		//
		// An example of the parameter from a D400 device
		//    resolutionLeftRight: 1920 1080
		//
		//    FocalLengthLeft :   1365.328979 1372.806641
		//    PrincipalPointLeft : 959.393311 536.781494
		//    DistortionLeft :       0.130178 - 0.393367 - 0.000580 0.001172 0.326398
		//
		//    FocalLengthRight :  1371.838989 1379.178101
		//    PrincipalPointRight: 961.465759 540.101624
		//    DistortionRight :      0.121403 - 0.385616 - 0.001131 - 0.000172 0.325395
		//
		//    RotationLeftRight : 0.999980 0.000408 - 0.006359
		//                      - 0.000443 0.999985 - 0.005404
		//                        0.006357 0.005407 0.999965
		//    TranslationLeftRight : -55.109779 - 0.111518 - 0.114459
		//    HasRGB : 0
		//
		// Another example of the parameters from a D435 device
		//
		//    resolutionLeftRight : 1280 800
		//
		//    FocalLengthLeft : 639.322205 637.623474
		//    PrincipalPointLeft : 645.968262 399.232727
		//    DistortionLeft : -0.057135 0.067378 0.000959 - 0.000607 - 0.021941
		//
		//    FocalLengthRight : 640.831848 639.201416
		//    PrincipalPointRight : 641.968384 405.641235
		//    DistortionRight : -0.056585 0.065952 0.000865 - 0.000556 - 0.021422
		//
		//    RotationLeftRight : 0.999997 - 0.001835 - 0.001385
		//                        0.001835 0.999998 - 0.000234
		//                        0.001385 0.000232 0.999999
		//    TranslationLeftRight : -50.030815 - 0.005517 0.060515
		//
		//    HasRGB : 1
		//    resolutionRGB : 1920 1080
		//    FocalLengthColor : 1376.079590 1375.954102
		//    PrincipalPointColor : 947.814758 543.885315
		//    DistortionColor : 0.000000 0.000000 0.000000 0.000000 0.000000
		//    RotationLeftColor : 0.999981 - 0.003833 0.004792
		//                        0.003843 0.999990 - 0.002125
		//                      - 0.004784 0.002143 0.999986
		//   TranslationLeftColor : 14.624806 0.352931 0.213506
		// *******************************************************************************************************

		if (CmdLineOptions.bWrite && !CmdLineOptions.dumpFile.empty())
		{
			string str;
			ifstream inFile;
			inFile.open(CmdLineOptions.dumpFile);
			if (inFile.fail())
			{
				std::cout << "Open " << CmdLineOptions.dumpFile << " failed." << std::endl;
				if (m_dcApi) delete m_dcApi;
				return EXIT_FAILURE;
			}

			cout << "reading calibration parameters from input file ..." << endl;
			ReadCustomCalibrationParametersFromFile(CmdLineOptions.dumpFile, resolutionLeftRight, focalLengthLeft, principalPointLeft, distortionLeft, focalLengthRight, principalPointRight,
				distortionRight, rotationLeftRight, translationLeftRight, hasRGB, resolutionRGB, focalLengthRGB, principalPointRGB, distortionRGB, rotationLeftRGB, translationLeftRGB);

			//
			// Write the optimized calibration parameters to device. This will alter the calibration on your device, please uncomment
			// the following code only when necessary.
			//
			status = m_dcApi->WriteCustomCalibrationParameters(resolutionLeftRight, focalLengthLeft, principalPointLeft, distortionLeft, focalLengthRight, principalPointRight,
				distortionRight, rotationLeftRight, translationLeftRight, hasRGB, resolutionRGB, focalLengthRGB, principalPointRGB, distortionRGB, rotationLeftRGB, translationLeftRGB);

			if (status != DC_SUCCESS)
			{
				cout << rs_convert_err_to_string(status) << endl;

				if (m_dcApi) delete m_dcApi;
				return status;
			}

			cout << "Calbration data updated successfully." << endl;
		}


		// Read back from device to confirm
		status = m_dcApi->ReadCalibrationParameters(resolutionLeftRight, focalLengthLeft, principalPointLeft, distortionLeft, focalLengthRight, principalPointRight,
			distortionRight, rotationLeftRight, translationLeftRight, hasRGB, resolutionRGB, focalLengthRGB, principalPointRGB, distortionRGB, rotationLeftRGB, translationLeftRGB);

		if (status != DC_SUCCESS)
		{
			cout << rs_convert_err_to_string(status) << endl;

			delete m_dcApi;
			return status;
		}

		cout << "Calibration parameters from the device:" << endl;
		cout << fixed << setprecision(6);

		cout << "  resolutionLeftRight: " << resolutionLeftRight[0] << " " << resolutionLeftRight[1] << endl << endl;
		cout << "  FocalLengthLeft: " << focalLengthLeft[0] << " " << focalLengthLeft[1] << endl;
		cout << "  PrincipalPointLeft: " << principalPointLeft[0] << " " << principalPointLeft[1] << endl;
		cout << "  DistortionLeft: " << distortionLeft[0] << " " << distortionLeft[1] << " " << distortionLeft[2] << " " << distortionLeft[3] << " " << distortionLeft[4] << endl << endl;

		cout << "  FocalLengthRight: " << focalLengthRight[0] << " " << focalLengthRight[1] << endl;
		cout << "  PrincipalPointRight: " << principalPointRight[0] << " " << principalPointRight[1] << endl;
		cout << "  DistortionRight: " << distortionRight[0] << " " << distortionRight[1] << " " << distortionRight[2] << " " << distortionRight[3] << " " << distortionRight[4] << endl << endl;

		cout << "  RotationLeftRight: " << rotationLeftRight[0] << " " << rotationLeftRight[1] << " " << rotationLeftRight[2] << endl;
		cout << "                     " << rotationLeftRight[3] << " " << rotationLeftRight[4] << " " << rotationLeftRight[5] << endl;
		cout << "                     " << rotationLeftRight[6] << " " << rotationLeftRight[7] << " " << rotationLeftRight[8] << endl;
		cout << "  TranslationLeftRight: " << translationLeftRight[0] << " " << translationLeftRight[1] << " " << translationLeftRight[2] << endl << endl;

		cout << "  HasRGB: " << (hasRGB ? 1 : 0) << endl << endl;

		if (hasRGB)
		{
			cout << "  resolutionRGB: " << resolutionRGB[0] << " " << resolutionRGB[1] << endl << endl;
			cout << "  FocalLengthColor: " << focalLengthRGB[0] << " " << focalLengthRGB[1] << endl;
			cout << "  PrincipalPointColor: " << principalPointRGB[0] << " " << principalPointRGB[1] << endl;
			cout << "  DistortionColor: " << distortionRGB[0] << " " << distortionRGB[1] << " " << distortionRGB[2] << " " << distortionRGB[3] << " " << distortionRGB[4] << endl;

			cout << "  RotationLeftColor: " << rotationLeftRGB[0] << " " << rotationLeftRGB[1] << " " << rotationLeftRGB[2] << endl;
			cout << "                     " << rotationLeftRGB[3] << " " << rotationLeftRGB[4] << " " << rotationLeftRGB[5] << endl;
			cout << "                     " << rotationLeftRGB[6] << " " << rotationLeftRGB[7] << " " << rotationLeftRGB[8] << endl;
			cout << "  TranslationLeftColor: " << translationLeftRGB[0] << " " << translationLeftRGB[1] << " " << translationLeftRGB[2] << endl << endl;
		}

		if (CmdLineOptions.bRead && !CmdLineOptions.dumpFile.empty())
		{
			CalibParamXmlWrite::WriteCustomCalibrationParametersToFile(CmdLineOptions.dumpFile, resolutionLeftRight, focalLengthLeft, principalPointLeft, distortionLeft, focalLengthRight,
				principalPointRight, distortionRight, rotationLeftRight, translationLeftRight, hasRGB, resolutionRGB, focalLengthRGB, principalPointRGB,
				distortionRGB, rotationLeftRGB, translationLeftRGB);
		}


		if (CmdLineOptions.bExtra)
		{
            cout << endl << "Extra calibration information:" << endl;

			float rl[9], rr[9];
			m_dcApi->ReadCalibration_World_Rotation(rl, rr);

			cout << endl << "World to left rotation matrix (inverse rotation of the left camera in rectified coordinate system):" << endl;

			for (int i = 0; i < 3; i++)
			{
				for (int j = 0; j < 3; j++)
					cout << "  " << rl[i * 3 + j];

				cout << endl;
			}

			cout << endl << "World to right rotation matrix (inverse rotation of the right camera in rectified coordinate system):" << endl;

			for (int i = 0; i < 3; i++)
			{
				for (int j = 0; j < 3; j++)
					cout << "  " << rr[i * 3 + j];

				cout << endl;
			}

			if (hasRGB)
			{
				cout << endl << "RGB camera intrinsics: " << endl;
				DC_Intrinsics intr;

				status = m_dcApi->ReadCalibration_RGB_Intrinsic(intr);

				if (status == DC_SUCCESS)
				{
					print_intrinsics(intr);
				}
				else
				{
					cout << rs_convert_err_to_string(status) << endl;
				}

				cout << endl << "RGB extrinsics in rectified coordinate system:" << endl;
				float r[9], t[3];
				status = m_dcApi->ReadCalibration_RGB_Extrinsic_Rectified(r, t);

				if (status == DC_SUCCESS)
				{
					cout << " Rotation Matrix:\n";

					for (int i = 0; i < 3; i++)
					{
						for (int j = 0; j < 3; j++)
							cout << "  " << r[i * 3 + j];

						cout << endl;
					}

					cout << "\n Translation Vector:\n";

					for (int i = 0; i < 3; i++)
					{
						cout << "  " << t[i];
					}

					cout << endl;
				}
				else
				{
					cout << rs_convert_err_to_string(status) << endl;
				}
			}
		}
	}

    // Release device handle
	if (m_dcApi) delete m_dcApi;
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



