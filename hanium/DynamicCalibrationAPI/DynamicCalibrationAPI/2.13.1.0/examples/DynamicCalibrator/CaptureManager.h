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

#include <vector>
#include "Rs400Device.h"
#include "ProcessDynCalibration.h"

using namespace devicewrapper;

namespace DynamicCalibrator
{
    enum SAVE_FRAME_FLAG {
        SAVE_FRAME_NONE = 0,
        SAVE_FRAME_ACCEPTED = 1,
        SAVE_FRAME_ALL = 2
    };

    class MainView;

    class CaptureManager
    {
    public:
        CaptureManager(int loglevel = 0) : CaptureManager((MainView*)nullptr, false, false) { m_loglevel = loglevel; }
        CaptureManager(MainView* view, int saveFrame, bool bGetRectErrorOnly = false, int loglevel = 0);

        virtual ~CaptureManager();

        std::vector<camera_info> ListCameras();

        bool InitializeCamera(std::string serialNumber);
        void *GetRs400DeviceHandle();

        int StartCapture(int width, int height, int fps, DSDynamicCalibration::CalibrationMode mode,
            bool bLaserPower, int aePoint, int sku, int sweep, bool aligned, int max_num_images, bool ignore_borders, int rgbwidth, int rgbheight, int rgbfps);

        void StopCapture();

        void StopDevice();

        void EnableAutoExposure(float value);
        void SetExposure(int value, bool bColor);

        void SetBrightness(int value, bool bColor);
        int GetBrightnessRange(int *rmin, int *rmax, int *rdef, bool bColor);

        void SetAeControl(unsigned int point);
		void SetSweepMode(int sweep);

        void SetROI(int ExposureTopEdge, int ExposureBottomEdge,
            int ExposureLeftEdge, int ExposureRightEdge);

        void* OnIdle();
        bool Render(int winWidth, int winHeight);

        template<class T>
        void SetDevicesChangedCallback(T callback)
        {
            m_rsDevice.SetDevicesChangedCallback(callback);
        }

		bool manual_capture;

    private:
        MainView* m_view;
		devicewrapper::Rs400Device m_rsDevice;
        ProcessDynCalib *m_dynCal;

        bool m_captureStarted;
        int  m_saveFrame;
        bool m_bGetRectErrorOnly;
        bool m_autoExposure;

        bool m_restore;
        uint8_t m_dtc[20];

        bool m_restore_tc;
        float m_thermal_compensation;

        int m_loglevel;
    };

}
