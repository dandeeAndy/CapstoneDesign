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
#include "GuiView.h"
#include "CliView.h"
#include "GL/freeglut.h"
#include "DSDynamicCalibration.h"
#include "Options.h"
#include "Gimbal.h"

#include <iomanip>


using namespace std;
using namespace DynamicCalibrator;
using namespace GIMBAL;

static void DisplayCameraList(void)
{
    std::unique_ptr<CaptureManager> pManger(new CaptureManager());
    auto devices = pManger->ListCameras();

    size_t device_count = devices.size();
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
        auto dev = devices[i];

        cout << left << setw(40) << dev.name
            << setw(15) << dev.serial
            << setw(20) << dev.fw_ver
            << setw(10) << dev.usb_type
	    << setw(40) << dev.physical_port
            << endl;
    }
}

template<typename T, typename ...Args>
std::unique_ptr<T> make_unique(Args&& ...args)
{
    return std::unique_ptr<T>(new T(std::forward<Args>(args)...));
}


int main(int argc, char * argv[])
{
    Options CmdLineOptions;
    string HelpMessage;
	Gimbal *m_gimbal = NULL;

    bool ret = CmdLineOptions.ParseCmdOptions(argc, argv, HelpMessage);

    if (!ret || CmdLineOptions.bShowHelp)
    {
        cout << HelpMessage << endl;
        return ret ? EXIT_SUCCESS : EXIT_FAILURE;
    }

    if (CmdLineOptions.bShowVer)
    {
        cout << DS_DYNAMIC_CALIBRATION_VERSION << endl;
        return EXIT_SUCCESS;
    }

    if (CmdLineOptions.bShowCameraList)
    {
        DisplayCameraList();
        return EXIT_SUCCESS;
    }

    bool bCliMode = false;

#if defined(_WIN32) && defined(_CONSOLE)
    bCliMode = true;
#endif

    if (CmdLineOptions.bCliMode)
    {
        bCliMode = true;
    }

/*
	cout << "Command line options:" << endl;
	cout << "AE setpoint: " << CmdLineOptions.AESetpoint << endl;
	cout << "AE auto sweep: " << CmdLineOptions.bAESweepAuto << endl;

	cout << "Device and target orientation aligned: " << CmdLineOptions.bDevTargetAligned << endl;
	cout << "Ignore borders: " << CmdLineOptions.bIgnoreBorders << endl;
	cout << "Skip rgb: " << CmdLineOptions.bSkipRGB << endl;
	cout << "Number of images in scale/rgb calibration: " << CmdLineOptions.numScaleImages << endl;
	cout << "Gimbal: " << CmdLineOptions.bUseGimbal << endl;
	cout << "Timeout: " << CmdLineOptions.timeOut << endl;

	cout << "Targeted: " << CmdLineOptions.bTargeted << endl;
	cout << "Hybrid mode: " << CmdLineOptions.bHybridMode << endl;

	cout << "Run rectification only: " << CmdLineOptions.RectifyOnly << endl;
	cout << "Run scale only: " << CmdLineOptions.bScaleCalibOnly << endl;
	cout << "Run RGB calibration only: " << CmdLineOptions.bRgbCalibOnly << endl;

	cout << "Mode: " << CmdLineOptions.calibrationMode << endl;
*/

	if (CmdLineOptions.numScaleImages > 0 && CmdLineOptions.numScaleImages < 6 && !CmdLineOptions.bForce)
	{
		cout << "Targeted calibration requires minimum 6 images. Less images may result sub-optimal results. If you want to experiment, please use the -force option along with -max-images option." << endl;
		return EXIT_FAILURE;
	}

	if ((CmdLineOptions.numScaleImages >= 0 || CmdLineOptions.calibrationMode != 1 || CmdLineOptions.bUseGimbal) && !bCliMode)
	{
		cout << "option not supported in GUI mode. Please run in command line mode with -cli option." << endl;
		return EXIT_FAILURE;
	}

	if (CmdLineOptions.calibrationMode == 1 && CmdLineOptions.bUseGimbal)
	{
		cout << "gimbal not supported in targeted calibration." << endl;
		return EXIT_FAILURE;
	}

    std::unique_ptr<MainView> view;

    if (bCliMode)
    {
        view = ::make_unique<CliView>();
    }
    else
    {
        view = ::make_unique<GuiView>();
    }

    view->SetCmdOptions(CmdLineOptions);

	if (view->Initialize() != DC_SUCCESS)
	{
		return view->GetErrorCode();
	}

	// gimbal
	if (CmdLineOptions.bUseGimbal && !CmdLineOptions.GimbalSerialPort.empty())
	{
		m_gimbal = new Gimbal(CmdLineOptions.GimbalSerialPort);

		if (!m_gimbal || !m_gimbal->IsConnected())
		{
			if (m_gimbal) delete m_gimbal;
			m_gimbal = nullptr;

			view->ErrorHandling(DC_ERROR_GIMBAL_NOT_START);

			return DC_ERROR_FAIL;
		}

		cout << "gimbal connected to serial port " << CmdLineOptions.GimbalSerialPort << endl;
		m_gimbal->EnableVerticalMove(false);

		view->pGimbal = m_gimbal;

		m_gimbal->Run();
	}

    glutMainLoop();

    int errCode = view->GetErrorCode();

	if (m_gimbal)
		delete m_gimbal;

    return errCode;
}

#ifdef _WIN32
int __stdcall WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, char*, int nShowCmd)
{
    return main(__argc, __argv);
}
#endif
