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
#include <cstring>
#include <algorithm>
#include "CliView.h"
#include "Stopwatch.h"
#include "signal.h"

using namespace std;
using namespace DynamicCalibrator;

CliView::CliView()
{
    m_devIdx = 0;

    // Handle Control-C signal
    signal(SIGINT, Control_C_Handler);

#ifndef _WIN32
    signal(SIGQUIT, Control_C_Handler);
#endif
}

CliView::~CliView()
{

}

int CliView::Initialize(void)
{
    m_captureManager = new CaptureManager(this, m_CmdOptions.SaveFrame, m_CmdOptions.bGetRectErrorOnly, m_loglevel);
    m_cameras = m_captureManager->ListCameras();
    m_devIdx = 0;

    int count = 0;
    while ((m_cameras.size() == 0) && (count++ < 60))
    {
        if (count == 1)
            cout << "No device detected, please connect camera to calibrate." << endl;

        std::this_thread::sleep_for(std::chrono::milliseconds(1000));

        m_cameras = m_captureManager->ListCameras();
    }

    if (m_cameras.size() == 0)
    {
        m_errorCode = DC_ERROR_CAMERA_NOT_PLUGGED;
        return m_errorCode;
    }

    camera_info camera = m_cameras[0];

    if (!m_sn.empty())
    {
        auto it = std::find_if(m_cameras.begin(), m_cameras.end(), [&](const camera_info & o) {
            return o.serial == m_sn;
        });

        if (it != m_cameras.end())
        {
            m_devIdx = (int)std::distance(m_cameras.begin(), it);
            camera = *it;
        }
        else
        {
            cout << "Error, invalid camera serial number specified!" << endl;
            m_errorCode = DC_ERROR_INCORRECT_OPTION_VALUE;
            return m_errorCode;
        }
    }

    CreateLogDirectory(camera.serial);

    AddLog("\nResult folder: " + this->m_dir);
    AddLog("\nSerial Number: " + camera.serial);
    AddLog("Device Name: " + camera.name);
    AddLog("Device PID:  " + camera.pid);
    AddLog("FW version:  " + camera.fw_ver);
    AddLog("USB Type:  " + camera.usb_type);

	if (m_loglevel > 0)
    {
        for (auto pf : camera.profiles)
        {
            auto video = pf.as<video_stream_profile>();
            cout << video.width() << " x " << video.height() << " @ " << video.fps() << ", " << pf.format() << endl;
        }
    }

    if (IsUsb2(camera))
    {
        m_errorCode = DC_ERROR_DEVICE_USB2;
        AddLog("\n" + rs_convert_err_to_string(m_errorCode));

        return m_errorCode;
    }

	switch (m_calibration_mode)
	{
	case 0:
		AddLog("\nCalibration Type: Targetless");
		break;

	case 1:
		AddLog("\nCalibration Type: Targeted");
		break;

	case 2:
		AddLog("\nCalibration Type: Hybrid");
		break;

	case 3:
		AddLog("\nCalibration Type: Scale Calibration Only");
		break;

	case 4:
		AddLog("\nCalibration Type: RGB Calibration Only");
		break;
	}


    if (camera.features & HAS_EMITTER)
    {
        if (m_useLaser)
            AddLog("Laser Power: On");
        else
            AddLog("Laser Power: Off");
    }

    if (m_autoExposureEnable)
    {
        AddLog("Auto Exposure: On");

        if (m_aesweepmode)
            AddLog("AE SetPoint: Auto");
        else
            AddLog("AE SetPoint: " + to_string(m_aeSetpoint));
    }
    else
    {
        AddLog("Auto Exposure: Off");
        AddLog("Depth Exposure: " + to_string(m_depthExposure));
        if (camera.features & SKU_RGB)
            AddLog("Color Exposure: " + to_string(m_colorExposure));
    }

	if (m_calibration_mode != 0)
	{
		AddLog("Target images: " + to_string(max_target_images));

		if (m_device_target_same_orientation)
			AddLog("Target and device orientation aligned: Yes");
		else
			AddLog("Target and device orientation aligned: No");

        if (m_skiprgb)
			AddLog("Skip rgb calibration: Yes");
		else
			AddLog("Skip rgb calibration: No");
	}

	if (m_calibration_mode == 0 || m_calibration_mode == 2)
	{
		if (m_ignore_borders)
			AddLog("Ignore borders: Yes");
		else
			AddLog("Ignore borders: No");
	}

    if (!IsFwVersionSupported(camera))
    {
        m_errorCode = DC_ERROR_FW_VERSION_OLD;
        AddLog("\n" + rs_convert_err_to_string(m_errorCode));

		std::string error_msg = "";
		stringstream stream;
		stream << "The minimum firmware version required for this device is " << camera.minFWVerMajor << "." << camera.minFWVerMinor << "." << camera.minFWVerPatch << "." << camera.minFWVerBuild << ". Please upgrade firmware and try again.\n";
		error_msg = stream.str();

		AddLog(error_msg);

        return m_errorCode;
    }

    if (m_timeout <= 0)
    {
        m_timeout = 180;
    }

	AddLog("Initializing GL ...");

    InitializeGL((void *)this);

	AddLog("Launching graphical view ...");

    glutIdleFunc([]() {
        MainView *pView = reinterpret_cast<MainView *>(glutGetWindowData());
        pView->OnIdle();
    });

    return DC_SUCCESS;
}

int CliView::UpdateCalibrationTablesComplete(std::string msg, bool bUpdated)
{
	int ret = DC_SUCCESS;

    m_captureManager->StopCapture();

    AddLog("\n" + msg);
    if ((m_cameras[m_devIdx].features & SKU_RGB) && m_targeted && !m_rgbCalib && !m_skiprgb)
    {
        AddLog("Scale calibration completed, start RGB calibration");

        std::this_thread::sleep_for(std::chrono::milliseconds(2000));
        m_rgbCalib = true;

		m_scaleCalibOnly = false;

		try
		{
			ret = StartCapture(m_devIdx);
		}
		catch (exception e)
		{
			AddLog("Failed starting RGB calibration");
		}

        return ret;
    }
	else if (m_hybrid)
	{
		m_targeted = true;
		m_scaleCalibOnly = true;

		try
		{
			ret = StartCapture(m_devIdx);
			m_hybrid = false;
		}
		catch (exception e)
		{
			AddLog("Failed starting scale calibration");
		}

		return ret;
	}

    if (bUpdated)
        AddLog("Calibration tables updated");
    else
    {
        AddLog("Calibration table update failed");
        m_errorCode = DC_ERROR_TABLE_WRITE_FAILED;
    }

    glutLeaveMainLoop();

	return ret;
}

/* Handling error message */
void CliView::ErrorHandling(int errorCode)
{
    if (m_CmdOptions.bGetRectErrorOnly && (errorCode == DC_ERROR_TIME_OUT))
        AddLog("\nRectification error reporting done.");
    else
        AddLog("\n" + rs_convert_err_to_string(errorCode));

    m_captureManager->StopCapture();
    glutLeaveMainLoop();
}

void CliView::OnDisplay()
{
    int ret = DC_SUCCESS;
    bool bDraw = true;

    glClearColor(0.1f, 0.1f, 0.15f, 1);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

    switch (m_runningStatus)
    {
    case STATUS_NOT_STARTED:
		try
		{
			ret = m_captureManager->InitializeCamera(m_cameras[m_devIdx].serial);
		}
		catch (exception e)
		{
			ret = false;
		}

        if (!ret) return;

		try
		{
			ret = StartCapture(m_devIdx);
		}
		catch (exception e)
		{
			ret = DC_ERROR_FAIL;
		}

        if (ret == DC_SUCCESS)
        {
            m_elapsedTime.Start();
            m_runningStatus = STATUS_RUNNING;
        }
        break;

    case STATUS_RUNNING:
        bDraw = m_captureManager->Render(m_winWidth, m_winHeight);
        if (m_elapsedTime.ElapsedSeconds() >= m_timeout)
        {
            m_errorCode = DC_ERROR_TIME_OUT;
            ErrorHandling(m_errorCode);
        }
        break;
    }

    if (ret != DC_SUCCESS)
        ErrorHandling(ret);

    if (bDraw) glutSwapBuffers();
    glutPostRedisplay();
}

void CliView::OnKeyBoard(unsigned char key, int x, int y)
{
    switch (tolower(key))
    {
    case 'q':
    case 27:      //ESC
        if (m_runningStatus == (int)STATUS_RUNNING)
        {
            m_captureManager->StopCapture();
        }
        AddLog("\nOperation terminated.");
        glutLeaveMainLoop();
        break;

	case 'c':
		m_captureManager->manual_capture = true;
		break;

    case 0x03:
    case 0x1C:
        Control_C_Handler(0);
        break;
    }
}

void CliView::Control_C_Handler(int)
{
    glutLeaveMainLoop();
}
