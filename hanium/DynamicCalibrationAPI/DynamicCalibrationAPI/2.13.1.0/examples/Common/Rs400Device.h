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

#include <functional>
#include <memory>       // For shared_ptr
#include <thread>
#include <mutex>

#include "librealsense2/rs.hpp"
#include "types.h"
#include "rs_utils.h"
#include "rs_hmc.h"

using namespace std;
using namespace rs2;

namespace devicewrapper
{
#define BUF_NUM 2

    enum RS_400_STREAM_TYPE
    {
        RS400_STREAM_INFRARED,
        RS400_STREAM_INFRARED2,
        RS400_STREAM_COLOR,
        RS400_STREAM_DEPTH,
        RS400_STREAM_COUNT
    };

    class Rs400Device
    {
    public:
        Rs400Device();
        virtual ~Rs400Device();

        std::vector<camera_info> ListCameras();
        bool InitializeCamera(std::string sn);
        void *GetDeviceHandle() { return (void *)&m_device; }

        bool SetMediaMode(int width, int height, int frameRate, int rgbWidth, int rgbHeight, int rgbFPS, bool enableDepth, bool enableLR, bool enableRgb, rs2_format ir_format = rs2_format::RS2_FORMAT_Y8);

        //If depth stream is enabled, otherImage will be depth image,
        //otherwise it will be right image
        void StartCapture(std::function<void(const void *leftImage, const void *rightImage, const void *colorImage, const void *depthImage, const uint64_t timeStamp)> callback);
        void StopCapture();

        void EnableAutoExposure(float value, bool bColor);
        void SetExposure(float value, bool bColor);
        float GetExposure(bool bColor);
        void GetExposureRange(int *rmin, int *rmax, bool bColor);
        void SetBrightness(float value, bool bColor);
        float GetBrightnessRange(int *rmin, int *rmax, int *rdef, bool bColor);
        void SetGain(float value, bool bColor);
        float GetGainRange(int *rmin, int *rmax, int *rdef, bool bColor);
        void EnableEmitter(float value);
        void SetAeControl(unsigned int point);
        void SetROI(int ExposureTopEdge, int ExposureBottomEdge, int ExposureLeftEdge, int ExposureRightEdge);

        void SetThermalCompensation(float value);
        float GetThermalCompensation();

        bool HwMonitorCmd_Get(uint8_t* cmd, uint8_t* data, int length);
        bool HwMonitorCmd_Set(uint8_t* cmd, uint8_t* data, int length);

		camera_info Get_Active_CameraInfo() { return active_camera; };
        std::string GetDevicePID();
        bool SupportsRGB();

        template<class T>
        void SetDevicesChangedCallback(T callback)
        {
            m_context.set_devices_changed_callback(callback);
        }

        bool Is_USB2() { return active_camera.Is_USB2(); }
        bool Is_USB3() { return active_camera.Is_USB3(); }
        bool Is_MIPI() { return active_camera.Is_MIPI(); }

    private:
        bool GetProfile(rs2::stream_profile& profile, rs2_stream stream, rs2_format format, int width, int height, int fps, int index);
        void ProcessFrame();
        int  GetDepthSensor(rs2::device* dev);
        int  GetColorSensor(rs2::device* dev);
        void HwReset();

    private:
        rs2::context m_context;
        rs2::device m_device;
        rs2::sensor m_depthSensor;
        rs2::sensor m_colorSensor;
        rs2::pipeline pipe;

        std::function<void(const void *leftImage, const void *rightImage, const void *colorImage, const void *depthImage, const uint64_t timeStamp)> m_callback;

        std::vector<rs2::stream_profile> m_depthProfiles;
        std::vector<rs2::stream_profile> m_colorProfiles;

        std::unique_ptr<uint8_t[]> m_leftImage[BUF_NUM];
        std::unique_ptr<uint8_t[]> m_rightImage[BUF_NUM];
        std::unique_ptr<uint16_t[]> m_mainImage[BUF_NUM];
        std::unique_ptr<uint16_t[]> m_depthImage[BUF_NUM];

        int  m_bufIdx;
        uint64_t m_bufLocked[BUF_NUM];

        void *m_pData[RS400_STREAM_COUNT][BUF_NUM];
        uint64_t m_timestamp[RS400_STREAM_COUNT][BUF_NUM];
        uint64_t m_ts;
        int m_timestampShift;

#ifdef _WIN32
        CRITICAL_SECTION m_mutex;
#else
        pthread_mutex_t  m_mutex;
#endif

        std::thread m_thread;
        bool m_stopProcessFrame;
        int  m_frameProcessIdx;
        bool m_frameProcessInWait;
#ifdef _WIN32
        CRITICAL_SECTION m_buf_mutex;
        CONDITION_VARIABLE m_buf_mutex_cv;
#else
        pthread_mutex_t  m_buf_mutex;
        pthread_cond_t m_buf_mutex_cv;
#endif

        bool m_captureStarted;
        bool m_bDepthEnabled;
        bool m_bRgbEnabled;
        bool m_bLrEnabled;
        int  m_fps_lr;
        int  m_fps_rgb;

        camera_info active_camera;
    };
}

