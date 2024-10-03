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
#include <sstream>
#include <iostream>
#include <thread>

#include "CaptureManager.h"
#include "DSDynamicCalibration.h"
#include "MainView.h"
#include "rs_utils.h"
#include "rs_hmc.h"

using namespace std;
using namespace DynamicCalibrator;
using namespace DynamicCalibrationAPI;
using namespace devicewrapper;

CaptureManager::CaptureManager(MainView* view, int SaveFrame, bool bGetRectErrorOnly, int loglevel)
{
    m_view = view;
    m_bGetRectErrorOnly = bGetRectErrorOnly;
    m_autoExposure = false;

    m_captureStarted = false;

    m_dynCal = nullptr;

    m_saveFrame = 0;
    if (SaveFrame >= 0)
    {
        if (SaveFrame == 0)
            m_saveFrame = SAVE_FRAME_ACCEPTED;
        else
            m_saveFrame = SAVE_FRAME_ALL;
    }

    manual_capture = false;
    m_restore = false;

    m_restore_tc = false;
    m_thermal_compensation = -1.0;

    m_loglevel = loglevel;
}

CaptureManager::~CaptureManager()
{
}

std::vector<camera_info> CaptureManager::ListCameras()
{
    std::vector<camera_info> cameras;
    cameras = m_rsDevice.ListCameras();

    return cameras;
}

bool CaptureManager::InitializeCamera(string serialNumber)
{
    bool rt = m_rsDevice.InitializeCamera(serialNumber);

    if (m_dynCal) delete m_dynCal;

    m_dynCal = new ProcessDynCalib(m_view, this, m_saveFrame, m_bGetRectErrorOnly);

    return rt;
}

void *CaptureManager::GetRs400DeviceHandle()
{
    return m_rsDevice.GetDeviceHandle();
}

int CaptureManager::StartCapture(int width, int height, int fps, DSDynamicCalibration::CalibrationMode mode,
    bool bLaserPower, int aePoint, int sku, int sweep, bool aligned, int max_num_images, bool ignore_borders, int rgbwidth, int rgbheight, int rgbfps)
{
    if (m_captureStarted) return DC_SUCCESS;
    bool bEnableDepth = (mode == DSDynamicCalibration::CalibrationMode::CAL_MODE_INTEL_TARGETED || mode == DSDynamicCalibration::CalibrationMode::CAL_MODE_INTEL_TARGETED_SCALE_ONLY) ? true : false;
    bool bEnableRgb = (mode == DSDynamicCalibration::CalibrationMode::CAL_MODE_INTEL_RGB_CALIB) ? true : false;

	if (m_loglevel > 0)
	{
		cout << "start capture ..." << endl;
	}

	if (!m_rsDevice.SupportsRGB() && bEnableRgb)
	return DC_ERROR_RGB_NOT_SUPPORTED_ON_DEVICE;

    m_captureStarted = true;
    float emitterVal = bLaserPower == true ? 1.0f : 0.0f;

	try {
		m_rsDevice.EnableEmitter(emitterVal);
	}
	catch (...)
	{
	}

    string pid = to_upper(m_rsDevice.GetDevicePID());

    // thermal compensation on D455/D450 USB devices and D457 MIPI devices
    if (pid.compare("0B5C") == 0 || pid.compare("ABCD") == 0)
    {
        try {
            m_thermal_compensation = m_rsDevice.GetThermalCompensation();

            if (m_loglevel > 0)
            {
                cout << "thermal compensation mode: " << m_thermal_compensation << endl;
            }

            m_rsDevice.SetThermalCompensation(0.0);
            float tc = m_rsDevice.GetThermalCompensation();

            if (m_loglevel > 0)
            {
                cout << "thermal compensation mode after disable: " << tc << endl;
            }

            m_restore_tc = true;
        }
        catch (...)
        {
        }
    }

	if (m_loglevel > 0)
	{
		cout << "reading depth table control." << endl;
	}

	uint8_t dcrcvBuf[20];
	m_rsDevice.HwMonitorCmd_Get(AMCGET, dcrcvBuf, 20);

	DepthTableControl *pDTC = (DepthTableControl*)dcrcvBuf;

	if (m_loglevel > 0)
	{
		cout << dump_buffer_to_console(dcrcvBuf, sizeof(dcrcvBuf));

		cout << pDTC->depthUnits << endl;
		cout << pDTC->depthClampMin << endl;
		cout << pDTC->depthClampMax << endl;
		cout << pDTC->disparityMode << endl;
		cout << pDTC->disparityShift << endl;
	}
	
    if (pid.compare("0B4D") == 0 || pid.compare("0B5B") == 0 )
    {
        // save DTC settings
        DS_MEMCPY(m_dtc, dcrcvBuf, sizeof(dcrcvBuf));

        if (m_loglevel > 0)
        {
            cout << "setting depth table control ..." << endl;
        }

        if (pid.compare("0B4D") == 0)
        {
            pDTC->disparityShift = 120;
        }
        else if (pid.compare("0B5B") == 0)
        {
            pDTC->depthUnits = 1000;
        }

        m_rsDevice.HwMonitorCmd_Set(AMCSET, dcrcvBuf, 20);
        m_rsDevice.HwMonitorCmd_Get(AMCGET, dcrcvBuf, 20);

        m_restore = true;

        pDTC = (DepthTableControl*)dcrcvBuf;

        if (m_loglevel > 0)
        {
			cout << dump_buffer_to_console(dcrcvBuf, sizeof(dcrcvBuf));

			cout << pDTC->depthUnits << endl;
			cout << pDTC->depthClampMin << endl;
			cout << pDTC->depthClampMax << endl;
			cout << pDTC->disparityMode << endl;
			cout << pDTC->disparityShift << endl;
        }
	}

    if (m_loglevel > 0)
    {
        cout << "setting up media mode: depth=" << bEnableDepth << ", rgb=" << bEnableRgb << endl;
    }


    if (!m_rsDevice.SetMediaMode(width, height, fps, rgbwidth, rgbheight,fps, bEnableDepth, true, bEnableRgb))
    return DC_ERROR_SET_STREAMING_MEDIA_MODE_FAILED;

    int ret = m_dynCal->InitDynCalParams(width, height, mode, rgbwidth, rgbheight, m_autoExposure, aePoint, sku, sweep, aligned, bLaserPower, max_num_images, ignore_borders, m_loglevel);

    if (ret == DC_SUCCESS)
    {
        ProcessDynCalib *dynCal = m_dynCal;
        m_rsDevice.StartCapture([dynCal](const void *leftImage, const void *rightImage, const void *colorImage, const void *depthImage, const uint64_t timeStamp) {
            const void *mImage = (depthImage != NULL) ? depthImage : colorImage;
            dynCal->ProcessFrames(leftImage, rightImage, mImage, timeStamp);
        });
    }

    return ret;
}

void CaptureManager::StopCapture()
{
    if (!m_captureStarted) return;

    m_captureStarted = false;

	try
	{
        m_rsDevice.StopCapture();
        if (m_dynCal) m_dynCal->StopProcessing();

        try {
            m_rsDevice.EnableEmitter(1.0);
	} catch (...) {}

        if (m_restore_tc)
        {
            if (m_thermal_compensation >= 0.0)
            {
               m_rsDevice.SetThermalCompensation(m_thermal_compensation);
               m_thermal_compensation = -1.0;
            }

            m_restore_tc = false;

            float tc = m_rsDevice.GetThermalCompensation();

            if (m_loglevel > 0)
            {
                cout << "thermal compensation mode after restore: " << tc << endl;
            }
        }

        if (m_restore)
        {
            m_rsDevice.HwMonitorCmd_Set(AMCSET, m_dtc, 20);
            m_rsDevice.HwMonitorCmd_Get(AMCGET, m_dtc, 20);

            DepthTableControl* pDTC = (DepthTableControl*) m_dtc;

           if (m_loglevel > 0)
           {
               cout << "restoring depth table control settings ..." << endl;
               cout << dump_buffer_to_console(m_dtc, sizeof(m_dtc));

               cout << pDTC->depthUnits << endl;
               cout << pDTC->depthClampMin << endl;
               cout << pDTC->depthClampMax << endl;
               cout << pDTC->disparityMode << endl;
               cout << pDTC->disparityShift << endl;
           }

           m_restore = false;
        }
    }
    catch (...)
    { }
}

void CaptureManager::StopDevice()
{
    try
    {
        m_rsDevice.StopCapture();
    }
    catch (...)
    { }
}

void CaptureManager::EnableAutoExposure(float value)
{
    try
    {
        m_rsDevice.EnableAutoExposure(value, false);
        m_rsDevice.EnableAutoExposure(value, true);
        m_autoExposure = (value == 0.0f) ? false : true;
    }
    catch (...)
    { }
}

void CaptureManager::SetExposure(int value, bool bColor)
{
    m_rsDevice.SetExposure((float)value, bColor);
}

void CaptureManager::SetBrightness(int value, bool bColor)
{
    try
    {
        m_rsDevice.SetBrightness((float)value, bColor);
    }
    catch (...)
    { }
}

int CaptureManager::GetBrightnessRange(int *rmin, int *rmax, int *rdef, bool bColor)
{
    return (int)m_rsDevice.GetBrightnessRange(rmin, rmax, rdef, bColor);
}

void CaptureManager::SetAeControl(unsigned int point)
{
    if (!m_autoExposure) return;

    m_rsDevice.SetAeControl(point);
}

void CaptureManager::SetSweepMode(int sweep)
{
	if (nullptr == m_dynCal) return;

	m_dynCal->SetSweepMode(sweep);
}

void CaptureManager::SetROI(int ExposureTopEdge, int ExposureBottomEdge,
    int ExposureLeftEdge, int ExposureRightEdge)
{
	if (!m_autoExposure) return;

    try
    {
        m_rsDevice.SetROI(ExposureTopEdge, ExposureBottomEdge, ExposureLeftEdge, ExposureRightEdge);
    }
    catch (...)
    { }
}

void* CaptureManager::OnIdle()
{
    if (m_dynCal && m_captureStarted)
    {
        return m_dynCal->OnIdle();
    }
    else
    {
        return nullptr;
    }
}

bool CaptureManager::Render(int winWidth, int winHeight)
{
    if (!m_captureStarted
        || (nullptr == m_dynCal)
        )
    {
        return false;
    }

    return m_dynCal->Render(winWidth, winHeight);
}
