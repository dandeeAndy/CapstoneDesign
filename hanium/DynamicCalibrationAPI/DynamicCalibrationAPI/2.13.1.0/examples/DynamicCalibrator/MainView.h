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

#include <GL/freeglut.h>

#include "CaptureManager.h"
#include "Options.h"
#include "Gimbal.h"
#include "rs_utils.h"

using namespace GIMBAL;

namespace DynamicCalibrator
{
    enum TEXT_ALIGN_FLAGS {
        // Must all be negative values!
        TEXT_ALIGN_CENTER = -1,
        TEXT_ALIGN_LEFT = -2,
        TEXT_ALIGN_RIGHT = -3,
        TEXT_ALIGN_TOP = -4,
        TEXT_ALIGN_BOTTOM = -5,
    };

    typedef struct tagCOLOR
    {
        int R;
        int G;
        int B;
        int A;
    } COLOR;

    typedef struct tagRECTANGLE
    {
        double left;
        double top;
        double right;
        double bottom;
    } RECTANGLE;

    typedef struct tagPOINT_D
    {
        double x;
        double y;
    } POINT_D;

    enum RUNNING_STATUS_ENUM {
        STATUS_NOT_STARTED,
        STATUS_RUNNING,
    };

    enum AE_SWEEP_MODE {
        AE_SWEEP_MANUAL  = 0,
        AE_SWEEP_AUTO  = 1
    };

    class MainView
    {
    public:
        MainView();
        virtual ~MainView();

        /* render */
        void SetColorImages(void *colorImage) {
            m_colorImage = colorImage;
        };
        void RenderImage();
        void RenderColorImage();
        void BlendBlocks(std::vector<RECTANGLE> blocks, std::vector<COLOR> colors);
        void RenderLines(std::vector<POINT_D> points, COLOR color, int lineWidth);
        void RenderText(int x, int y, void *font, const char* message, float r,
            float g, float b, float a);

        /* redisplay */
        void PostRedisplay() { glutPostRedisplay(); }
        /* Get error code */
        int GetErrorCode() { return m_errorCode; }

        void OnIdle();
        void OnReShape(int width, int height);
        void OnClose() {};

        /* Initialization */
        virtual int Initialize(void) = 0;

        /* render last frame */
        void RenderLastFrame() { OnDisplay(); }

        /* Update calibration tables*/
        virtual int UpdateCalibrationTablesComplete(std::string msg, bool bUpdated) = 0;

        /* Handling error message */
        virtual void ErrorHandling(int errorCode) = 0;

        virtual void OnDisplay() = 0;
        virtual void OnKeyBoard(unsigned char key, int x, int y) = 0;

        virtual void AddLog(std::string msg) = 0;

        std::string GetOutputDir() { return m_dir; }

        void SetCmdOptions(Options& CmdOptions)
        {
            m_CmdOptions = CmdOptions;

            // Pass the readonly command line options to corresponding
            // class data members:
            SetOptions();
        };

	public:
		Gimbal *pGimbal;

    protected:
        void InitializeGL(void *viewClass);
        int StartCapture(int idx);

        bool IsFwVersionSupported(camera_info caminfo);
        bool IsUsb2(camera_info caminfo);
        bool IsUsb3(camera_info caminfo);
        void SetOptions(void);
        void SetViewport(GLint x, GLint y, GLsizei width, GLsizei height);
        void GetExposureValue(int idx);

        void ConvertYUY2ToRGBA(const uint8_t* image, int width, int height, uint8_t* output);

        void CreateLogDirectory(std::string serial);

    protected:
        CaptureManager* m_captureManager{nullptr};
        std::vector<camera_info> m_cameras;
        std::string m_sn;

        int m_errorCode;

        void *m_image;
        void *m_colorImage;

        // Texture
        GLuint m_texture;

        GLint m_viewport[4];

        int m_runningStatus;

		int  m_aesweepmode;

        int  m_aeSetpoint;
		int  m_aeSetpointMin;
		int  m_aeSetpointMax;
		int  m_aeSetpointDefault;

		int  m_aeRgbBrightness;
		int  m_aeRgbBrightnessMin;
		int  m_aeRgbBrightnessMax;
		int  m_aeRgbBrightnessDefault;
		
		int  m_useLaser;

        int m_width;
        int m_height;

        int m_width_rgb;
        int m_height_rgb;

        int m_winWidth;
        int m_winHeight;

        unsigned int m_timeout;

        Options m_CmdOptions;

		int m_calibration_mode;
		bool m_targeted;

		bool m_scaleCalibOnly;
        bool m_rgbCalib;
		bool m_hybrid;

		bool m_skiprgb;


		bool m_device_target_same_orientation;
		int max_target_images;

		bool m_ignore_borders;

        GLuint m_textures[2];
        std::unique_ptr<uint32_t[]> m_rgbImage;

        bool m_autoExposureEnable;
        int  m_depthExposure;
        int  m_depthExposureMin;
        int  m_depthExposureMax;
        int  m_colorExposure;
        int  m_colorExposureMin;
        int  m_colorExposureMax;

        std::string m_dir;
        std::ofstream m_logFile;
        int m_loglevel;

        Stopwatch m_elapsedTime;
    };
}
