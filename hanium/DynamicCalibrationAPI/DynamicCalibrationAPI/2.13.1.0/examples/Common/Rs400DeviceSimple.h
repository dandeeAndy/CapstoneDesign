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

namespace devicewrapper
{
    class Rs400DeviceSimple
    {
    public:
        Rs400DeviceSimple();
        virtual ~Rs400DeviceSimple() {};

        std::vector<camera_info> ListCameras();
        bool InitializeCamera(std::string sn);
        void *GetDeviceHandle() { return (void *)&m_device; }

        bool supports_rgb_on_left() {
            string pid = m_cameraInfo.pid;
            // Intel RealSense Depth Camera D405 color stream from left sensor
            if (pid.compare("0B5B") == 0)
                return true;
            else
                return false;
        }

        bool Is_MIPI();
		camera_info Get_Active_CameraInfo() { return m_cameraInfo; };

    private:
        int  GetDepthSensor(rs2::device* dev);
        int  GetColorSensor(rs2::device* dev);

        rs2::context m_context;
        rs2::device m_device;
        rs2::sensor m_depthSensor;
        rs2::sensor m_colorSensor;
        camera_info m_cameraInfo;
    };
}

