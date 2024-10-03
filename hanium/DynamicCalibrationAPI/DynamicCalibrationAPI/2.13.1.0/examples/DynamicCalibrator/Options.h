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

#pragma once

#include "CommandLine.h"
#include <string>

namespace DynamicCalibrator
{
    using namespace std;

#ifdef _WIN32
#define DEFAULT_GIMBAL_SERIALPORT "com1"
#else
#define DEFAULT_GIMBAL_SERIALPORT "/dev/ttyUSB0"
#endif

    struct Options
    {
        bool bShowHelp{ false };
        bool bShowCameraList{ false };
        int  UseLaser{ true };
        int  SaveFrame{ -1 };
        bool bTargeted{ true };
        bool bAESweepAuto{ true };
        int  AESetpoint{ 1000 };
        bool bShowVer{ false };
        string CameraSerial{};
        bool bUseGimbal{ false };
        string GimbalSerialPort{};
        int timeOut{ -1 }; // in seconds
        bool bCliMode{ false };
        bool bGetRectErrorOnly{ false };
        bool bAutoExposureDisable{ false };
        int  depthExposure{ 0 };
        int  colorExposure{ 0 };

		bool bDevTargetAligned{ false };
		bool bSkipRGB{ false };
		bool bIgnoreBorders{ false };
		int calibrationMode{ -1 };
		int numScaleImages{ -1 };
		bool bForce{ false };
		bool bVerbose{ false };

        bool ParseCmdOptions(int argc, char * argv[], string& HelpMessage)
        {
            int AESetpointForced = -1;

            // Parse command line options
            CommandLine cl(argc, argv);

            cl.addOption(bShowHelp, "-help", "-?", "display list of command line options");
			cl.addOption(bShowVer, "-version", "-v", "show dynamic calibration version info");
			cl.addOption(bCliMode, "-cli", "-cli", "run in non-interactive command line interface");
			cl.addOption(bShowCameraList, "-show", "-list", "display list of connected cameras");
			cl.addOption(CameraSerial, "camera serial number", "-sn", "-serial", "if multiple cameras connected to the current system, choose one of the cameras to calibrate by specifying its serial number");
			cl.addOption(calibrationMode, "0, 1, 2, 3, or 4", "-mode", "-m", "select calibration mode: 0 for target-less calibration, 1 for targeted calibration, 2 for hybrid calibration, 3 for scale only (for debugging), 4 for rgb only (for debugging)");
            cl.addOption(SaveFrame, "0 or 1", "-dump", "-d", "(for debugging) dump calibration frames and results to files. 1 to dump every frames");
            cl.addOption(AESetpointForced, "0 to 4095", "-setpoint", "-s", "force AE setpoint to adjust auto exposure reference point");
            cl.addOption(timeOut, "in seconds" ,"-timeout", "-t", "time out duration in seconds");
            cl.addOption(bGetRectErrorOnly, "-error", "-e", "report rectification (vertical alignment) error in pixels periodically until timeout");
			cl.addOption(UseLaser, "0 or 1", "-laser", "-l", "force turn on or off laser in target-less calibration");
			cl.addOption(GimbalSerialPort, "Gimbal comport name", "-gimbal", "--gimbal", "Gimbal comport name");

// disabling manual exposure options due to lack of RGB frame sync under manual exposure         
//          cl.addOption(bAutoExposureDisable, "-AE", "-ae", "Disable auto expousure");
//          cl.addOption(depthExposure, "Depth exposure value", "-DE", "-de", "Set Depth Exposure ");
//          cl.addOption(colorExposure, "RGB exposure value", "-RE", "-re", "Set RGB Exposure");
		
			cl.addOption(bDevTargetAligned, "-a", "-aligned", "device and target aligned in orientation, for example, device is mounted vertically, and target is positioned vertically");
			cl.addOption(bSkipRGB, "-skiprgb", "-skiprgb", "Skip RGB calibration.");
			cl.addOption(bIgnoreBorders, "-ignore-borders", "-ignore-borders", "ignore the border blocks during target-less rectification.");
			cl.addOption(numScaleImages, "more than 6", "-max-images", "-max-images", "number of images to capture in scale calibration and rgb calibration");
			cl.addOption(bForce, "-force", "-force", "force the specified parameters");
			cl.addOption(bVerbose, "-verbose", "-verbose", "verbose debug messages");

            int invalidoptions = cl.checkAllArgsUsed();

            if (-1 == AESetpointForced)
            {
				bAESweepAuto = true;
                AESetpoint = 1000;
            }
            else
            {
				bAESweepAuto = false;
                AESetpoint = AESetpointForced;
            }

            if (GimbalSerialPort.empty())
            {
                bUseGimbal = false;
                GimbalSerialPort = string(DEFAULT_GIMBAL_SERIALPORT);
            }
            else
            {
                bUseGimbal = true;
            }

            if (timeOut <= 0)
            {
				if (bGetRectErrorOnly)
					timeOut = 18;
				else
					timeOut = 180;
            }

            // calibration mode
            // 0 - target-less rectification
            // 1 - targeted calibration (targeted rectification + targeted scale) (default)
            // 2 - hybrid calibration (target-less rectification + targeted scale calibration)
            // 3 - scale calibration
            // 4 - rgb calibration
            
            // if no calibration mode is specified, default to targeted calibration
            if (calibrationMode < 0)
                calibrationMode = 1;

            HelpMessage = cl.getHelpMessage();

            // -1: error, 0: success
            return (invalidoptions == -1) ? false : true;
        }
    };
}
