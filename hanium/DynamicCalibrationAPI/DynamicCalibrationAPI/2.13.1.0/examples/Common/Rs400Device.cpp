/*
**********************************************************************************************************
*                                                                                                       **
* INTEL CONFIDENTIAL                                                                                    **
* Copyright (2018 - 2020) Intel Corporation.                                                            **
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
#include <iomanip>
#include <iostream>
#include <sstream>
#include <thread>
#include "Rs400Device.h"
#include "librealsense2/rs_advanced_mode.hpp"

#include <iostream>
#include <fstream>

using namespace std;
using namespace rs2;
using namespace rs400;
using namespace devicewrapper;

#define __D400_USE_LIBREALSENSE__

#if 0
#define  LOG(...)  { std::ostringstream ss; ss << __VA_ARGS__; cout << ss.str() << endl; }
#else
#define  LOG(...)  {}
#endif

struct y12i_pixel {
    uint8_t rl : 8, rh : 4, ll : 4, lh : 8;
int l() const { return lh << 4 | ll; } int r() const { return rh << 8 | rl; } };

Rs400Device::Rs400Device()
{
    m_captureStarted = false;
    m_bufIdx = 0;
    m_frameProcessIdx = 0;
    m_frameProcessInWait = false;
    m_stopProcessFrame = true;
	m_depthProfiles.clear();
	m_colorProfiles.clear();

	m_depthSensor = NULL;
	m_colorSensor = NULL;

    for (uint32_t i = 0; i < RS400_STREAM_COUNT; i++)
    {
        for (int j = 0; j < BUF_NUM; j++)
        {
            m_timestamp[i][j] = 0;
            m_pData[i][j] = nullptr;
        }
    }

    m_ts = 0;
    m_timestampShift = -1;

#ifdef _WIN32
    InitializeCriticalSection(&m_mutex);
    InitializeCriticalSection(&m_buf_mutex);
    InitializeConditionVariable(&m_buf_mutex_cv);
#else
    if (0 != pthread_mutex_init(&m_mutex, NULL)) throw std::runtime_error("pthread_mutex_init failed");
    if (0 != pthread_mutex_init(&m_buf_mutex, NULL)) throw std::runtime_error("pthread_mutex_init failed");
    if (0 != pthread_cond_init(&m_buf_mutex_cv, NULL)) throw std::runtime_error("pthread_cond_init failed");
#endif
    m_bDepthEnabled = false;
    m_bLrEnabled = false;
    m_bRgbEnabled = false;

    m_fps_lr = 0;
    m_fps_rgb = 0;

    active_camera = {};
}

Rs400Device::~Rs400Device()
{
#ifndef _WIN32
    if (0 != pthread_mutex_destroy(&m_mutex)) throw std::runtime_error("pthread_mutex_destroy failed");
    if (0 != pthread_mutex_destroy(&m_buf_mutex)) throw std::runtime_error("pthread_mutex_destroy failed");
#endif

    m_depthProfiles.clear();
    m_colorProfiles.clear();
}

vector<camera_info> Rs400Device::ListCameras()
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

        info.profiles.clear();

        for (auto s : sensors)
        {
            vector<stream_profile> pfs = s.get_stream_profiles();

            for (auto p : pfs)
                info.profiles.push_back(p);
        }

        if (sensors[idx].supports(rs2_option::RS2_OPTION_LASER_POWER))
            info.features |= HAS_EMITTER;

///        if (sensors[idx].supports(rs2_option::RS2_OPTION_LED_ENABLED))
///            info.features |= SKU_LED;

        m_device = dev;

        uint8_t rcvBuf[1024];
        HwMonitorCmd_Get(gvd_cmd, rcvBuf, 1024);

        if (rcvBuf[PROJECTOR_TYPE] & 0x01)
            info.features |= SKU_WIDE;

        if (rcvBuf[DEPTH_ACTIVE_MODE] == 0)
            info.features |= SKU_PASSIVE;

        if (rcvBuf[RGB_MODE] & 0x01)
            info.features |= SKU_RGB;

        if (rcvBuf[IMU_SENSOR] & 0x01)
            info.features |= SKU_IMU;

        if (rcvBuf[EEPROM_LOCK_STATUS] & 0x01)
            info.features |= EEPROM_LOCKED;

// PID taken F416 RGB
//		if (info.pid.compare("0B52") == 0 || info.pid.compare("0b52") == 0)
//		{
//			info.features |= SKU_F416_USB2;
//		}

//		if (info.pid.compare("0B4F") == 0 || info.pid.compare("0b4f") == 0)
//		{
//			info.features |= SKU_D431;
//		}

        info.productid = rcvBuf[PRODUCT_ID_OFFSET];

        if (info.productid == 0x11)
            info.features |= SKU_D431;

        m_depthSensor = sensors[idx];

        int colorSensorIdx = -1;
        if (info.pid.compare("0B5B") != 0)
        {
            colorSensorIdx = GetColorSensor(&dev);
        }

        if (colorSensorIdx > 0)
        {
            LOG("ListCameras RGB detected " << colorSensorIdx);
            m_colorSensor = sensors[colorSensorIdx];
            info.features |= SKU_RGB;
        }

        LOG("ListCameras RGB sensor index " << colorSensorIdx);
        LOG("RGB sensor index:" << colorSensorIdx);

        GetExposureRange(&info.depthExposureMin, &info.depthExposureMax, false);
        info.depthExposure = (int) GetExposure(false);

        info.depthSetpoint = 1000;
        info.depthSetpointMin = 0;
        info.depthSetpointMax = 4095;
        info.depthSetpointDefault = 1000;

        if (info.features & SKU_RGB)
        {
            if (info.physical_port.find("vid_8086") != string::npos) // USB devices
            {
                GetExposureRange(&info.colorExposureMin, &info.colorExposureMax, true);
                info.colorExposure = (int) GetExposure(true);
                info.rgbBrightness = (int) GetBrightnessRange(&info.rgbBrightnessMin, &info.rgbBrightnessMax, &info.rgbBrightnessDefault, true);
            }
        }

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

bool Rs400Device::InitializeCamera(string sn)
{
    LOG("Initializing camera " << sn);
    int idx = 0;
    camera_info info{};
    active_camera = {};

    vector<camera_info> cameras = ListCameras();

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

    info = cameras[idx];

    auto devices = m_context.query_devices();
    m_device = devices[idx];

    int depSensorIdx = GetDepthSensor(&m_device);
    if (depSensorIdx < 0) return false;

    auto sensors = devices[idx].query_sensors();
    m_depthSensor = sensors[depSensorIdx];

    int colorSensorIdx = -1;
    if (info.pid.compare("0B5B") != 0)    // no dedicated rgb sensro for D405
    {
        colorSensorIdx = GetColorSensor(&m_device);
    }

    if (colorSensorIdx > 0)
    {
        m_colorSensor = sensors[colorSensorIdx];

        vector<stream_profile> pfs = m_colorSensor.get_stream_profiles();
        for (auto pf : pfs)
        {
            auto video = pf.as<video_stream_profile>();
            LOG("Initialize rgb::" << video.width() << " x " << video.height() << " @ " << video.fps() << ", " << pf.format());
        }
    }

    std::string pid = cameras[idx].pid;
    active_camera = info;
    return !info.name.empty();
}

bool Rs400Device::SetMediaMode(int width, int height, int frameRate, int rgbWidth, int rgbHeight, int rgbFPS, bool enableDepth, bool enableLR, bool enableRgb, rs2_format ir_format)
{
    LOG("SetMediaMode:: SN:" << active_camera.serial << "Profile: " << width << "," << height << "," << frameRate << "rgb:" << rgbWidth <<"," << rgbHeight << "," << rgbFPS << ", enableDepth=" << enableDepth << "enableLR="<<enableLR << ",enableRgb=" << enableRgb << ", IRformat=" << ir_format);

    m_bDepthEnabled = enableDepth;
    m_bLrEnabled = enableLR;
    m_bRgbEnabled = enableRgb;
    m_fps_lr = frameRate;
    m_fps_rgb = rgbFPS;

    m_depthProfiles.clear();
    m_colorProfiles.clear();

    int size = 0;
    rs2_format format;

    if (m_bLrEnabled)
    {
        //Enable Y8/Y16 format for Left
        stream_profile infraredProfile;
        format = ir_format;
        if (!GetProfile(infraredProfile, rs2_stream::RS2_STREAM_INFRARED, format, width, height, m_fps_lr, 1)) return false;

        m_depthProfiles.push_back(infraredProfile);

        //Enable Y8/Y16 format for Right
        stream_profile infraredProfile2;
        if (!GetProfile(infraredProfile2, rs2_stream::RS2_STREAM_INFRARED, format, width, height, m_fps_lr, 2)) return false;

        m_depthProfiles.push_back(infraredProfile2);

        size = width * (height + 1);

        if (infraredProfile.format() == rs2_format::RS2_FORMAT_Y16)
            size *= 2;
    }

    if (enableDepth)
    {
        stream_profile depthProfile;
        format = rs2_format::RS2_FORMAT_Z16;
        if (!GetProfile(depthProfile, rs2_stream::RS2_STREAM_DEPTH, format, width, height, m_fps_lr, 0)) return false;

        m_depthProfiles.push_back(depthProfile);
    }

    if (enableRgb)
    {
        stream_profile profile;
        format = rs2_format::RS2_FORMAT_YUYV;

        LOG("SetMediaMode:: rgb" << rgbWidth << "x" << rgbHeight << "@" << m_fps_rgb);
        if (!GetProfile(profile, rs2_stream::RS2_STREAM_COLOR, format, rgbWidth, rgbHeight, m_fps_rgb, 0)) return false;

        auto video = profile.as<video_stream_profile>();
        LOG("RGB profile::" << video.width() << " x " << video.height() << " @ " << video.fps() << "," << profile.format());
        m_colorProfiles.push_back(profile);
    }

    for (int i = 0; i < BUF_NUM; i++)
    {
        if (m_bLrEnabled)
        {
            m_leftImage[i] = std::unique_ptr<uint8_t[]>(new uint8_t[size]);
            m_rightImage[i] = std::unique_ptr<uint8_t[]>(new uint8_t[size]);
        }

        if (enableRgb)
        {
            m_mainImage[i] = std::unique_ptr<uint16_t[]>(new uint16_t[rgbWidth*rgbHeight]);
        }

        if (enableDepth)
        {
            m_depthImage[i] = std::unique_ptr<uint16_t[]>(new uint16_t[width*height]);
        }

        m_bufLocked[i] = 0;
    }

    m_bufIdx = 0;

    return true;
}

void Rs400Device::StartCapture(std::function<void(const void *leftImage, const void *rightImage,
    const void *mainImage, const void *depthImage, const uint64_t timeStamp)> callback)
{
    m_callback = callback;

    if (!m_callback)
        throw std::runtime_error("SetCallback() must be called before StartCapture()!");

    if (m_depthProfiles.size() == 0)
        throw std::runtime_error("SetMediaMode() must be called before StartCapture()!");

    if (m_captureStarted) return;

    for (int i = 0; i < BUF_NUM; i++)
    {
        m_bufLocked[i] = 0;
    }

    m_bufIdx = 0;
    m_frameProcessIdx = 0;
    m_frameProcessInWait = false;

    m_stopProcessFrame = false;
    m_thread = std::thread([this]()
    {
        while (!m_stopProcessFrame)
        {
            ProcessFrame();
        }
    });

    vector<rs2::stream_profile> profiles;
    for (int i = 0; i < m_depthProfiles.size(); i++)
    {
        profiles.push_back(m_depthProfiles[i]);
    }

    for (int i = 0; i < m_colorProfiles.size(); i++)
    {
        profiles.push_back(m_colorProfiles[i]);
    }

    rs2::config cfg;
    cfg.enable_device(active_camera.serial);

    for (int i = 0; i < profiles.size(); i++)
    {
        rs2::video_stream_profile pf = profiles[i].as<video_stream_profile>();

        rs2_stream type = pf.stream_type();
        int index = pf.stream_index();
        int width = pf.width();
        int height = pf.height();
        rs2_format format = pf.format();
        int fps = pf.fps();

        std::cout << type << ", " << index << ", " << width << ", " << height << ", " << format << "," << fps << std::endl;

        cfg.enable_stream(type, index, width, height, format, fps);
    }


    pipe.start(cfg, [&](rs2::frame frames) {
    if (auto fs = frames.as<rs2::frameset>())
    {
//            std::cout << std::endl;
//            std::cout << "------------ " << fs.size() << "------------ " << std::endl;

//            for (auto f : fs)
//            {
//                std::cout << f.get_frame_number() << "," << f.get_data_size() << std::endl;
//            }

            //if other frame callback is still in processing, drop the frame
            MUTEX_LOCK(&m_mutex);

            //Native image atomic fetch
            if (LOCKED_EXCHANGE_ADD((uint64_t *)&m_bufLocked[m_bufIdx], 0))
            {
                MUTEX_UNLOCK(&m_mutex);
                return;
            }

            m_ts = (unsigned long long)fs.get_timestamp();

            if (m_bDepthEnabled)
            {
                rs2::video_frame depth_frame = fs.get_depth_frame();
                int size = depth_frame.get_data_size();

                uint16_t *depth = m_depthImage[m_bufIdx].get();
                DS_MEMCPY_S((void *)depth, size, (void *)depth_frame.get_data(), size);
            }

            if (m_bLrEnabled)
            {
                rs2::video_frame left_frame = fs.get_infrared_frame(1);
                rs2::video_frame right_frame = fs.get_infrared_frame(2);

                int size = left_frame.get_data_size();

                uint8_t *left = m_leftImage[m_bufIdx].get();
                uint8_t *right = m_rightImage[m_bufIdx].get();

                DS_MEMCPY_S(left, size, (void *)left_frame.get_data(), size);
                DS_MEMCPY_S(right, size, (void *)right_frame.get_data(), size);
            }

            if (m_bRgbEnabled)
            {
                rs2::video_frame color_frame = fs.get_color_frame();
                int size = color_frame.get_data_size();

                if (m_pData[(int)RS400_STREAM_COLOR][m_bufIdx] == nullptr)
                    m_pData[(int)RS400_STREAM_COLOR][m_bufIdx] = new uint16_t[size];

                DS_MEMCPY_S(m_pData[(int)RS400_STREAM_COLOR][m_bufIdx], size, (void *)color_frame.get_data(), size);

                // convert uyvy to yuyv
                if (Is_MIPI())
                {
                    uint16_t* p = (uint16_t*) m_pData[(int)RS400_STREAM_COLOR][m_bufIdx];

                    for (int i = 0; i < size / 2; i++)
                    {
                        uint8_t* u = (uint8_t*)p;
                        uint8_t* y = (uint8_t*)p + 1;
                        swap(*u, *y);

                        p++;
                    }
                }

                uint16_t *color = m_mainImage[m_bufIdx].get();
                DS_MEMCPY_S((void *)color, size, m_pData[RS400_STREAM_COLOR][m_bufIdx], size);
            }

            LOCKED_EXCHANGE((uint64_t *)&m_bufLocked[m_bufIdx], 1);     //atomic set to 1 for lock

            if (m_frameProcessInWait)
            {
                //notify frame process thread that frame is availeb to process
                MUTEX_LOCK(&m_buf_mutex);
                m_frameProcessIdx = m_bufIdx;
                COND_SIGNAL(&m_buf_mutex_cv);
                MUTEX_UNLOCK(&m_buf_mutex);
            }

            m_bufIdx += 1;
            if (m_bufIdx >= BUF_NUM) m_bufIdx = 0;

            MUTEX_UNLOCK(&m_mutex);
        }
    });

    m_captureStarted = true;
}

void Rs400Device::StopCapture()
{
    if (!m_captureStarted) return;

    try
    {
        pipe.stop();
    }
    catch (...) {};

    if (m_thread.joinable())
    {
        m_stopProcessFrame = true;
        if (m_frameProcessInWait)
        {
            //notify frame process thread that frame is availeb to process
            MUTEX_LOCK(&m_buf_mutex);
            COND_SIGNAL(&m_buf_mutex_cv);
            MUTEX_UNLOCK(&m_buf_mutex);
        }

        m_thread.join();
        m_stopProcessFrame = false;
    }

    m_captureStarted = false;
}

void Rs400Device::ProcessFrame()
{
    //left and right frames only. Native image
    uint64_t bufLocked = LOCKED_EXCHANGE_ADD((uint64_t *)&m_bufLocked[m_frameProcessIdx], 0); //atomic fetch#else

    if (bufLocked == 0)
    {
        //all in coming frames have been processed. Wait for next frame
        MUTEX_LOCK(&m_buf_mutex);
        m_frameProcessInWait = true;
#ifdef _WIN32
        SleepConditionVariableCS(&m_buf_mutex_cv, &m_buf_mutex, INFINITE);
#else
        (void)pthread_cond_wait(&m_buf_mutex_cv, &m_buf_mutex);
#endif
        m_frameProcessInWait = false;
        MUTEX_UNLOCK(&m_buf_mutex);

        if (m_stopProcessFrame)
            return;
    }

    //process
    uint8_t *left = nullptr;
    uint8_t *right = nullptr;
    uint8_t *color = nullptr;
    uint8_t *depth = nullptr;

    if (m_bLrEnabled)
    {
        left = m_leftImage[m_frameProcessIdx].get();
        right = m_rightImage[m_frameProcessIdx].get();
    }

    if (m_bRgbEnabled)
        color = (uint8_t *)m_mainImage[m_frameProcessIdx].get();

    if (m_bDepthEnabled)
        depth = (uint8_t *)m_depthImage[m_frameProcessIdx].get();

    m_callback(left, right, color, depth, m_ts);

    LOCKED_EXCHANGE((uint64_t *)&m_bufLocked[m_frameProcessIdx], 0);   //atomic set to 0 to unlock
    m_frameProcessIdx += 1;
    if (m_frameProcessIdx >= BUF_NUM) m_frameProcessIdx = 0;
}

void Rs400Device::EnableAutoExposure(float value, bool bColor)
{
    if (!bColor)
        m_depthSensor.set_option(rs2_option::RS2_OPTION_ENABLE_AUTO_EXPOSURE, value);
    else if (m_colorSensor != NULL)
    {
        m_colorSensor.set_option(rs2_option::RS2_OPTION_ENABLE_AUTO_EXPOSURE, value);

        // disable AUTO_EXPOSURE_PRIORITY to ensure frame sync between rgb and depth/left/right sensors
        if (m_colorSensor.supports(rs2_option::RS2_OPTION_AUTO_EXPOSURE_PRIORITY))
        {
			cout << "disable AUTO_EXPOSURE_PRIORITY to ensure frame sync between rgb and depth/left/right sensors" << endl;
            m_colorSensor.set_option(rs2_option::RS2_OPTION_AUTO_EXPOSURE_PRIORITY, 0.0);
        }
    }
}

void Rs400Device::SetExposure(float value, bool bColor)
{
    if (!bColor)
        m_depthSensor.set_option(rs2_option::RS2_OPTION_EXPOSURE, value);
    else if (m_colorSensor != NULL)
        m_colorSensor.set_option(rs2_option::RS2_OPTION_EXPOSURE,value);
}

float Rs400Device::GetExposure(bool bColor)
{
    if (!bColor)
        return m_depthSensor.get_option(rs2_option::RS2_OPTION_EXPOSURE);
    else if (m_colorSensor != NULL)
        return m_colorSensor.get_option(rs2_option::RS2_OPTION_EXPOSURE);

    return 0;
}

void Rs400Device::GetExposureRange(int *rmin, int *rmax, bool bColor)
{
    if (!bColor)
    {
        auto range = m_depthSensor.get_option_range(rs2_option::RS2_OPTION_EXPOSURE);
        *rmin = (int)range.min;
        *rmax = (int)range.max;
    }
    else if (m_colorSensor != NULL)
    {
        auto range = m_colorSensor.get_option_range(rs2_option::RS2_OPTION_EXPOSURE);
        *rmin = (int)range.min;
        *rmax = (int)range.max;
    }
}

void Rs400Device::SetBrightness(float value, bool bColor)
{
    if (!bColor)
    {
        if (m_depthSensor.supports(rs2_option::RS2_OPTION_BRIGHTNESS))
        {
             m_depthSensor.set_option(rs2_option::RS2_OPTION_BRIGHTNESS, value);
        }
    }
    else if (m_colorSensor != NULL)
    {
        if (m_colorSensor.supports(rs2_option::RS2_OPTION_BRIGHTNESS))
        {
            m_colorSensor.set_option(rs2_option::RS2_OPTION_BRIGHTNESS, value);
        }
    }
}

float Rs400Device::GetBrightnessRange(int *rmin, int *rmax, int *rdef, bool bColor)
{
    float brightness = 0;

    if (!bColor)
    {
        auto range = m_depthSensor.get_option_range(rs2_option::RS2_OPTION_BRIGHTNESS);
        *rmin = (int)range.min;
        *rmax = (int)range.max;
        *rdef = (int)range.def;
        brightness = m_depthSensor.get_option(rs2_option::RS2_OPTION_BRIGHTNESS);
    }
    else if (m_colorSensor != NULL && !Is_MIPI())
    {
        auto range = m_colorSensor.get_option_range(rs2_option::RS2_OPTION_BRIGHTNESS);
        *rmin = (int)range.min;
        *rmax = (int)range.max;
        *rdef = (int)range.def;
        brightness = m_colorSensor.get_option(rs2_option::RS2_OPTION_BRIGHTNESS);
    }

    return brightness;
}

void Rs400Device::SetGain(float value, bool bColor)
{
    if (!bColor)
        m_depthSensor.set_option(rs2_option::RS2_OPTION_GAIN, value);
    else if (m_colorSensor != NULL)
        m_colorSensor.set_option(rs2_option::RS2_OPTION_GAIN, value);
}

float Rs400Device::GetGainRange(int *rmin, int *rmax, int *rdef, bool bColor)
{
    float gain = 0;

    if (!bColor)
    {
        auto range = m_depthSensor.get_option_range(rs2_option::RS2_OPTION_GAIN);
        *rmin = (int)range.min;
        *rmax = (int)range.max;
        *rdef = (int)range.def;
        gain = m_depthSensor.get_option(rs2_option::RS2_OPTION_GAIN);
    }
    else if (m_colorSensor != NULL)
    {
        auto range = m_colorSensor.get_option_range(rs2_option::RS2_OPTION_GAIN);
        *rmin = (int)range.min;
        *rmax = (int)range.max;
        *rdef = (int)range.def;
        gain = m_colorSensor.get_option(rs2_option::RS2_OPTION_GAIN);
    }

    return gain;
}

void Rs400Device::EnableEmitter(float value)
{
    try {
        if (m_depthSensor.supports(rs2_option::RS2_OPTION_EMITTER_ENABLED))
        {
            m_depthSensor.set_option(rs2_option::RS2_OPTION_EMITTER_ENABLED, value);
        }
    } catch (...)
    { }
}

void Rs400Device::SetThermalCompensation(float value)
{
    if (m_depthSensor.supports(rs2_option::RS2_OPTION_THERMAL_COMPENSATION))
    {
        m_depthSensor.set_option(rs2_option::RS2_OPTION_THERMAL_COMPENSATION, value);

        // Allow for FW changes to propagate
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
}

float Rs400Device::GetThermalCompensation()
{
    float tc = -1.0;

    if (m_depthSensor.supports(rs2_option::RS2_OPTION_THERMAL_COMPENSATION))
    {
        tc = m_depthSensor.get_option(rs2_option::RS2_OPTION_THERMAL_COMPENSATION);
    }

    return tc;
}

void Rs400Device::SetAeControl(unsigned int point)
{
    try {
        advanced_mode advanced = m_device.as<rs400::advanced_mode>();
        STAEControl aeControl = { point };
        advanced.set_ae_control(aeControl);
    }
    catch (exception e)
    {
#ifdef DEBUG
        throw runtime_error("Set AE Control Exception!");
#endif
    }
}

void Rs400Device::SetROI(int ExposureTopEdge, int ExposureBottomEdge, int ExposureLeftEdge, int ExposureRightEdge)
{
    // Default ROI behaviour is center 3/4 of the screen:
    if (m_depthSensor.is<roi_sensor>())
    {
        m_depthSensor.as<roi_sensor>().set_region_of_interest({ ExposureLeftEdge, ExposureTopEdge,
            ExposureRightEdge, ExposureBottomEdge });
    }
}

int Rs400Device::GetDepthSensor(device* dev)
{
    auto sensors = dev->query_sensors();

    for (int i = 0; i < (int)sensors.size(); i++)
    {
        if (sensors[i].supports(rs2_option::RS2_OPTION_DEPTH_UNITS))
            return i;
    }

    return -1;
}

int Rs400Device::GetColorSensor(device* dev)
{
    auto sensors = dev->query_sensors();

    for (int i = 0; i < (int)sensors.size(); i++)
    {
        vector<stream_profile> pfs = sensors[i].get_stream_profiles();

        for (auto pf : pfs)
        {
            auto video = pf.as<video_stream_profile>();
            LOG("GetColorSensor::"<< video.width() << " x " << video.height() << " @ " << video.fps() << "," << pf.format());

            if (pf.format() == RS2_FORMAT_YUYV)
                return i;
        }
    }

    return -1;
}

bool Rs400Device::GetProfile(stream_profile& profile, rs2_stream stream, rs2_format format, int width, int height, int fps, int index)
{
    rs2::sensor sensor;

    if (stream == rs2_stream::RS2_STREAM_INFRARED)
    {
        sensor = m_depthSensor;
    }
    else if (stream == rs2_stream::RS2_STREAM_DEPTH)
    {
        sensor = m_depthSensor;
    }
    else if (stream == rs2_stream::RS2_STREAM_COLOR)
    {
        std::string pid = active_camera.pid;

        // D405 color stream comes from the left sensor. No dedicated color sensor.
        if (pid.compare("0B5B") == 0)
            sensor = m_depthSensor;
        else
            sensor = m_colorSensor;
    }

    vector<stream_profile> pfs = sensor.get_stream_profiles();

    for (int i = 0; i < (int)pfs.size(); i++)
    {
        auto video = pfs[i].as<video_stream_profile>();

        LOG("GetProfile:: " << video.width() << " x " << video.height() << " @ " << video.fps() << "," << pfs[i].format());

        if ((pfs[i].format() == format)
            && (video.width() == width)
            && (video.height() == height)
            && (video.fps() == fps)
            && (video.stream_index() == index)
            )
        {
            profile = pfs[i];
            return true;
        }
    }

    return false;
}

bool Rs400Device::HwMonitorCmd_Get(uint8_t* cmd, uint8_t* data, int length)
{
    void * rs400Dev = (void*) &m_device;

#ifdef __D400_USE_LIBREALSENSE__
#ifdef __ANDROID__
    rs2_error* e = 0;
    rs2_device* dev = (rs2_device*)rs400Dev;

    uint8_t RawBuffer[DS5_CMD_LENGTH];

    LOG("HwMonitorCmd_Get at line %d.", __LINE__);
    DS_MEMCPY(RawBuffer, cmd, DS5_CMD_LENGTH);

    LOG("before send_and_receive_raw_data at line %d.", __LINE__);
    std::shared_ptr<const rs2_raw_data_buffer> list(
    rs2_send_and_receive_raw_data(dev, (void*)RawBuffer, DS5_CMD_LENGTH, &e),
    rs2_delete_raw_data);
    error::handle(e);
    LOG("after send_and_receive_raw_data at line %d.", __LINE__);

    auto size = rs2_get_raw_data_size(list.get(), &e);
    error::handle(e);

    auto rcvBuf = rs2_get_raw_data(list.get(), &e);

    if (rcvBuf[0] != cmd[4])
        return false;

    LOG("HwMonitorCmd_Get at line %d.", __LINE__);

    int len = (length <= size - DS5_CMD_OPCODE_SIZE) ? length : size - DS5_CMD_OPCODE_SIZE;

    DS_MEMCPY(data, rcvBuf + DS5_CMD_OPCODE_SIZE, len);

    LOG("HwMonitorCmd_Get at line %d.", __LINE__);
    return true;

#else
    LOG("HwMonitorCmd_Get start at line %d.", __LINE__);
    try {
        device device = *(rs2::device *)rs400Dev;
        std::vector<uint8_t> RawBuffer(DS5_CMD_LENGTH);
        std::vector<uint8_t> rcvBuf;

        LOG("HwMonitorCmd_Get at line %d.", __LINE__);
        auto debug = device.as<debug_protocol>();

        LOG("HwMonitorCmd_Get at line %d.", __LINE__);
        DS_MEMCPY(RawBuffer.data(), cmd, DS5_CMD_LENGTH);

        LOG("before send_and_receive_raw_data at line %d.", __LINE__);
        rcvBuf = debug.send_and_receive_raw_data(RawBuffer);
        LOG("after send_and_receive_raw_data at line %d.", __LINE__);

        if (rcvBuf[0] != cmd[4])
            return false;

        LOG("HwMonitorCmd_Get at line %d.", __LINE__);

        size_t len = (length <= rcvBuf.size() - DS5_CMD_OPCODE_SIZE) ? length : rcvBuf.size() - DS5_CMD_OPCODE_SIZE;

        DS_MEMCPY(data, rcvBuf.data() + DS5_CMD_OPCODE_SIZE, len);

        LOG("HwMonitorCmd_Get at line %d.", __LINE__);
    }
    catch (exception e)
    {
        LOG("HwMonitorCmd_Get at line %d.", __LINE__);
        return false;
    }

    LOG("HwMonitorCmd_Get end at line %d.", __LINE__);
    return true;
#endif
#else
    // not use librealsense
    return true;
#endif
}

bool Rs400Device::HwMonitorCmd_Set(uint8_t* cmd, uint8_t* data, int length)
{
    void * rs400Dev = (void*)&m_device;

#ifdef __D400_USE_LIBREALSENSE__
#ifdef __ANDROID__
    rs2_error* e = 0;
    rs2_device* dev = (rs2_device*)rs400Dev;

    LOG("HwMonitorCmd_Set at line %d.", __LINE__);

    std::vector<uint8_t> RawBuffer(DS5_CMD_LENGTH + length);
    DS_MEMCPY(RawBuffer.data(), cmd, DS5_CMD_LENGTH);
    if (length > 0)
        DS_MEMCPY(RawBuffer.data() + DS5_CMD_LENGTH, data, length);
    uint16_t *snd_buf = (uint16_t *)RawBuffer.data();
    snd_buf[0] += length;

    LOG("before send_and_receive_raw_data at line %d.", __LINE__);
    std::shared_ptr<const rs2_raw_data_buffer> list(
    rs2_send_and_receive_raw_data(dev, (void*)RawBuffer.data(), DS5_CMD_LENGTH + length, &e),
        rs2_delete_raw_data);
    error::handle(e);
    LOG("after send_and_receive_raw_data at line %d.", __LINE__);

    auto size = rs2_get_raw_data_size(list.get(), &e);
    error::handle(e);

    LOG("HwMonitorCmd_Set at line %d.", __LINE__);

    auto rcvBuf = rs2_get_raw_data(list.get(), &e);

    if (rcvBuf[0] != cmd[4])
        return false;

    LOG("HwMonitorCmd_Set at line %d.", __LINE__);
    return true;
#else
    try {
        device device = *(rs2::device *)rs400Dev;
        std::vector<uint8_t> RawBuffer(DS5_CMD_LENGTH + length);
        std::vector<uint8_t> rcvBuf;
        DS_MEMCPY(RawBuffer.data(), cmd, DS5_CMD_LENGTH);
        if (length > 0)
            DS_MEMCPY(RawBuffer.data() + DS5_CMD_LENGTH, data, length);
        uint16_t *snd_buf = (uint16_t *)RawBuffer.data();
        snd_buf[0] += length;

        auto debug = device.as<debug_protocol>();

        LOG("before send_and_receive_raw_data at line %d.", __LINE__);
        rcvBuf = debug.send_and_receive_raw_data(RawBuffer);
        LOG("after send_and_receive_raw_data at line %d.", __LINE__);
        if (rcvBuf[0] != cmd[4])
            return false;
        }
        catch (exception e)
        {
            return false;
        }

        return true;
#endif
#else
     // not use librealsense
    return true;
#endif
}

string Rs400Device::GetDevicePID()
{
    return active_camera.pid;
}

bool Rs400Device::SupportsRGB()
{
    return (m_colorSensor != NULL);
}

void Rs400Device::HwReset()
{
    m_device.hardware_reset();
}
