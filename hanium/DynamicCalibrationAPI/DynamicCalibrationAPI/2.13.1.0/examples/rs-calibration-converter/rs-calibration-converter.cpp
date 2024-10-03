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

#include "DSDynamicCalibration.h"
#include "DSCalData.h"

#include "CommandLine.h"
#include "CalibParamXmlWrite.h"
#include "rs_utils.h"


using namespace std;
using namespace DynamicCalibrationAPI;
using namespace CalibParamXmlWrite;

//
// This example demos usage of the calibration parameter read/write APIs for calibration data conversions
//
// The D400 devices stores calibration data in proprietary internal format on the device. The calibration
// tools supplied by Intel manage these data transparently. However, in some usage cases, users desire to
// calibrate the devices with their own algorithms and in such cases the calibration parameters from user
// custom calibration need to be transferred to the device in the fomrat that's compatible with d400 devices
// in order to take effect. The custom calibration read/write apis are provided to meet this need.
// 
// The custom calibration read/write apis can directly read/write to the physical device. This is
// demonstrated in the CustomRW tool and example for supported platforms. In other cases, the CustomRW tool
// may not support user's platform. The custom calibration read/write apis were improved to support device-less
// calibration data conversions. The user can use the apis to convert from their custom calibration parameters
// into d400 compatible binary format and use other tools to write the data into the device. For example,
// convert the parameters on Intel/Windows 10 into d400 calibration binary data and then transfer the data to the
// desired platform, like ARM/Yocto, where another simpler open source tool can be ported and write the data
// into physical devices.
//
// In those custom calibration use cases, the user is responsible to come up the correct calibration
// parameters with their own algorithm, and APIs are available to convert those high level calibration
// paramaters into d400 compatible format, or vice versa.
//
//  The Vision Calibration Data is an Intel prietary binary file lumped all tables together in the order
//     coefficient table (0x19) 512 bytes
//     depth table (0x1F)       256 bytes
//     rgb table (0x20)         256 bytes (only applies for devices with rgb)
//   since coeffcient table and depth table are required on every device, so the input file size is either
//   768 bytes or 1024 bytes.
//
//
// Example #1, to convert user custom calibration parameters into d400 compatible format:
//   DynamicCalibrationAPI::DSDynamicCalibration *m_dcApi = new DSDynamicCalibration();
//   m_dcApi->Initialize(NULL, DynamicCalibrationAPI::DSDynamicCalibration::CAL_MODE_USER_CUSTOM);
//   ...
//   prepare user custom calibration parameters
//   ...
//   write the parameters to library and automatically convert into d400 compatible data inside the library
//   m_dcApi->WriteCustomCalibrationParameters(......)
//   ...
//   read back d400 compatible data from library
//   m_dcApi->ReadCalibrationRawData(pTableCoff, DSDynamicCalibration::CAL_TABLE_COEFF)
//   m_dcApi->ReadCalibrationRawData(pTableDepth, DSDynamicCalibration::CAL_TABLE_DEPTH)
//   m_dcApi->ReadCalibrationRawData(pTableRgb, DSDynamicCalibration::CAL_TABLE_RGB)
//   ...
//   write d400 compatible data into a file that can be transported to the desired platform and write to
//   physical device with other tools, for example, Intel.RealSense.CustomRW tool.
//
// Example #2, convert d400 compatible calibration data into high level calibration parameters that
// user can read. The d400 calibration data can be from previous conversions, saved from actual device, or
// from Intel calibration tools.
//   DynamicCalibrationAPI::DSDynamicCalibration *m_dcApi = new DSDynamicCalibration();
//   m_dcApi->Initialize(NULL, DynamicCalibrationAPI::DSDynamicCalibration::CAL_MODE_USER_CUSTOM);
//   ...
//   read d400 calibration data into appropriate calibration tables (coefficient, depth and rgb tables)
//   ...
//   write the binary tables to the library
//   m_dcApi->WriteCalibrationRawData(pTableCoff, DSDynamicCalibration::CAL_TABLE_COEFF)
//   m_dcApi->WriteCalibrationRawData(pTableDepth, DSDynamicCalibration::CAL_TABLE_DEPTH)
//   m_dcApi->WriteCalibrationRawData(pTableRgb, DSDynamicCalibration::CAL_TABLE_RGB)
//   ...
//   read high level parameters back from the library
//   m_dcApi->ReadCalibrationParameters(......)
//
//
//


struct Options
{
	bool bShowHelp{ false };
	bool bVerbose{ false };

	bool bBin2Xml{ false };
	bool bXml2Bin{ false };

	bool bExtra{ false };

	string inputFile{};
	string outFile{};

	bool ParseCmdOptions(int argc, char * argv[], string& HelpMessage)
	{
		// parse command line options
		CommandLine cl(argc, argv);

		cl.addOption(bShowHelp, "--help", "-?", "display list of command line options");
		cl.addOption(bVerbose, "--verbose", "-v", "display verbose debugging messages");

		cl.addOption(bBin2Xml, "--bin2xml", "-bin2xml", "convert binary calibration data to parameters in xml format");
		cl.addOption(bXml2Bin, "--xml2bin", "-xml2bin", "convert calibration parameters specified in xml format into binary format compatible with D400 devices");

		cl.addOption(inputFile, "input file name", "--input", "-i", "read input data from the specified file");
		cl.addOption(outFile, "output file name", "--output", "-o", "write output data to the specified file");

		cl.addOption(bExtra, "--extra", "-ex", "print extra calibration information to console");

		int invalidoptions = cl.checkAllArgsUsed();
		HelpMessage = cl.getHelpMessage();

		// -1: error, 0: success
		return (invalidoptions == -1 || cl.numArgs() == 0) ? false : true;
	}
};


void print_help(char * execmd)
{
	cout << endl;
	cout << "Usages:" << endl;
	cout << "The calibration parameters are saved in XML format. The D400 compatible binary calibration table data is saved in Intel prietary Vision Calibration Data format." << endl;
	cout << endl;
	cout << "Example #1: convert user calibration parameters into d400 compatible binary data file" << endl;
	cout << "    " << execmd << " -xml2bin -i sample-d430.xml -o mycal.bin" << endl;
	cout << endl;
	cout << "Example #2: convert user calibration parameters into d400 compatible binary data and print it to screen" << endl;
	cout << "    " << execmd << " -xml2bin -i sample-d430.xml" << endl;
	cout << endl;
	cout << "Example #3: convert d400 compatible binary calibration data into a text file in xml format" << endl;
	cout << "    " << execmd << " -bin2xml -i mycal.bin -o my.xml" << endl;
	cout << endl;
	cout << "Example #4: convert d400 compatible binary calibration data into xml format and print it to screen" << endl;
	cout << "    " << execmd << " -bin2xml -i mycal.bin" << endl;
	cout << "Example #5: convert user calibration parameters into d400 compatible binary data and extract extra calibration information onto screen" << endl;
	cout << "    " << execmd << " -xml2bin -i sample-d430.xml -ex" << endl;
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
	cout << "rs-calibration-converter for Intel RealSense Technology, Version: " << DS_DYNAMIC_CALIBRATION_VERSION << endl << endl;

	Options CmdLineOptions;
	string HelpMessage;

	bool optionsOK = CmdLineOptions.ParseCmdOptions(argc, argv, HelpMessage);

	if (!optionsOK || CmdLineOptions.bShowHelp)
	{
		cout << HelpMessage << endl;
		print_help(argv[0]);
		return optionsOK ? EXIT_SUCCESS : EXIT_FAILURE;
	}

    if (!CmdLineOptions.inputFile.empty())
    {
        if (!file_exist(CmdLineOptions.inputFile.c_str()))
        {
            cout << "Error: cannot find input file " << CmdLineOptions.inputFile << endl;
            return EXIT_FAILURE;
	    }
    }
	else
	{
		cout << "Error: no input file is provided." << endl;
		return EXIT_FAILURE;
	}

	int status = DC_SUCCESS;

	// create Dynamic Calibration API interface
	DynamicCalibrationAPI::DSDynamicCalibration *m_dcApi = new DSDynamicCalibration();

	status = m_dcApi->Initialize(NULL, DynamicCalibrationAPI::DSDynamicCalibration::CAL_MODE_USER_CUSTOM);

	if (status != DC_SUCCESS)
	{
		cout << "dc api initilialization failed: " << status << endl;
		return EXIT_FAILURE;
	}

    //
    // The expected calibration parameters for D400 series devices are defined as following:
    //
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
    bool hasRGB = false;
    int resolutionLeftRight[2], resolutionRGB[2];
    double focalLengthLeft[2], focalLengthRight[2], focalLengthRGB[2];
    double principalPointLeft[2], principalPointRight[2], principalPointRGB[2];
    double distortionLeft[5], distortionRight[5], distortionRGB[5];
    double rotationLeftRight[9], rotationLeftRGB[9];
    double translationLeftRight[3], translationLeftRGB[3];

    // Perform calibration with user custom algo and obtain optimized calibration parameters
    //
    // An example of the parameters from a D400 device
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
    // resolutionLeftRight: 1280 800
    //
    // FocalLengthLeft : 642.016968 642.227966
    // PrincipalPointLeft : 639.621033 395.596008
    // DistortionLeft : -0.048908 0.053317 - 0.000203 - 0.000408 - 0.016420
    //
    // FocalLengthRight : 640.390991 640.862976
    // PrincipalPointRight : 642.309021 393.813995
    // DistortionRight : -0.050081 0.054582 - 0.000205 - 0.000309 - 0.016406
    //
    // RotationLeftRight : 0.999992 - 0.004075 0.000347
    //                     0.004075 0.999991 - 0.001125
    //                   - 0.000342 0.001127 0.999999
    // TranslationLeftRight : -50.151600 - 0.183895 0.191991
    //
    // HasRGB : 1
    //
    // resolutionRGB : 1920 1080
    //
    // FocalLengthColor : 1381.300049 1382.469971
    // PrincipalPointColor : 970.752991 547.115967
    // DistortionColor : 0.000000 0.000000 0.000000 0.000000 0.000000
    // RotationLeftColor : 0.999938 - 0.011143 0.000610
    //                     0.011144 0.999937 - 0.001491
    //                   - 0.000594 0.001498 0.999999
    // TranslationLeftColor : 15.070100 0.057487 0.163458
    // *******************************************************************************************************
    //
    // The same set of sample D435 calibration parameters are saved in XML format as input to convert into D400
    // binary Vision Calibration Data format or as output when convert from a binary data into user readable
    // format. This same XML format is used by the Intel RealSense CustomRW tool as well.
    //
	//< ? xml version = "1.0" ? >
	//	<Config>
	//	<param name = "ResolutionLeftRight">
	//	<value>1280< / value>
	//	<value>800< / value>
	//	< / param>
	//	<param name = "FocalLengthLeft">
	//	<value>642.017< / value>
	//	<value>642.228< / value>
	//	< / param>
	//	<param name = "PrincipalPointLeft">
	//	<value>639.621< / value>
	//	<value>395.596< / value>
	//	< / param>
	//	<param name = "DistortionLeft">
	//	<value>-0.0489082< / value>
	//	<value>0.0533167< / value>
	//	<value>-0.000203188< / value>
	//	<value>-0.000408171< / value>
	//	<value>-0.0164199< / value>
	//	< / param>
	//	<param name = "FocalLengthRight">
	//	<value>640.391< / value>
	//	<value>640.863< / value>
	//	< / param>
	//	<param name = "PrincipalPointRight">
	//	<value>642.309< / value>
	//	<value>393.814< / value>
	//	< / param>
	//	<param name = "DistortionRight">
	//	<value>-0.0500806< / value>
	//	<value>0.0545825< / value>
	//	<value>-0.000204965< / value>
	//	<value>-0.000308591< / value>
	//	<value>-0.0164062< / value>
	//	< / param>
	//	<param name = "RotationLeftRight">
	//	<value>0.999992< / value>
	//	<value>-0.00407484< / value>
	//	<value>0.000347068< / value>
	//	<value>0.00407523< / value>
	//	<value>0.999991< / value>
	//	<value>-0.00112548< / value>
	//	<value>-0.000342479< / value>
	//	<value>0.00112688< / value>
	//	<value>0.999999< / value>
	//	< / param>
	//	<param name = "TranslationLeftRight">
	//	<value>-50.1516< / value>
	//	<value>-0.183895< / value>
	//	<value>0.191991< / value>
	//	< / param>
	//	<param name = "HasRGB">
	//	<value>1< / value>
	//	< / param>
	//	<param name = "ResolutionRGB">
	//	<value>1920< / value>
	//	<value>1080< / value>
	//	< / param>
	//	<param name = "FocalLengthRGB">
	//	<value>1381.3< / value>
	//	<value>1382.47< / value>
	//	< / param>
	//	<param name = "PrincipalPointRGB">
	//	<value>970.753< / value>
	//	<value>547.116< / value>
	//	< / param>
	//	<param name = "DistortionRGB">
	//	<value>0< / value>
	//	<value>0< / value>
	//	<value>0< / value>
	//	<value>0< / value>
	//	<value>0< / value>
	//	< / param>
	//	<param name = "RotationLeftRGB">
	//	<value>0.999938< / value>
	//	<value>-0.0111434< / value>
	//	<value>0.000610457< / value>
	//	<value>0.0111443< / value>
	//	<value>0.999937< / value>
	//	<value>-0.00149119< / value>
	//	<value>-0.000593801< / value>
	//	<value>0.0014979< / value>
	//	<value>0.999999< / value>
	//	< / param>
	//	<param name = "TranslationLeftRGB">
	//	<value>15.0701< / value>
	//	<value>0.0574875< / value>
	//	<value>0.163458< / value>
	//	< / param>
	//	< / Config>
    //
    // 

    // vision calibration data buffer
    uint8_t *pVision = NULL;

    if (CmdLineOptions.bXml2Bin)
    {
		// convert custom calibration parameters into d400 compatible binary format
		//
		//   DynamicCalibrationAPI::DSDynamicCalibration *m_dcApi = new DSDynamicCalibration();
		//   m_dcApi->Initialize(NULL, DynamicCalibrationAPI::DSDynamicCalibration::CAL_MODE_USER_CUSTOM);
		//   ...
		//   prepare user custom calibration parameters
		//   ...
		//   write the parameters to library and automatically convert into d400 compatible data inside the library
		//   m_dcApi->WriteCustomCalibrationParameters(......)
		//   ...
		//   read back d400 compatible data from library
		//   m_dcApi->ReadCalibrationRawData(pTableCoff, DSDynamicCalibration::CAL_TABLE_COEFF)
		//   m_dcApi->ReadCalibrationRawData(pTableDepth, DSDynamicCalibration::CAL_TABLE_DEPTH)
		//   m_dcApi->ReadCalibrationRawData(pTableRgb, DSDynamicCalibration::CAL_TABLE_RGB)
		//   ...
		//   write d400 compatible data into a file that can be transported to the desired platform and write to
		//   physical device.
		//
		// the user input calibration parameters are formulated in xml format as an example, user is free to choose
		// any desired input format for their application, but it may be more convienient to use this xml format
		// since this is the format used in the Intel tools and can be transportable.
        //


		cout << "reading calibration parameters from input file ..." << endl;
        ReadCustomCalibrationParametersFromFile(CmdLineOptions.inputFile, resolutionLeftRight, focalLengthLeft, principalPointLeft, distortionLeft, focalLengthRight, principalPointRight,
				distortionRight, rotationLeftRight, translationLeftRight, hasRGB, resolutionRGB, focalLengthRGB, principalPointRGB, distortionRGB, rotationLeftRGB, translationLeftRGB);

        // write custom calibration parameters to the library which converts internally into d400 compatible binary format
		cout << "writing calibration parameters to library for conversion ..." << endl;
        status = m_dcApi->WriteCustomCalibrationParameters(resolutionLeftRight, focalLengthLeft, principalPointLeft, distortionLeft, focalLengthRight, principalPointRight,
				distortionRight, rotationLeftRight, translationLeftRight, hasRGB, resolutionRGB, focalLengthRGB, principalPointRGB, distortionRGB, rotationLeftRGB, translationLeftRGB);

        if (status != DC_SUCCESS)
        {
            cout << rs_convert_err_to_string(status) << endl;

            if (m_dcApi) delete m_dcApi;
            return status;
        }

       // read back the d400 compatible binary calibration data from library
       // either by reading the tables individually or all tables together in Vision Calibration Data
       //

	   // read all tables together in Vision Calibration Data
	   int vision_data_size = 0;

	   if (hasRGB)
	   {
		   vision_data_size = MAX_VISION_DATA_SIZE;
	   }
	   else
	   {
		   vision_data_size = MIN_VISION_DATA_SIZE;
	   }

	   pVision = (uint8_t*) malloc(vision_data_size);
	   status = m_dcApi->ReadCalibrationRawData(pVision, DSDynamicCalibration::CAL_TABLE_ALL);
	   if (status != DC_SUCCESS)
	   {
		   cout << rs_convert_err_to_string(status) << endl;
		   if (pVision) free(pVision);
		   if (m_dcApi) delete m_dcApi;
		   return EXIT_FAILURE;
	   }

	   // print the binary calibration data to screen or into a output file
	   string output = CmdLineOptions.outFile;

	   if (output.empty())
	   {
		   cout << "vision calibration data: " << endl;
		   cout << dump_buffer_to_console(pVision, vision_data_size);
	   }
	   else
	   {
		   cout << "writing vision calibration data into output file " << output << endl;
		   ofstream myFile(output, ios::out | ios::binary | ios::trunc);
		   myFile.write((const char*)pVision, vision_data_size);
		   myFile.close();

		   cout << "calbration data converted successfully." << endl;
	   }
    }
    else if (CmdLineOptions.bBin2Xml)
    {
        // convert d400 compatible calibration data into high level calibration parameters that
        // user can read. The d400 calibration data can be from previous conversions, saved from actual device, or
        // from Intel calibration tools.
        //
        //   DynamicCalibrationAPI::DSDynamicCalibration *m_dcApi = new DSDynamicCalibration();
        //   m_dcApi->Initialize(NULL, DynamicCalibrationAPI::DSDynamicCalibration::CAL_MODE_USER_CUSTOM);
        //   ...
        //   read d400 calibration data into appropriate calibration tables (coefficient, depth and rgb tables)
        //   the input is a binary file lumped all tables together in the order
        //     coefficient table (0x19) 512 bytes
        //     depth table (0x1F)       256 bytes
        //     rgb table (0x20)         256 bytes (only applies for devices with rgb)
        //   since coeffcient table and depth table are required on every device, so the input file size is either
        //   768 bytes ( coefficient + depth for devices without rgb) or 1024 bytes (coefficient + depth + rgb for devices with rgb).
        //   ...
        //   write the binary tables to the dc library
        //   m_dcApi->WriteCalibrationRawData(pTableCoff, DSDynamicCalibration::CAL_TABLE_COEFF)
        //   m_dcApi->WriteCalibrationRawData(pTableDepth, DSDynamicCalibration::CAL_TABLE_DEPTH)
        //   m_dcApi->WriteCalibrationRawData(pTableRgb, DSDynamicCalibration::CAL_TABLE_RGB)
        //   ...
        //   read high level parameters back from the library
        //   m_dcApi->ReadCalibrationParameters(......)
        //
        ifstream myFile(CmdLineOptions.inputFile, ios::out | ios::binary);

        myFile.seekg(0, myFile.end);
        int length = myFile.tellg();
        myFile.seekg(0, myFile.beg);

        cout << "input binary file length: " << length << endl;

		if ((length != MIN_VISION_DATA_SIZE)    &&      // table 0x19 and 0x1f
			(length != MAX_VISION_DATA_SIZE))           // tables 0x19, 0x1f, and 0x20
		{
			cout << "wrong input file size. input file should be either " << MIN_VISION_DATA_SIZE << " or ";
			cout << MAX_VISION_DATA_SIZE << " bytes" << endl;
			return EXIT_FAILURE;
		}

        // setup all tables together in vision calibration data
        // pVision buffer should be the maximum possible size, DC_CALIB_COEFF_TABLE_SIZE + DC_CALIB_DEPTH_TABLE_SIZE + DC_CALIB_RGB_TABLE_SIZE
        // even though there is no rgb table and the input file is smaller (the last DC_CALIB_RGB_TABLE_SIZE bytes in the buffer will be zeros)
		pVision = (uint8_t*) malloc (MAX_VISION_DATA_SIZE);
		myFile.read((char*)pVision, length);
		myFile.close();

		if (CmdLineOptions.bVerbose)
		{
            cout << dump_buffer_to_console((uint8_t*)pVision, MAX_VISION_DATA_SIZE);
		}

		// set the vision data into dc library
		status = m_dcApi->WriteCalibrationRawData(pVision, DSDynamicCalibration::CAL_TABLE_ALL);
        if (status != DC_SUCCESS)
        {
            cout << "dc api fail to set vision calibration data: " << status << endl;
            return EXIT_FAILURE;
        }

        // Read parameters from dc library
        status = m_dcApi->ReadCalibrationParameters(resolutionLeftRight, focalLengthLeft, principalPointLeft, distortionLeft, focalLengthRight, principalPointRight,
				distortionRight, rotationLeftRight, translationLeftRight, hasRGB, resolutionRGB, focalLengthRGB, principalPointRGB, distortionRGB, rotationLeftRGB, translationLeftRGB);

        if (status != DC_SUCCESS)
        {
            cout << rs_convert_err_to_string(status) << endl;

            if (m_dcApi) delete m_dcApi;
            return status;
        }

        if (CmdLineOptions.outFile.empty())
        {
            cout << "Calibration parameters from the input calibration data:" << endl;
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
        }
        else
        {
            cout << "writing calibration parameters into " << CmdLineOptions.outFile << endl;
            CalibParamXmlWrite::WriteCustomCalibrationParametersToFile(CmdLineOptions.outFile, resolutionLeftRight, focalLengthLeft, principalPointLeft, distortionLeft, focalLengthRight,
					principalPointRight, distortionRight, rotationLeftRight, translationLeftRight, hasRGB, resolutionRGB, focalLengthRGB, principalPointRGB,
					distortionRGB, rotationLeftRGB, translationLeftRGB);
        }

		cout << "calbration data converted successfully." << endl;
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

		cout << endl << "World to right rotation matrix (inverse rotation of the left camera in rectified coordinate system):" << endl;

		for (int i = 0; i < 3; i++)
		{
			for (int j = 0; j < 3; j++)
				cout << "  " << rr[i * 3 + j];

			cout << endl;
		}

		cout << endl << "RGB camera intrinsics:" << endl;
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

    // clean up
    if (pVision) free(pVision);
    if (m_dcApi) delete m_dcApi;

    return status;
}
catch (const std::exception& e)
{
    std::cerr << e.what() << std::endl;
    return EXIT_FAILURE;
}



