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
#include <algorithm>
#include "librealsense2/rs.hpp"
#include "GuiView.h"
#include "imgui-fonts-fontawesome.hpp"
#include "imgui-fonts-karla.hpp"

// demo slides in RGBA format and DEMO_IMG_WIDTH x DEMO_IMG_HEIGHT size. Original picture can be JPG then use
// a third party tool to convert to RGBA format. Then write a simple tool to convert the RGBA binary files into
// c files included below
#include "demo/targetedoverview.h"
#include "demo/targetedt0c.h"
#include "demo/targetedt1.h"
#include "demo/targetedt2.h"
#include "demo/targetedt3.h"
#include "demo/targetedt4.h"
#include "demo/targetedstart.h"
#include "demo/targetedrect.h"
#include "demo/targetedscale.h"
#include "demo/targetedrgb.h"

#include "demo/targetlessoverview.h"
#include "demo/targetlessscene1.h"
#include "demo/targetlessscene2.h"
#include "demo/targetlessscene3.h"
#include "demo/targetlesscalibration1.h"
#include "demo/targetlesscalibration2.h"
#include "demo/targetlesscalibration3.h"

#include "demo/demoverify.h"

using namespace std;
using namespace DynamicCalibrator;


GuiView::GuiView()
{
    m_devIdx = 0;
    m_devIdxDummy = 0;
    m_showAdvancedOptions = false;
    m_bPlugMsgInShow = false;

    m_elapsedTime.Start();
    m_CalibrationStatus = CALIBRATION_STATUS_NONE;

    m_prevSerial.clear();

    font_18 = nullptr;
    font_14 = nullptr;

    m_bNeedToRefresh = false;

	showdemo = false;
	step = 0;
}

GuiView::~GuiView()
{
    ImGui_ImplGlut_Shutdown();
}

GLuint LoadDemoTexture(unsigned char * data)
{
	GLuint texture = 0;

	glEnable(GL_TEXTURE_2D);
	glGenTextures(1, &texture);
	glBindTexture(GL_TEXTURE_2D, texture);

	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
	glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, DEMO_IMG_WIDTH, DEMO_IMG_HEIGHT, 0, GL_RGBA, GL_UNSIGNED_BYTE, data);

	glBindTexture(GL_TEXTURE_2D, 0);
	glDisable(GL_TEXTURE_2D);

	return texture;
}

int GuiView::Initialize(void)
{
    // GUI mode (default: targetless):
    m_targeted = true;

    m_captureManager = new CaptureManager(this, m_CmdOptions.SaveFrame);
    m_cameras = m_captureManager->ListCameras();
    if (m_cameras.size())
    {
        std::sort(m_cameras.begin(), m_cameras.end());
    }
    m_devIdx = 0;

    InitializeGL((void *)this);
    glutMouseFunc([](int button, int state, int x, int y) {
        ImGui_ImplGlut_MouseButtonCallback(button, state, x, y);
        glutPostRedisplay();
    });
    glutMotionFunc([](int x, int y) {
        ImGui_ImplGlut_MotionCallback(x, y);
        glutPostRedisplay();
    });
    glutPassiveMotionFunc([](int x, int y) {
        ImGui_ImplGlut_PassiveMotionCallback(x, y);
        glutPostRedisplay();
    });
    ImGui_ImplGlut_Init(true);

    default_control_panel_width = m_winWidth * 0.2;
    default_log_height = m_winHeight * 0.2;

    EasyTheming(font_14, font_18);

    m_captureManager->SetDevicesChangedCallback([&](rs2::event_information& info)
    {
        m_bNeedToRefresh = true;
        //force redisaply
        glClearColor(0.0f, 0.0f, 0.0f, 1);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
        glutPostRedisplay();
    });

    if (m_cameras.size())
        GetExposureValue(m_devIdx);

	// targeted calibration demos
	targeted_demo_texture_id[0] = LoadDemoTexture((unsigned char*) targetedoverview);
	targeted_demo_texture_id[1] = LoadDemoTexture((unsigned char*) targetedt0c);
	targeted_demo_texture_id[2] = LoadDemoTexture((unsigned char*) targetedt1);
	targeted_demo_texture_id[3] = LoadDemoTexture((unsigned char*) targetedt2);
	targeted_demo_texture_id[4] = LoadDemoTexture((unsigned char*) targetedt3);
	targeted_demo_texture_id[5] = LoadDemoTexture((unsigned char*) targetedt4);
	targeted_demo_texture_id[6] = LoadDemoTexture((unsigned char*) targetedstart);
	targeted_demo_texture_id[7] = LoadDemoTexture((unsigned char*) targetedrect);
	targeted_demo_texture_id[8] = LoadDemoTexture((unsigned char*) targetedscale);
	targeted_demo_texture_id[9] = LoadDemoTexture((unsigned char*) targetedrgb);
	targeted_demo_texture_id[10] = LoadDemoTexture((unsigned char*) demoverify);

	// targetless calibration demos
	targetless_demo_texture_id[0] = LoadDemoTexture((unsigned char*) targetlessoverview);
	targetless_demo_texture_id[1] = LoadDemoTexture((unsigned char*) targetlessscene1);
	targetless_demo_texture_id[2] = LoadDemoTexture((unsigned char*) targetlessscene2);
	targetless_demo_texture_id[3] = LoadDemoTexture((unsigned char*) targetlessscene3);
	targetless_demo_texture_id[4] = LoadDemoTexture((unsigned char*) targetlesscalibration1);
	targetless_demo_texture_id[5] = LoadDemoTexture((unsigned char*) targetlesscalibration2);
	targetless_demo_texture_id[6] = LoadDemoTexture((unsigned char*) targetlesscalibration3);
	targetless_demo_texture_id[7] = LoadDemoTexture((unsigned char*) demoverify);

    return EXIT_SUCCESS;
}

int GuiView::UpdateCalibrationTablesComplete(std::string msg, bool bUpdated)
{
	int ret = DC_SUCCESS;

    std::string logmsg = msg;

    m_captureManager->StopCapture();

    if (bUpdated && (m_cameras[m_devIdx].features & SKU_RGB) &&  m_targeted && !m_rgbCalib && !m_skiprgb)
    {
        m_appLog.AddLog(msg);
        m_appLog.AddLog("Scale calibration completed, start RGB calibration");
        m_rgbCalib = true;

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

    m_runningStatus = STATUS_NOT_STARTED;

    if (bUpdated)
    {
        logmsg += "\nCalibration completed, results updated to device successfully!\n";
        m_CalibrationStatus = CALIBRATION_STATUS_SUCCESSFUL;
    }
    else
    {
        logmsg += "\nCalibration Failed. The results failed to update to the device. One of the common causes is loose USB connection. Please check the device and try again.\n";
        m_CalibrationStatus = CALIBRATION_STATUS_FAILED;
        m_errorCode = DC_ERROR_TABLE_WRITE_FAILED;
    }
    m_appLog.AddLog(logmsg);

    m_rgbCalib = false;

    OnDisplay();
    glutPostRedisplay();
    glutIdleFunc(nullptr);

	return ret;
}

void GuiView::ErrorHandling(int errorCode)
{
    m_errorCode = errorCode;
    m_appLog.AddLog(rs_convert_err_to_string(errorCode));
    m_captureManager->StopCapture();
    m_runningStatus = STATUS_NOT_STARTED;
    m_rgbCalib = false;
}

void GuiView::StartCalibration()
{
    auto camera = m_cameras[m_devIdx];

    CreateLogDirectory(camera.serial);
    m_appLog.SetLogFileStream(&m_logFile);

    m_appLog.AddLog("\nResult folder: " + this->m_dir);
    m_appLog.AddLog("Serial number: " + camera.serial);
    m_appLog.AddLog("Device name: " + camera.name);
    m_appLog.AddLog("Device PID: " + camera.pid);
    m_appLog.AddLog("FW version: " + camera.fw_ver);
    m_appLog.AddLog("USB Type: " + camera.usb_type);

    if (!m_targeted)
        m_appLog.AddLog("Calibration Type: Targetless");
    else
        m_appLog.AddLog("Calibration Type: Targeted");

    if (camera.features & HAS_EMITTER)
    {
        if (m_useLaser && !m_targeted)
            m_appLog.AddLog("Laser Power: On");
        else
            m_appLog.AddLog("Laser Power: Off");
    }

	if (camera.features & SKU_RGB)
	{
		m_appLog.AddLog("RGB: Yes");
	}

	if (camera.features & SKU_WIDE)
	{
		m_appLog.AddLog("Wide Angle Lens: Yes");
	}

	if (camera.features & SKU_IMU)
	{
		m_appLog.AddLog("IMU: Yes");
	}

    if (m_autoExposureEnable)
    {
        m_appLog.AddLog("Auto Exposure: On");

        m_appLog.AddLog("IR setpoint: " + std::to_string(m_aeSetpoint) + ", (min: " + std::to_string(m_aeSetpointMin) + ", max: " + std::to_string(m_aeSetpointMax) + ", default: " + std::to_string(m_aeSetpointDefault) + ")");

        if (camera.features & SKU_RGB)
        {
            m_appLog.AddLog("RGB brightness: " + std::to_string(m_aeRgbBrightness) + ", (min: " + std::to_string(m_aeRgbBrightnessMin) + ", max: " + std::to_string(m_aeRgbBrightnessMax) + ", default: " + std::to_string(m_aeRgbBrightnessDefault) + ")");
        }

        if (m_aesweepmode)
            m_appLog.AddLog("AE SetPoint: Auto");
        else
            m_appLog.AddLog("AE SetPoint: " + std::to_string(m_aeSetpoint));
    }
    else
    {
        m_appLog.AddLog("Auto Exposure: Off");
        m_appLog.AddLog("Depth Exposure: " + std::to_string(m_depthExposure));
        if (camera.features & SKU_RGB)
            m_appLog.AddLog("Color Exposure: " + std::to_string(m_colorExposure));
    }

    m_CalibrationStatus = CALIBRATION_STATUS_NONE;

    if (!IsFwVersionSupported(camera))
    {
        m_errorCode = DC_ERROR_FW_VERSION_OLD;
        m_appLog.AddLog(rs_convert_err_to_string(m_errorCode));

		std::string error_msg = "";
		stringstream stream;
		stream << "The minimum firmware version required for this device is " << camera.minFWVerMajor << "." << camera.minFWVerMinor << "." << camera.minFWVerPatch << "." << camera.minFWVerBuild << ". Please upgrade firmware and try again.\n";
		error_msg = stream.str();

		m_appLog.AddLog(error_msg);

        return;
    }

	bool initialized = false;

	try
	{
		initialized = m_captureManager->InitializeCamera(camera.serial);
	}
	catch (exception e)
	{
		initialized = false;
	}

    if (initialized)
    {
        int ret = DC_SUCCESS;

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
            m_elapsedTime.Restart();
            m_runningStatus = STATUS_RUNNING;
        }
        else
        {
            m_appLog.AddLog(rs_convert_err_to_string(ret));
        }
    }
    else
    {
        m_appLog.AddLog("Failed to initialize device.");
        return;
    }

    if (m_runningStatus != STATUS_RUNNING)
    {
        m_appLog.AddLog("Failed to start calibration.");
    }
}

void GuiView::CheckButtonClick()
{
    auto camera = m_cameras[m_devIdx];

    for (int i = 0; i < 10; i++) ImGui::Spacing();

    const char *szButtonTextStart = "Start Calibration";
    const char *szButtonTextStop = "Stop Calibration";

    ImVec2 label_size;

    if (m_runningStatus == STATUS_NOT_STARTED)
    {
        label_size = ImGui::CalcTextSize(szButtonTextStart, NULL, true);
    }
    else
    {
        label_size = ImGui::CalcTextSize(szButtonTextStop, NULL, true);
    }

    ImVec2 button_size = ImVec2(label_size.x + 12, label_size.y + 12);

    // Center the button:
    float center_x = ImGui::GetWindowContentRegionMin().x +
        (ImGui::GetWindowContentRegionWidth() - button_size.x)/2;

    ImGui::SetCursorPosX(center_x);

    bool pressed = false;

    switch (m_runningStatus)
    {
    case STATUS_NOT_STARTED:
        pressed = ImGui::Button(szButtonTextStart, button_size);

        if (ImGui::IsItemHovered() && !IsFwVersionSupported(camera))
        {
            ImGui::PushStyleColor(ImGuiCol_Text, redish);
            ImGui::SetTooltip("Error, firmware on device is outdated");
            ImGui::PopStyleColor();
        }

        if (pressed)
        {
            glutIdleFunc([]() {
                MainView *pView = reinterpret_cast<MainView *>(glutGetWindowData());
                pView->OnIdle();
            });

			showdemo = false;

            glutPostRedisplay();
            StartCalibration();
        }
        break;

    case STATUS_RUNNING:
    {
        bool bTimeOut = m_elapsedTime.ElapsedSeconds() >= m_timeout ? true : false;
        if (bTimeOut)
        {
            m_errorCode = DC_ERROR_TIME_OUT;
            m_appLog.AddLog(rs_convert_err_to_string(m_errorCode));
        }

        ImGui::PushStyleColor(ImGuiCol_Button, redish);
        ImGui::PushStyleColor(ImGuiCol_ButtonHovered, redish + 0.1f);
        ImGui::PushStyleColor(ImGuiCol_ButtonActive, redish + (-0.1f));

        if (ImGui::Button(szButtonTextStop, button_size) || bTimeOut)
        {
            glutPostRedisplay();
            m_captureManager->StopCapture();
            m_runningStatus = STATUS_NOT_STARTED;
            m_rgbCalib = false;
            if (!bTimeOut)
                m_appLog.AddLog("Calibration has been cancelled.\n");
            glutIdleFunc(nullptr);
        }
        ImGui::PopStyleColor(3);
    }
    break;

    default:
        break;
    }
}

void GuiView::ShowUI()
{
    HotplugHandler();

    ImGui_ImplGlut_NewFrame();

    // Set window position and size dynamically
    ImGui::SetNextWindowPos({ 0, 0 });

    ImGui::SetNextWindowSize(ImVec2(default_control_panel_width, m_winHeight));

    ImGuiWindowFlags flags = ImGuiWindowFlags_NoResize | ImGuiWindowFlags_NoMove |
        ImGuiWindowFlags_NoCollapse | ImGuiWindowFlags_NoTitleBar |
        ImGuiWindowFlags_NoSavedSettings;

    ImGui::Begin("Control Panel", nullptr, flags);
    ImGui::PushFont(font_14);

    if (m_cameras.size())
    {
        auto camera = m_cameras[m_devIdx];
        if (m_prevSerial != camera.serial)
        {
            m_CalibrationStatus = CALIBRATION_STATUS_NONE;
        }

        m_prevSerial = camera.serial;

        ShowDeviceDetails();

        if (IsUsb3(camera) || camera.Is_MIPI())
        {
            ShowDeviceOptions();

            if (m_runningStatus == STATUS_NOT_STARTED)
            {
                if (m_CalibrationStatus == CALIBRATION_STATUS_NONE)
                {
                    ShowDemoHelpMsg();
                }
                else
                {
                    ShowCalibrationResults();
                }
            }

            CheckButtonClick();
        }
        else if (IsUsb2(camera))
        {
            ShowUsbError();
        }
    }
	else
	{
		m_CalibrationStatus = CALIBRATION_STATUS_NONE;
		ImGui::Text("No device detected.");
	}

    ImGui::PopFont();
    ImGui::End();

    m_appLog.Show(font_14,
        default_control_panel_width, m_winHeight - default_log_height,
        m_winWidth - default_control_panel_width,
        default_log_height);

//    if ((m_runningStatus == STATUS_NOT_STARTED)
//        && (m_CalibrationStatus != CALIBRATION_STATUS_NONE)
//        )
//    {
//        ShowCalibrationResults();
//    }

    ImGui::Render();
}

void GuiView::ShowDeviceDetails(void)
{
    auto camera = m_cameras[m_devIdx];

    ImVec2 pos;
    pos.x = 0;
    pos.y = 0;

    ImDrawList* draw_list = ImGui::GetWindowDrawList();

    draw_list->AddRectFilled(pos, { (float)default_control_panel_width, pos.y + 40 },
        ImColor(light_blue));

    draw_list->AddLine(pos, { (float)default_control_panel_width, pos.y },
        ImColor(black));

    std::vector<const char*>  names;
    for (auto &s : m_cameras) names.push_back(s.serial.c_str());

    ImGui::AlignFirstTextHeightToWidgets();
    ImGui::Text("Devices:");
    ImGui::SameLine();

    ImGui::PushItemWidth(-1);

    ImGuiStyle& style = ImGui::GetStyle();
    const float w = ImGui::CalcItemWidth();
    const ImVec2 label_size = ImGui::CalcTextSize("", NULL, true);

    ImVec2 Min = ImGui::GetCursorPos();
    ImVec2 Max = { ImGui::GetCursorPos().x + w,
        ImGui::GetCursorPos().y + label_size.y + style.FramePadding.y*2.0f };

    ImGui::PushStyleColor(ImGuiCol_Button, light_blue);
    ImGui::PushStyleColor(ImGuiCol_ButtonHovered, light_blue + 0.1f);
    ImGui::PushStyleColor(ImGuiCol_ButtonActive, light_blue + (-0.1f));

    if (m_runningStatus == STATUS_NOT_STARTED)
    {
        bool value_changed = ImGui::Combo("", &m_devIdx, names.data(), static_cast<int>(m_cameras.size()));

        if (value_changed)
        {
            m_CalibrationStatus = CALIBRATION_STATUS_NONE;
            GetExposureValue(m_devIdx);
        }
    }
    else
    {
        m_devIdxDummy = 0;
        ImGui::Combo("", &m_devIdxDummy, camera.serial.c_str(), 1);
    }
    ImGui::PopStyleColor(3);
    ImGui::PopItemWidth();

    draw_list->AddRect(Min, Max, ImColor(regular_text), style.FrameRounding);

    ImGui::SetCursorPosY(ImGui::GetCursorPosY() + 12);

    ImGui::PushStyleColor(ImGuiCol_Text, regular_text);
    ImGui::Columns(2, "DevicesList", false);
    ImGui::SetColumnOffset(1, 130);

    ImGui::Text("Device PID:");
    ImGui::Text("Device name:");
    ImGui::Text("Serial number:");
    ImGui::Text("Firmware version:");
    ImGui::Text("USB Type:");
    ImGui::NextColumn();
    ImGui::Text(camera.pid.c_str());
    ImGui::Text(camera.name.c_str());
    ImGui::Text(camera.serial.c_str());

    if (IsFwVersionSupported(camera))
    {
        ImGui::Text(camera.fw_ver.c_str());
    }
    else
    {
        // mark firmware version as red if it is out of date:
        ImGui::TextColored(redish, camera.fw_ver.c_str());
    }

    if (!IsUsb2(camera))
    {
        ImGui::Text(camera.usb_type.c_str());
    }
    else
    {
        ImGui::TextColored(redish, camera.usb_type.c_str());
    }

    ImGui::Columns(1);

    ImGui::PopStyleColor();
}

void GuiView::ShowAdvancedDeviceOptions()
{
    auto camera = m_cameras[m_devIdx];

// disabling manual exposure options due to lack of RGB frame sync under manual exposure

//    if (m_targeted)
//    {
//        ImGui::AlignFirstTextHeightToWidgets();
//        ImGui::Checkbox("AutoExposure", &m_autoExposureEnable);
//        ImGui::Spacing();
//    }
//    else
//    {
        m_autoExposureEnable = true;
//    }

    if (m_autoExposureEnable)
    {
        ImGui::AlignFirstTextHeightToWidgets();
		ImGui::SameLine(3);
        ImGui::Text("    Auto Exposure Brightness Sweep:");
		ImGui::PushItemWidth(-1);
		ImGui::PopItemWidth();
		ImGui::Spacing();

		ImGui::AlignFirstTextHeightToWidgets();
        ImGui::SameLine(20);
        bool changed_indoor = ImGui::RadioButton("Auto", &m_aesweepmode, AE_SWEEP_AUTO);

        ImGui::SameLine(100);
        bool changed_manual = ImGui::RadioButton("Manual", &m_aesweepmode, AE_SWEEP_MANUAL);

		bool changed = changed_indoor | changed_manual;

		if (changed)
		{
//			std::string msg = "changed: " + std::to_string(changed_indoor) + std::to_string(changed_outdoor) + std::to_string(changed_manual);
//			m_appLog.AddLog(msg.c_str());

//			msg = "Ae setpoint: " + std::to_string(m_aeSetpoint) + " Ae brightness: " + std::to_string(m_aeRgbBrightness);
//			m_appLog.AddLog(msg.c_str());
		}

		m_captureManager->SetSweepMode(m_aesweepmode);

		if (m_aesweepmode == AE_SWEEP_AUTO)
		{
			if (changed_indoor)
			{
				m_aeSetpoint = m_aeSetpointDefault;
				m_aeRgbBrightness = m_aeRgbBrightnessDefault;
			}
		}
        else if (m_aesweepmode == AE_SWEEP_MANUAL)
        {
            // Manual AE setpoint for depth sensor:
            ImGui::AlignFirstTextHeightToWidgets();
            ImGui::Text("        IR:");
            ImGui::SameLine(80);
            ImGui::PushItemWidth(-1);
			bool setpoint_value_changed = ImGui::SliderInt("##AEsetpoint", &m_aeSetpoint, m_aeSetpointMin, m_aeSetpointMax);
            ImGui::PopItemWidth();
            ImGui::Spacing();

			if (setpoint_value_changed)
			{
				std::string msg = "Ae setpoint: " + std::to_string(m_aeSetpoint);
				m_appLog.AddLog(msg.c_str());
			}

			bool brightness_value_changed = false;

            // Manual AE brightness for RGB sensor:
            if (camera.features & SKU_RGB)
            {
                ImGui::AlignFirstTextHeightToWidgets();
                ImGui::Text("        RGB:");
                ImGui::SameLine(80);
                ImGui::PushItemWidth(-1);
				brightness_value_changed = ImGui::SliderInt("##AEbrightness", &m_aeRgbBrightness, m_aeRgbBrightnessMin, m_aeRgbBrightnessMax);
                ImGui::PopItemWidth();
                ImGui::Spacing();

				if (brightness_value_changed)
				{
					std::string msg = "Ae brightness: " + std::to_string(m_aeRgbBrightness);
					m_appLog.AddLog(msg.c_str());
				}
            }

			ImGui::AlignFirstTextHeightToWidgets();
			ImGui::Text("    ");
			ImGui::SameLine(80);
			ImGui::PushItemWidth(-1);
			char* buttontext = "Restore to Default Values";

			if (ImGui::Button(buttontext))
			{
				m_aeSetpoint = m_aeSetpointDefault;
				m_aeRgbBrightness = m_aeRgbBrightnessDefault;
				setpoint_value_changed = true;
				brightness_value_changed = true;
			}

			if (changed | setpoint_value_changed | brightness_value_changed)
			{
				m_captureManager->SetSweepMode(AE_SWEEP_MANUAL);
				m_captureManager->SetAeControl(m_aeSetpoint);
				m_captureManager->SetBrightness(m_aeRgbBrightness, true);
			}
        }
    }
    else
    {
        ImGui::AlignFirstTextHeightToWidgets();
        ImGui::Text("Depth Exposure:");
        ImGui::SameLine(110);
        ImGui::PushItemWidth(-1);
        ImGui::SliderInt("##DepthExposure", &m_depthExposure, m_depthExposureMin, m_depthExposureMax);
        ImGui::PopItemWidth();
        ImGui::Spacing();
        if (camera.features & SKU_RGB)
        {
            ImGui::AlignFirstTextHeightToWidgets();
            ImGui::Text("RGB Exposure:");
            ImGui::SameLine(110);
            ImGui::PushItemWidth(-1);
            ImGui::SliderInt("##RGBExposure", &m_colorExposure, m_colorExposureMin, m_colorExposureMax);
            ImGui::PopItemWidth();
            ImGui::Spacing();
        }
    }

    if ((camera.features & HAS_EMITTER)
        && !m_targeted)
    {
        ImGui::SetCursorPosY(ImGui::GetCursorPosY() + 5);
        ImGui::AlignFirstTextHeightToWidgets();
        // Turn on or off laser in target-less calibration:
        ImGui::Text("Laser:");
        ImGui::SameLine(50);
        ImGui::RadioButton("On", &m_useLaser, true);
        ImGui::SameLine(120);
        ImGui::RadioButton("Off", &m_useLaser, false);
    }

	ImGui::AlignFirstTextHeightToWidgets();
	ImGui::PushItemWidth(-1);
	ImGui::PopItemWidth();
	ImGui::Spacing();

	if (camera.features & SKU_RGB)
	{
		ImGui::AlignFirstTextHeightToWidgets();

		ImGui::Checkbox("Skip RGB Calibration", &m_skiprgb);
		ImGui::Spacing();
	}

    ImGui::Spacing();
    ImGui::AlignFirstTextHeightToWidgets();
    ImGui::Text("    Timeout:");
    ImGui::SameLine(80);
    ImGui::PushItemWidth(-1);
    ImGui::InputInt("##Timeout", (int *)&m_timeout, 15);
    ImGui::PopItemWidth();

    if (m_targeted)
    {
        return;
    }
}

void GuiView::ShowDeviceOptions()
{
    ImGui::Spacing();
    ImGui::Spacing();
    ImGui::Spacing();
    ImGui::Spacing();

#ifdef ENABLE_TARGETLESS_CALIBRATION_IN_GUI
    if (ImGui::Checkbox("Use Target", &m_targeted))
    {
        m_CalibrationStatus = CALIBRATION_STATUS_NONE;
		showdemo = false;
    }
#endif

    ImGui::Spacing();
    ImGui::Spacing();
    ImGui::Spacing();
    ImGui::Spacing();

    ImGui::PushStyleColor(ImGuiCol_Header, ImGui::GetStyle().Colors[ImGuiCol_WindowBg]);
    m_showAdvancedOptions = ImGui::CollapsingHeader("Advanced Settings");
    ImGui::PopStyleColor();

    if (m_showAdvancedOptions)
    {
        ShowAdvancedDeviceOptions();
    }
}

void GuiView::HotplugHandler()
{
    if (!m_bNeedToRefresh
        || (m_runningStatus != (int)STATUS_NOT_STARTED)
        )
    {
        return;
    }

    m_bNeedToRefresh = false;

    try
    {
        std::vector<camera_info> CameraList_Current = m_captureManager->ListCameras();
        std::sort(CameraList_Current.begin(), CameraList_Current.end());

        std::vector<camera_info> removed;
        std::set_difference(m_cameras.begin(), m_cameras.end(),
            CameraList_Current.begin(), CameraList_Current.end(),
            std::inserter(removed, removed.begin()));

        for (auto& removed_dev : removed)
        {
            std::string msg = "Camera disconnected, serial number " + removed_dev.serial;
            m_appLog.AddLog(msg.c_str());
        }

        std::vector<camera_info> added;
        std::set_difference(CameraList_Current.begin(), CameraList_Current.end(),
            m_cameras.begin(), m_cameras.end(),
            std::inserter(added, added.begin()));

        for (auto& added_dev : added)
        {
            std::string msg = "Camera connected, serial number " + added_dev.serial;
            m_appLog.AddLog(msg.c_str());
        }

        m_cameras = std::move(CameraList_Current);

        if (m_cameras.size())
        {
            m_devIdx = std::min(m_devIdx, (int)m_cameras.size() - 1);
        }
        else
        {
            m_devIdx = 0;
        }
    }
    catch (...)
    {
        m_cameras.clear();
        m_devIdx = 0;
        m_bNeedToRefresh = true;
    }

    glutPostRedisplay();
}

void GuiView::OnDisplay()
{
    bool bDraw = true;
    if (m_runningStatus == (int)STATUS_RUNNING)
    {
        int w = m_winWidth - default_control_panel_width;
        int h = m_winHeight - default_log_height;

        // Set viewport (excluding control panel and output/logging windows):
        SetViewport(default_control_panel_width, default_log_height,
            (GLsizei)w, (GLsizei)h);

        bDraw = m_captureManager->Render(w, h);

        // Restore to default viewport:
        SetViewport(0, 0, (GLsizei)m_winWidth, (GLsizei)m_winHeight);
    }
    else
    {
        glClearColor(0.0f, 0.0f, 0.0f, 1);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    }

    if (bDraw)
    {
        ShowUI();
        glutSwapBuffers();
    }

    if (m_runningStatus == (int)STATUS_RUNNING)
        glutPostRedisplay();
}

void GuiView::OnKeyBoard(unsigned char key, int x, int y)
{
    if (m_runningStatus == (int)STATUS_NOT_STARTED)
    {
        ImGui_ImplGlut_KeyCallback(key, x, y);

        if (key == 27)  //ESC key
        {
            glutLeaveMainLoop();
        }
    }
    else if (m_runningStatus == (int)STATUS_RUNNING)
    {
        if (key == 27)  //ESC key
        {
            m_captureManager->StopCapture();
            m_runningStatus = STATUS_NOT_STARTED;
            m_rgbCalib = false;
            m_appLog.AddLog("Calibration has been cancelled.\n");
            glutPostRedisplay();
        }
    }
}

void GuiView::EasyTheming(ImFont*& font_14, ImFont*& font_18)
{
    ImGuiStyle& style = ImGui::GetStyle();

    ImGuiIO& io = ImGui::GetIO();

    const auto OVERSAMPLE = 1;

    static const ImWchar icons_ranges[] = { 0xf000, 0xf3ff, 0 };

    // Load 18px size fonts
    {
        ImFontConfig config_words;
        config_words.OversampleV = OVERSAMPLE;
        config_words.OversampleH = OVERSAMPLE;
        font_18 = io.Fonts->AddFontFromMemoryCompressedTTF(karla_regular_compressed_data,
            karla_regular_compressed_size, 20.f, &config_words);

        ImFontConfig config_glyphs;
        config_glyphs.MergeMode = true;
        config_glyphs.OversampleV = OVERSAMPLE;
        config_glyphs.OversampleH = OVERSAMPLE;
        font_18 = io.Fonts->AddFontFromMemoryCompressedTTF(font_awesome_compressed_data,
            font_awesome_compressed_size, 20.f, &config_glyphs, icons_ranges);
    }

    // Load 14px size fonts
    {
        ImFontConfig config_words;
        config_words.OversampleV = OVERSAMPLE;
        config_words.OversampleH = OVERSAMPLE;
        font_14 = io.Fonts->AddFontFromMemoryCompressedTTF(karla_regular_compressed_data,
            karla_regular_compressed_size, 15.f);

        ImFontConfig config_glyphs;
        config_glyphs.MergeMode = true;
        config_glyphs.OversampleV = OVERSAMPLE;
        config_glyphs.OversampleH = OVERSAMPLE;
        font_14 = io.Fonts->AddFontFromMemoryCompressedTTF(font_awesome_compressed_data,
            font_awesome_compressed_size, 16.f, &config_glyphs, icons_ranges);
    }

    style.WindowRounding = 0.0f;
    style.ScrollbarRounding = 0.0f;

    style.Colors[ImGuiCol_Text] = white;
    style.Colors[ImGuiCol_WindowBg] = dark_grey;
    style.Colors[ImGuiCol_Border] = white;
    style.Colors[ImGuiCol_BorderShadow] = transparent;
    style.Colors[ImGuiCol_FrameBg] = light_blue;

    style.Colors[ImGuiCol_ScrollbarBg] = scrollbar_bg;
    style.Colors[ImGuiCol_ScrollbarGrab] = scrollbar_grab;
    style.Colors[ImGuiCol_ScrollbarGrabHovered] = scrollbar_grab + 0.1f;
    style.Colors[ImGuiCol_ScrollbarGrabActive] = scrollbar_grab + (-0.1f);

    style.Colors[ImGuiCol_ComboBg] = light_blue;
    style.Colors[ImGuiCol_CheckMark] = regular_blue;

    style.Colors[ImGuiCol_SliderGrab] = regular_blue;
    style.Colors[ImGuiCol_SliderGrabActive] = regular_blue;

    style.Colors[ImGuiCol_Button] = button_color;
    style.Colors[ImGuiCol_ButtonHovered] = button_color + 0.1f;
    style.Colors[ImGuiCol_ButtonActive] = button_color + (-0.1f);

    style.Colors[ImGuiCol_TitleBg] = title_color;
    style.Colors[ImGuiCol_TitleBgCollapsed] = title_color;
    style.Colors[ImGuiCol_TitleBgActive] = header_color;
}

void GuiView::ShowCalibrationResults(void)
{
    auto flags = ImGuiWindowFlags_NoResize |
        ImGuiWindowFlags_NoMove |
        ImGuiWindowFlags_NoCollapse |
        ImGuiWindowFlags_NoTitleBar;

    ImGui::PushFont(font_18);
    ImGui::PushStyleColor(ImGuiCol_WindowBg, transparent);
    
	ImGui::SetNextWindowPos({ (float)default_control_panel_width + 15, (float)m_winHeight / 3 });
	ImGui::SetNextWindowSize({ (float)(m_winWidth - default_control_panel_width - 25), (float)(m_winHeight * 15 / 16 - default_log_height) });
		
    ImGui::Begin("calibrationresults_popup", nullptr, flags);

    switch (m_CalibrationStatus)
    {
    case CALIBRATION_STATUS_SUCCESSFUL:
        ImGui::TextColored(green, "Calibration Successful");
		ImGui::TextWrapped("Results updated to the device. Please check depth quality with Intel RealSense Quality Tool or other tools that fit your product usage. If necessary, rerun the calibration until satisfactory result is achieved.");
        break;

    case CALIBRATION_STATUS_FAILED:
        ImGui::TextColored(redish, "Calibration Failed");
        ImGui::TextColored(regular_text, "Calibration was not able to complete.");
        break;

    }

	if (ImGui::Button("OK"))
	{
		m_CalibrationStatus = CALIBRATION_STATUS_NONE;
	}

    ImGui::End();
    ImGui::PopStyleColor();
    ImGui::PopFont();
}

void GuiView::ShowDemoHelpMsg()
{
	unsigned int total_steps = 0;
	char *help_msg = "";
	const char *demo_steps[12] = {};

	if (m_targeted)
	{
		total_steps = TARGETED_DEMO_STEPS;

		help_msg =
			"Targeted calibration requires a special target printed on paper or displayed on phone screen with "
			"the \"Intel RealSense Dynamic Target Tool\" app on iPhones and android phones. Target precision is critical to calibration accuracy. "
			"Please take time to ensure its correctness.\n"
			"\n"
			"- Printed Target: A print target image print-target-fixed-width.pdf (v2.1), is supplied in the calibration tool package under the target directory, "
			"for example, C:\\CalibrationToolAPI\\<version>\\target. "
			"Print the target on 8.5 x 11 inches letter size pager without scaling, check the physical target image size on paper and verify key feature dimensions as outlined "
			"in print-target-fixed-width.pdf, setup the printed target on a flat surface so that the bars are vertical (use a roller or some other object, to ensure the target "
			"is flat on the surface. Tape the printed target on the flat surface after confirming that the target is flat on the surface.)\n"
			"\n"
			"- Phone Target: The \"Intel RealSense Dynamic Target Tool\" app is "
			"available on Apple App Store and Google Play, search \"dynamic target tool\" or \"realsense\" on the stores to "
			"find and install the app on your phone.\n"
			"\n"
			"The demo below highlights the targeted calibration process. For details, please refer to \"Targeted Calibration\" and \"Intel RealSense Dynamic Calibration Target "
			"Setup\" sections in User Guide for Intel RealSense Depth Module D400 Series Software Calibration Tool.\n"
            "\n"
			;

		demo_steps[0] =
			"OVERVIEW\n"
			"Targeted calibration requires setting up a special target either printed on paper or displayed on phone screen "
			"through \"Intel RealSense Dynamic Target Tool\" app on iPhones or Android phones. The process goes through multiple phases to correct various "
			"calibration errors on the device, including rectification and scale in depth and depth to RGB on devices with RGB. Full details are documented in "
			"release notes and user guide. Please be sure spend time to review and ensure proper process is followed."
			"\n"
			;

		demo_steps[1] =
			"TARGET SETUP - TARGET HIGHLIGHTS\n"
			"The target contains a graphical pattern with fixed width stripped bars in the middle and small checker blocks on the top and bottom. "
			"The pattern displayed on phone depends on the screen size. The larger phones display more and longer bars than the smaller phones. The pattern used in "
			"printed target is same as the pattern displayed on iPhone 7 plus. The width of the bars in the middle (highlighted in green excluding the ones on the left and right "
			"edges) are fixed to 10 mm and the length of the bars are integral number of 10 mm, i.e., either 90mm, 100mm, 110mm, or 120mm, etc. The user's guide has detailed "
			"instruction in checking these dimensions in the target pattern printed on paper or displayed on phone to ensure accuracy."
			"\n"
			;

		demo_steps[2] =
			"TARGET SETUP - PRINTED TARGET\n"
			"A target image print-target-fixed-width.pdf v2.1 is supplied in the calibration tool installation under the target directory. "
			"Print it on 8.5x11 inch letter size paper with NO scaling, verify physical dimensions as outlined in the target, then set it up on a "
			"flat surface, for example, gator board (5mm, available in art supply stores) or foam-core (0.25\" or 3/16\", available in most "
			"art stores and major retailers), so that the bars are vertical (use a roller or some other object to ensure the target, "
			"especially the graphical bar chart portion, is completely flat on the surface, and glue the printed target on the flat surface using either glue stick or spray adhesive "
			"like 3M Super 77 spray adhesive).\n"
			"\n"
			;

		demo_steps[3] =
			"TARGET SETUP - PHONE TARGET\n"
			"The target can also be displayed on phone screens through the \"Intel RealSense Dynamic Target Tool\" app. The app is available on Apple App Store and Google Play. "
			"Search \"dynamic target tool\" or \"realsense\" on the stores to find and install it on your iPhone or Android phone. iPhones 5, 5s, 6, 6s, 6s+, 7, 7+, 8, 8+ and iPhone X "
			"are supported. Andorid phones Samsung Galaxy S8 plus, Samsung Galaxy S7, Google Nexus 5, LG G4, Notes 5, and Motorola XT1650 are also supported. Please refer to the User "
			"Guide for list of supported phones. The phone calibration portion of this software including the phone app is currently supported as beta feature and may contain a number "
			"of known or unknown issues. Please report issues found to the RealSense development team via https://realsense.intel.com/community/"
			"\n"
			;

		demo_steps[4] =
			"TARGET SETUP - POSITION AND ORIENTATION\n"
			"Position the device 600 - 850 mm away pointing to the target so that the bars in target is approximately vertically oriented in field of view. Through out the calibration process, relative movement between the "
			"device and the target is required. Depends on your usage case and product restriction, you can either put the target on a fixed stand and move the device, or put the device on a fixed tripod and move the target instead. The "
			"relative position and orientation requirement is the same."
			"\n"
			;

		demo_steps[5] =
			"TARGET SETUP - AVOID REFLECTION\n"
			"Avoid reflections from environment - lighting reflection on phone screens severe impacts targeted calibration effectiveness. When a phone target is used where lighting "
			"reflection on phone glass screen presents, for example, outdoor under bright sunlight, or indoor with lots of lights surrounded, calibration performance degrade. In severe "
			"cases, calibration may not converge (as impacted images thrown away and target cannot be found) and it takes longer to complete or no result may be reached.\n"
			"\n"
			;

		demo_steps[6] =
			"CONNECT DEVICE AND START CALIBRATION\n"
			"Connect and select the device to calibrate. Click \"Start Calibration\" to start the process which involves 2 or 3 phases depends on SKU. Follow on-screen instruction to finish each phase in a sequential order. If phone target is used, be careful relections on the phone screen may interfere with the calibration process and the appilication may not be able to "
			"identify the target. Try to position the phone so that reflections from lighting and other surroundings can be avoided. By default, the application will adjust exposure automatically to fit into user's environment. If preferred, you can disable the "
			"automatic exposure search in the \"Advanced Settings\" and manually adjust the exposure setting before start the calibration.\n"
			;

		demo_steps[7] =
			"RECTIFICATION PHASE\n"
			"The rectification phase rectifies the left and right images and prepare for the next phase where scale error in depth can be corrected. Position the device 600 - 850 mm away pointing to the target so that the bars in target is approximately vertically oriented in field of view. A block of shaded blue squares are presented in the middle of the window. "
			"Move the device or target slowly so that the black and white small squares and bars in the target chart overlaps the blue squares in the window. The blue squares will start clearing up. Repeat the proces until all blue squares are cleared. "
			"Throughout the process, the calibration application keeps track of the target, if it fails detecting the target, if automatic exposure search is enabled, it will loop through exposures to search for the target. To the user, it appears the lighting goes from bright to dark and to bright again if no target is present or failed to detect due to other reasons like reflection "
			"interference. This is expected. If it loops through exposure cycles and still cannot detect the target, possibly due to reflections on phone screen or too close or too far away from the target, try to reposition the device or the target and try again.\n"
			;

		demo_steps[8] =
			"SCALE PHASE\n"
			"The scale phase corrects the depth scale errors. It require capturing 15 images of the target in various positions. Position the device 600 - 850 mm away pointing to the target so that the bars in target is approximately vertically oriented in field of view. "
			"Move the device or target slowly. No specific pattern of the movement is required. Also, it does not need to be in the same plane. Random position and distance in the range is fine. Once a position is accepted, a blue rectangle hightlights that target position "
			"will be drawn in the window. The new position should be those that does not have images previously captured. The app checks that and make sure the new position is unique. The green process bar at the bottom shows progress. Repeat the process until it finishes. "
			"At end of the scale phase, the calibration results of rectification and scale phases are updated to the device no matter if there is a RGB phase or not."
			;

		demo_steps[9] =
			"RGB PHASE (ONLY ON DEVICES WITH RGB)\n"
			"The RGB phase calibrates the depth to RGB for UV mapping and only available on devices with RGB, for example, D415 and D435. This phase is very similar to the scale phase and also requires capturing 15 images of the target at various positions. "
			"Position the device 600 - 850 mm away pointing to the target so that the bars in target is approximately vertically oriented in field of view. Be sure to move the device or target very slowly. At end of the RGB phase, the additional RGB calibration result is "
			"updated to the device. At this point, both left/right depth and depth-RGB are calibrated and the actual corrections are highlighted in the output area in terms of degrees of rotation angles."
			"\n"
			;

		demo_steps[10] =
			"VERIFY CALIBRATION RESULTS\n"
			"After the calibration is finished and results updated to the device. It's important to verify good calibration results by checking depth quality with Intel RealSense Quality Tool or other "
			"tools that fit your product usage. If necessary, rerun the calibration until satisfactory result is achieved."
			;
	}
	else
	{
		total_steps = TARGETLESS_DEMO_STEPS;

		 help_msg =
			"Targetless Calibration - calibrating device without a target. \n"
			 "- Pros: Simplicity, no calibration target is needed. Fits with user cases where calibrating with a target may not be feasible. \n"
			 "- Cons: Calibrates left/right depth but not RGB. Generally less accurate and less consistent than Targeted Calibration. \n"
			 "The demo below highlights the targetless calibration process. For details, please refer to \"Target-less Calibration\" section "
			 "in User Guide document for Intel RealSense Depth Module D400 Series Software Calibration Tool.\n"
			 "\n"
			 ;


		demo_steps[0] =
			"OVERVIEW\n"
			"Targetless calibration does not require dedicated target. Simply select a scene that has textures and good lighting, plug in the device, run the app, point the camera to the scene and start calibration. Please note, "
			"targetless calibration does not calibrate RGB on devices with RGB, for example, D415 and D435. Targeted calibration should be used if RGB calibration is desired. Full detail is documented in "
			"release notes and user guide. Please be sure spend time to review and ensure proper process is followed. "
			;

		demo_steps[1] =
			"SCENE SELECTION - SAMPLE SCENE\n"
			"Targetless calibration works better in scenes with lots of textures and good lighting condition, for example, boxes with big printed texts, signage, or office scenes. "
			"\n"
			;

		demo_steps[2] =
			"SCENE SELECTION - SAMPLE SCENE\n"
			"If the device is equiped with a laser projector, for example, D410, D415, D430, and D435, then it can also work in scenes with less textures like office walls. In those cases, the laser projector will be turned "
			"on during calibration and will project artifictial textures onto the wall to assist with the calibration."
			"\n"
			;

		demo_steps[3] =
			"SCENE SELECTION - SCENES TO AVOID\n"
			"In order to achieve consistent calibration results, some scenes should be avoided. For example, scenes with the checkerboard pattern or targeted calibration target in the background. Scenes "
			"with very dark lighting conditions or scenes with very bright lights should also be avoided. "
			"\n"
			;

		demo_steps[4] =
			"CONNECT DEVICE and START CALIBRATION\n"
			"Plug in the device, click the \"Start Calibration\" button to get started. Position the device around one meter or more away directly facing the scene. Do not position the device too close to the scene. "
			"\n"
			;

		demo_steps[5] =
			"FOLLOW ON-SCREEN INSTRUCTIONS\n"
			"The app window starts with full of shaded blue squares."
			"\n"
			;

		demo_steps[6] =
			"FOLLOW ON-SCREEN INSTRUCTIONS\n"
			"Move the device very slowly point to textures in the scene and overlap the textures with the blue blocks. The blue squares will start clearing. "
			"After majority of the squares are cleared and the remaining blue blocks may be hard to clear due to lack of matched textures. At this "
			"point, the app will focus device exposure to those remaining blocks so those areas will be exposed properly for better chance of matching texture features. The brightness may experience quick "
			"changes and appears flashing. This is expected. Please continue until all blue squares are cleared."
			"\n"
			;

		demo_steps[7] =
			"VERIFY CALIBRATION RESULTS\n"
			"After the calibration is finished and results will be updated to the device. It's important to verify good calibration results by checking depth quality with Intel RealSense Quality Tool or other "
			"tools that fit your product usage. If necessary, rerun the calibration until satisfactory result is achieved."
			"\n"
			;
	}


	auto flags = ImGuiWindowFlags_NoResize |
		ImGuiWindowFlags_NoMove |
		ImGuiWindowFlags_NoCollapse |
		ImGuiWindowFlags_NoTitleBar;

	ImGui::PushFont(font_18);
	ImGui::PushStyleColor(ImGuiCol_WindowBg, transparent);
	ImGui::SetNextWindowPos({ (float)default_control_panel_width + 15, (float)m_winHeight / 25 });
	ImGui::SetNextWindowSize({ (float)(m_winWidth - default_control_panel_width - 25), (float)(m_winHeight * 15 / 16 - default_log_height) });
	ImGui::Begin("modehelp_popup", nullptr, flags);

	ImGui::PushStyleColor(ImGuiCol_Text, regular_text);

	glEnable(GL_TEXTURE_2D);

	char* buttontext = "";

	if (showdemo)
	{
		buttontext = "Close Demo";
	}
	else
	{
		ImGui::TextWrapped(help_msg);
		buttontext = "Show Demo";
	}

	if (ImGui::Button(buttontext))
	{
		showdemo = !showdemo;
	}

	glEnable(GL_TEXTURE_2D);

	if (showdemo)
	{
		ImGui::SameLine(200);
		bool backbuttonclicked = false;
		
		if (step > 0)
		{
			backbuttonclicked = ImGui::Button("Back");
		}

		float demo_display_height = m_winHeight * 0.4;
		float demo_display_width = demo_display_height * DEMO_IMG_WIDTH / DEMO_IMG_HEIGHT; // maintain image aspect ratio

		ImGui::SameLine(200 + demo_display_width + 52);

		bool nextbuttonclicked = false;
		
		if (step < total_steps - 1)
		{
			nextbuttonclicked = ImGui::Button("Next");
		}

		if (backbuttonclicked)
		{
			if (step > 0)
				step--;
		}

		if (nextbuttonclicked)
		{
			if (step < total_steps - 1)
				step++;
		}

		step = step % total_steps;

		GLuint demo_texture_id = 0;

		if (m_targeted)
		{
			demo_texture_id = targeted_demo_texture_id[step];
		}
		else
		{
			demo_texture_id = targetless_demo_texture_id[step];
		}

//  	    std::string msg = "demo texture id [" + std::to_string(step)  + "] = " + std::to_string(demo_texture_id);
//		m_appLog.AddLog(msg);
		glBindTexture(GL_TEXTURE_2D, targeted_demo_texture_id[step]);

		ImGui::SameLine(250);
		ImGui::Image((GLuint*) demo_texture_id, ImVec2(demo_display_width, demo_display_height));

		ImGui::TextWrapped(demo_steps[step]);
	}
	else
	{
		// reset to first demo slide
		step = 0;
	}

	glBindTexture(GL_TEXTURE_2D, 0);
	glDisable(GL_TEXTURE_2D);

	ImGui::PopStyleColor();
	ImGui::End();

	ImGui::PopStyleColor();
	ImGui::PopFont();
}


void GuiView::AddLog(std::string msg)
{
    m_appLog.AddLog(msg);
}

void GuiView::ShowUsbError()
{
    auto flags = ImGuiWindowFlags_NoResize |
        ImGuiWindowFlags_NoMove |
        ImGuiWindowFlags_NoCollapse |
        ImGuiWindowFlags_NoTitleBar;

    ImGui::PushFont(font_18);
    ImGui::PushStyleColor(ImGuiCol_WindowBg, transparent);

    ImGui::SetNextWindowPos({ (float)default_control_panel_width + 15, (float)m_winHeight / 3 });
    ImGui::SetNextWindowSize({ (float)(m_winWidth - default_control_panel_width - 25), (float)(m_winHeight * 15 / 16 - default_log_height) });

    ImGui::Begin("usb_error", nullptr, flags);

    ImGui::TextColored(redish, "USB2 device not supported.");

    string err_msg = rs_convert_err_to_string(DC_ERROR_DEVICE_USB2);
    ImGui::TextWrapped(err_msg.c_str());

    ImGui::End();
    ImGui::PopStyleColor();
    ImGui::PopFont();
}
