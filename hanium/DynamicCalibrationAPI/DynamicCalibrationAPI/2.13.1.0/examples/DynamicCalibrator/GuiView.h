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

#ifndef _GUIVIEW_H_
#define _GUIVIEW_H_

#include <vector>
#include <GL/freeglut.h>

#include <iostream>
#include "imgui.h"
#include "imgui_impl_glut.h"
#include "CaptureManager.h"
#include "Stopwatch.h"

#include "MainView.h"

#define TARGETED_DEMO_STEPS       11        // number of demo images for targeted calibration
#define TARGETLESS_DEMO_STEPS      8        // number of demo images for targetless calibration

#define DEMO_IMG_WIDTH           640        // demo image width in pixels
#define DEMO_IMG_HEIGHT          360        // demo image height in pixels

namespace DynamicCalibrator
{

    enum CALIBRATION_STATUS_ENUM {
        CALIBRATION_STATUS_FAILED = 0,
        CALIBRATION_STATUS_SUCCESSFUL,
        CALIBRATION_STATUS_NONE,
    };

    inline ImVec4 from_rgba(uint8_t r, uint8_t g, uint8_t b, uint8_t a)
    {
        return ImVec4(r / (float)255, g / (float)255, b / (float)255, a / (float)255);
    }

    inline ImVec4 operator+(const ImVec4& c, float v)
    {
        return ImVec4(
            std::max(0.f, std::min(1.f, c.x + v)),
            std::max(0.f, std::min(1.f, c.y + v)),
            std::max(0.f, std::min(1.f, c.z + v)),
            std::max(0.f, std::min(1.f, c.w))
        );
    }

    static const ImVec4 regular_blue = from_rgba(0, 0x71, 0xc5, 255);
    static const ImVec4 black = from_rgba(0, 0, 0, 255);
    static const ImVec4 transparent = from_rgba(0, 0, 0, 0);
    static const ImVec4 white = from_rgba(255, 255, 255, 255);
    static const ImVec4 green = from_rgba(0, 255, 0, 255);
    static const ImVec4 regular_text = from_rgba(0xc3, 0xd5, 0xe5, 0xff);
    static const ImVec4 scrollbar_bg = from_rgba(14, 17, 20, 255);
    static const ImVec4 scrollbar_grab = from_rgba(54, 66, 67, 255);
    static const ImVec4 dark_grey = from_rgba(36, 44, 51, 255);
    static const ImVec4 light_blue = from_rgba(0x3e, 0x4d, 0x59, 0xff);
    static const ImVec4 redish = from_rgba(255, 46, 54, 255);
    static const ImVec4 button_color = from_rgba(0, 115, 200, 255);
    static const ImVec4 header_color = from_rgba(36, 44, 51, 255);
    static const ImVec4 title_color = from_rgba(27, 33, 38, 255);
    static const ImVec4 output_color = from_rgba(0x09, 0x0b, 0x0d, 255);

	class AppLog
	{
	public:
		AppLog()
		{
			ScrollToBottom = false;
			lines = 0;
			pLogFile = nullptr;
		}

		void SetLogFileStream(std::ofstream* logFile)
		{
			pLogFile = logFile;
		}

		void AddLog(std::string msg)
		{
			std::lock_guard<std::mutex> lock(m);

			if (msg.empty() || (msg == "\n"))
			{
				log.push_back("\n");
			}
			else
			{
				lines++;

				std::string prefix = "#" + std::to_string(lines) + ": ";
				log.push_back(prefix);

				log.push_back(msg);
				log.push_back("\n");
			}

			ScrollToBottom = true;

			if (pLogFile != nullptr)
				*pLogFile << msg << std::endl;
		}

		std::string GetLog(void)
		{
			std::string result;
			std::lock_guard<std::mutex> lock(m);

			for (auto&& l : log) std::copy(l.begin(), l.end(), std::back_inserter(result));

			return result;
		}

		void Show(ImFont* font, float x, float y, float w, float h)
		{
			ImGuiWindowFlags flags = ImGuiWindowFlags_NoResize | ImGuiWindowFlags_NoMove |
				ImGuiWindowFlags_NoSavedSettings | ImGuiWindowFlags_ShowBorders
				| ImGuiWindowFlags_NoCollapse;

			ImGui::PushFont(font);
			ImGui::SetNextWindowPos({ x, y });
			ImGui::SetNextWindowSize({ w, h });
			ImGui::PushStyleVar(ImGuiStyleVar_WindowPadding, ImVec2(0, 0));
			ImGui::PushStyleColor(ImGuiCol_WindowBg, output_color);
			ImGui::PushStyleColor(ImGuiCol_Border, dark_grey);

			ImGui::Begin("Output", nullptr, flags);
			ImGui::PushStyleColor(ImGuiCol_Text, regular_text);

			ImGui::TextUnformatted(GetLog().c_str());

			if (ScrollToBottom)
			{
				ScrollToBottom = false;
				ImGui::SetScrollHere(1.0f);
			}

			ImGui::PopStyleColor();
			ImGui::End();

			ImGui::PopStyleColor();
			ImGui::PopStyleColor();
			ImGui::PopStyleVar();
			ImGui::PopFont();
		}

	private:
		std::mutex m;
		std::vector<std::string> log;
		bool ScrollToBottom;
		unsigned int lines;
		std::ofstream* pLogFile;
	};

    class GuiView : public MainView
    {
    public:
        GuiView();
        virtual ~GuiView();

        /* Initialization */
        int Initialize(void);

        /* Update calibration tables*/
        int UpdateCalibrationTablesComplete(std::string msg, bool bUpdated);

        /* Handling error message */
        void ErrorHandling(int errorCode);

        void OnDisplay();
        void OnKeyBoard(unsigned char key, int x, int y);

        void AddLog(std::string msg);
        void ShowUsbError();

    private:
        void StartCalibration();
        void HotplugHandler();
        void CheckButtonClick();
        void ShowUI();
        void ShowDeviceOptions();
        void ShowAdvancedDeviceOptions();
        void ShowDeviceDetails(void);
        void EasyTheming(ImFont*& font_14, ImFont*& font_18);
        void ShowCalibrationResults();
        void ShowDemoHelpMsg(void);

    private:
        int  m_devIdx;
        int  m_devIdxDummy;
        bool m_bPlugMsgInShow;

        bool m_showAdvancedOptions;

        AppLog m_appLog;
        ImFont* font_18;
        ImFont* font_14;
        CALIBRATION_STATUS_ENUM m_CalibrationStatus;

        std::string m_prevSerial;

        bool m_bNeedToRefresh;

        int default_control_panel_width = 280;
        int default_log_height = 100;
        bool m_mouseClicked = true;

		bool showdemo;
		unsigned int step;

		GLuint targeted_demo_texture_id[TARGETED_DEMO_STEPS];
		GLuint targetless_demo_texture_id[TARGETLESS_DEMO_STEPS];
    };
}

#endif // _GUIVIEW_H_
