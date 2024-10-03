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

#ifndef _D400_CALIBRATION_COMMON_H_
#define _D400_CALIBRATION_COMMON_H_

#pragma once

#ifdef _WIN32
#include <Windows.h>
#else
#include <pthread.h>
#endif

#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include <algorithm>

#include "librealsense2/rs.hpp"

using namespace std;
using namespace rs2;


#ifdef _WIN32
#define MUTEX_LOCK      EnterCriticalSection
#define MUTEX_UNLOCK    LeaveCriticalSection
#define COND_SIGNAL     WakeConditionVariable

#define LOCKED_EXCHANGE InterlockedExchange
#define LOCKED_EXCHANGE_ADD InterlockedExchangeAdd
#else
#define MUTEX_LOCK(m)    if (0 != pthread_mutex_lock(m)) throw std::runtime_error ("pthread_mutex_lock failed")
#define MUTEX_UNLOCK(m)  if (0 != pthread_mutex_unlock(m)) throw std::runtime_error ("pthread_mutex_unlock failed")
#define COND_SIGNAL(c)  (void) pthread_cond_signal(c)

#define LOCKED_EXCHANGE __sync_lock_test_and_set
#define LOCKED_EXCHANGE_ADD __sync_fetch_and_add
#endif

namespace devicewrapper
{
// target-less calibration is disabled by default in the app gui
//#define ENABLE_TARGETLESS_CALIBRATION_IN_GUI

    // minimum required FW version in the format of 5.REQUIRED_MINIMUM_FW_MINOR_VERSION.REQUIRED_MINIMUM_FW_PATCH_VERSION

    // for example, 5.10.6.0
    const int REQUIRED_MINIMUM_FW_MAJOR_VERSION = 5;
    const int REQUIRED_MINIMUM_FW_MINOR_VERSION = 10;
    const int REQUIRED_MINIMUM_FW_PATCH_VERSION = 6;
    const int REQUIRED_MINIMUM_FW_BUILD_VERSION = 0;

	// for devices with RGB, for example, D415 and D435, the minimum required FW
    const int RGB_REQUIRED_MINIMUM_FW_MINOR_VERSION = REQUIRED_MINIMUM_FW_MINOR_VERSION;
    const int RGB_REQUIRED_MINIMUM_FW_PATCH_VERSION = REQUIRED_MINIMUM_FW_PATCH_VERSION;

    enum GVD_FIELDS
    {
        PRODUCT_ID_OFFSET = 4,
        SKU_COMPONENT = 162,
        DEPTH_ACTIVE_MODE = 170,
        RGB_MODE = 174,
        IMU_SENSOR = 178,
        PROJECTOR_TYPE = 182,
        EEPROM_LOCK_STATUS = 228,
    };

    enum RS400_FEATURES
    {
        SKU_PASSIVE = 0x01,
        SKU_WIDE    = 0x02,
        SKU_RGB	= 0x04,
        HAS_EMITTER = 0x10,
        EEPROM_LOCKED = 0x20,
        SKU_IMU     = 0x40,
        SKU_LED       = 0x80,
        SKU_MIPI      = 0x100,
        SKU_D431      = 0x200,
        SKU_F416_USB2 = 0x400,
    };

    class camera_info
    {
    public:
        std::string name;
        std::string module;
        std::string serial;
        std::string fw_ver;
        std::string pid;
        std::string physical_port;
        std::string usb_type;
        std::vector<rs2::stream_profile> profiles;
        int features;
        int depthExposure;
        int depthExposureMin;
        int depthExposureMax;
        int colorExposure;
        int colorExposureMin;
        int colorExposureMax;

        int  depthSetpoint;
        int  depthSetpointMin;
        int  depthSetpointMax;
        int  depthSetpointDefault;

        int  rgbBrightness;
        int  rgbBrightnessMin;
        int  rgbBrightnessMax;
        int  rgbBrightnessDefault;

        int minFWVerMajor;
        int minFWVerMinor;
        int minFWVerPatch;
        int minFWVerBuild;
        int productid;

        bool operator () (const camera_info& l) const
        {
            return serial == l.serial;
        }

        bool operator < (const camera_info& l) const
        {
            return serial < l.serial;
        }

        bool Is_MIPI() { return (usb_type.find("MIPI") != string::npos); }
        bool Is_USB2() { return (usb_type.find("2") == 0); }
        bool Is_USB3() { return (usb_type.find("3") == 0); }
    };
}
#endif
