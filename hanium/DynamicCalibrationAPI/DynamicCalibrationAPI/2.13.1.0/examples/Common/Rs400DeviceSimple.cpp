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

#ifndef _WIN32
#include <dirent.h>
#else
#include <process.h>
#endif

#include "string"
#include "Rs400DeviceSimple.h"
#include "librealsense2/rs_advanced_mode.hpp"

using namespace std;
using namespace devicewrapper;
using namespace rs2;
using namespace rs400;

Rs400DeviceSimple::Rs400DeviceSimple()
{
    m_depthSensor = NULL;
    m_colorSensor = NULL;
    m_cameraInfo = {};
}

vector<camera_info> Rs400DeviceSimple::ListCameras()
{
    vector<camera_info> cameras;
    auto devices = m_context.query_devices();

    for (int i = 0; i < (int)devices.size(); i++)
    {
        camera_info info{};
        auto dev = devices[i];

        info.name = dev.get_info(rs2_camera_info::RS2_CAMERA_INFO_NAME);
        // filter out non RS400 camera
        if (info.name.find("RealSense") == string::npos || info.name.find("4") == string::npos) continue;

        info.pid = to_upper(dev.get_info(rs2_camera_info::RS2_CAMERA_INFO_PRODUCT_ID));
        info.physical_port = dev.get_info(rs2_camera_info::RS2_CAMERA_INFO_PHYSICAL_PORT);
        info.serial = dev.get_info(rs2_camera_info::RS2_CAMERA_INFO_SERIAL_NUMBER);
        info.fw_ver = dev.get_info(rs2_camera_info::RS2_CAMERA_INFO_FIRMWARE_VERSION);

        if (info.pid.compare("ABCD") == 0) // D457 MIPI device
        {
            info.usb_type = "MIPI";
        }
        else // USB devices
        {
            info.usb_type = dev.get_info(RS2_CAMERA_INFO_USB_TYPE_DESCRIPTOR);
        }

        info.features = 0x0;

        int idx = GetDepthSensor(&dev);
        if (idx < 0) continue;

        auto sensors = dev.query_sensors();

        if (sensors[idx].supports(rs2_option::RS2_OPTION_LASER_POWER))
            info.features |= HAS_EMITTER;

        std::vector<uint8_t> RawBuffer =
        { 0x14, 0, 0xab, 0xcd, 0x10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };

        std::vector<uint8_t> rcvBuf;

		try {
			auto debug = dev.as<debug_protocol>();;
			rcvBuf = debug.send_and_receive_raw_data(RawBuffer);
		}
		catch (exception e)
		{
			continue;
		}

        if ((rcvBuf[SKU_COMPONENT] & 0x0f) == 2)
            info.features |= SKU_WIDE;

        if (rcvBuf[DEPTH_ACTIVE_MODE] == 0)
            info.features |= SKU_PASSIVE;

		m_depthSensor = sensors[idx];

		int colorSensorIdx = GetColorSensor(&dev);
		if (colorSensorIdx > 0)
		{
			m_colorSensor = sensors[colorSensorIdx];
			info.features |= SKU_RGB;
		}

		if (colorSensorIdx > 0)
			info.features |= SKU_RGB;

		info.minFWVerMajor = REQUIRED_MINIMUM_FW_MAJOR_VERSION;
		info.minFWVerMinor = REQUIRED_MINIMUM_FW_MINOR_VERSION;
		info.minFWVerPatch = REQUIRED_MINIMUM_FW_PATCH_VERSION;
		info.minFWVerBuild = REQUIRED_MINIMUM_FW_BUILD_VERSION;

		if (info.features & SKU_RGB)
		{
			info.minFWVerMinor = RGB_REQUIRED_MINIMUM_FW_MINOR_VERSION;
			info.minFWVerPatch = RGB_REQUIRED_MINIMUM_FW_PATCH_VERSION;
		}

        cameras.push_back(info);
    }

    return cameras;
}

bool Rs400DeviceSimple::InitializeCamera(string sn)
{
    int idx = 0;

    vector<camera_info> cameras = ListCameras();
    if (cameras.size() == 0) return false;

    if (!sn.empty())
    {
        idx = -1;
        for (int i = 0; i < (int)cameras.size(); i++)
        {
            if (cameras[i].serial == sn)
            {
                idx = i;
                break;
            }
        }

        if (idx == -1) return false;
    }

    m_cameraInfo = cameras[idx];

    auto devices = m_context.query_devices();
    m_device = devices[idx];
    int depSensorIdx = GetDepthSensor(&m_device);
    if (depSensorIdx < 0) return false;

    m_device = devices[idx];
    auto sensors = devices[idx].query_sensors();
    m_depthSensor = sensors[depSensorIdx];

    return true;
}

int Rs400DeviceSimple::GetDepthSensor(device* dev)
{
	auto sensors = dev->query_sensors();

	for (int i = 0; i < (int)sensors.size(); i++)
	{
		if (sensors[i].supports(rs2_option::RS2_OPTION_DEPTH_UNITS))
			return i;
	}

	return -1;
}

int Rs400DeviceSimple::GetColorSensor(device* dev)
{
	auto sensors = dev->query_sensors();

	for (int i = 0; i < (int)sensors.size(); i++)
	{
		if (sensors[i].supports(rs2_option::RS2_OPTION_CONTRAST))
			return i;
	}

	return -1;
}

bool Rs400DeviceSimple::Is_MIPI()
{
    std::string port = m_cameraInfo.physical_port;
    if ((port.find("vid_8086") != string::npos) || (port.find("usb") != string::npos)) // usb devices
        return false;
    else
        return true;
}
