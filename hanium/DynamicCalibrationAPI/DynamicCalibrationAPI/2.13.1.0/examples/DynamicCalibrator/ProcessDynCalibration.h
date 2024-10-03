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

#ifdef _WIN32
#include <Windows.h>
#endif

#include <functional>
#include <chrono>
#include "DSDynamicCalibration.h"
#include "Stopwatch.h"
#include "FileWrite.h"

using namespace std::chrono;
using namespace DynamicCalibrationAPI;

namespace DynamicCalibrator
{
#define DC_REJECTED_MAX             20
#define DC_REJECTED_STEP            10

#define DC_SETPOINT_LOW             300
#define DC_SETPOINT_HIGH            1200
#define DC_SETPOINT_STEP            100

#define PHONELOC_DIM    8
#define AE_ROI_THRESHOLD_SCORE 0.85f
#define MAX_SCALE_IMAGES    15
#define MAX_COLOR_IMAGES    15

// Passive, standard FOV (RS400)
#define SCENE_HAS_FEATURES_THRESHOLD_SCORE_PSR 0.075f
// Active, standard FOV (RS410)
#define SCENE_HAS_FEATURES_THRESHOLD_SCORE_ASR 0.15f
// Passive, wide FOV (RS420)
#define SCENE_HAS_FEATURES_THRESHOLD_SCORE_PWG 0.25f
// Active, wide FOV (RS430)
#define SCENE_HAS_FEATURES_THRESHOLD_SCORE_AWG 0.35f

    class CaptureManager;
    class MainView;

    class ProcessDynCalib
    {
    public:
        ProcessDynCalib(MainView* view, CaptureManager* captureManager, int saveFrame, bool bGetRectErrorOnly);
        virtual ~ProcessDynCalib();

        int InitDynCalParams(int width, int height, DSDynamicCalibration::CalibrationMode calibMode, int width_rgb, int height_rgb, bool bAutoExposure, int aePoint, int sku, int sweep, bool aligned, bool active, int max_num_images, bool ignore_borders, int loglevel);
		void SetSweepMode(int sweep);

        void ProcessFrames(const void *leftImage, const void *rightImage,
            const void *mainImage, const uint64_t timeStamp);

        void* OnIdle();
        bool Render(int winWidth, int winHeight);

        void StopProcessing();

        bool InitScaleCalibration();
		bool ContinueCalibrationToScalePhase();
		bool StartScaleCalibrationOnly();

        int InitRgbCalibration();

    private:
        void DynCalAddImagesSuccess();
        void DynCalAddImagesFailure(int ImageStatus);

        void SetGridFill(const DynamicCalibrationAPI::DSDynamicCalibration::GridLevel* gridLevels,
                         int gridWidth, int gridHeight, bool useAEROI,
                         DynamicCalibrationAPI::DSDynamicCalibration::GridFill* gridFills,
                         int& aeroiX, int& aeroiY);

        void UpdateSetPointValue();
        void UpdateRgbBrightnessValue();

        bool SceneHasFeatures(const DynamicCalibrationAPI::DSDynamicCalibration::GridFeatures* gridFeatures,
            int gridWidth, int gridHeight);

        std::string TranslateStatusToText(int status);

        void ProcessScaleFrames(const void *leftImage, const void *rightImage, const void *depthImage,
            const uint64_t timeStamp);

        void* ScaleOnIdle();
        bool  ScaleRender(int winWidth, int winHeight);

        void ProcessRgbCalibFrames(const void *leftImage, const void *rightImage, const void *rgbImage,
            const uint64_t timeStamp);

        void* RgbCalibOnIdle();
        bool  RgbCalibRender(int winWidth, int winHeight);

        int UpdateCalibrationTables(std::string msg);

    private:
        MainView* m_mainView;
        CaptureManager* m_captureManager;
        DynamicCalibrationAPI::DSDynamicCalibration *m_dcApi;

        void *m_image;
        void *m_colorImage;

        const DynamicCalibrationAPI::DSDynamicCalibration::GridLevel* m_gridLevels;
        DynamicCalibrationAPI::DSDynamicCalibration::GridFill* m_gridFills;
        const DynamicCalibrationAPI::DSDynamicCalibration::GridFeatures* m_gridFeatures;

        int m_width;
        int m_height;

        int m_width_rgb;
        int m_height_rgb;

        int m_gridWidth;
        int m_gridHeight;

        bool m_bROIEnabled = false;
        int m_ROIResetCout = 0;
        int m_ExposureLeftEdge;
        int m_ExposureRightEdge;
        int m_ExposureTopEdge;
        int m_ExposureBottomEdge;
        int m_Region;

        bool m_bTargeted;
        bool m_bWarmUpDone;
        int m_status;
        int m_AESweep;
        unsigned int m_ae_setpoint;
        bool m_autoExposure;

        int m_numFramesReceived;
        std::chrono::high_resolution_clock::time_point last_frame_time;

        int m_RejectedThreshold;
        int m_numFramesProcessed;
        int m_framesRejected;
        int m_rgbFramesRejected;
        int m_imageNum;
        bool m_gridIsFull;
        bool m_bAEenabled;
        bool m_SceneHasFeatures;
        int m_sku;

        int m_saveFrame;
        bool m_bGetRectErrorOnly;

        bool m_scaleStarted;
        int m_scaleFrameCount;
        bool m_scalePhaseCompleted;
        int m_frameCountSuccess;

		bool m_scaleonly;

        bool m_bRgbCalib;
        int m_rgbFrameCount;
        bool m_rgbPhaseCompleted;
        int m_rgbBrightnessMin;
        int m_rgbBrightnessMax;
        int m_rgbBrightnessDefault;
        int m_rgbBrightness;

        float AckPhoneLoc[MAX_SCALE_IMAGES][PHONELOC_DIM];

        float m_phoneLoc[PHONELOC_DIM];

        time_point<high_resolution_clock> m_startTime, m_lastImgTime;
        milliseconds m_warmupTime;
        milliseconds m_passedTime;

        Stopwatch m_elapsedTime;
        Stopwatch m_prevGetRectErrorTime;

        FileWrite m_fileWrite;

#ifdef _WIN32
        CRITICAL_SECTION m_mutexCamFrame;
        CONDITION_VARIABLE m_cvCamFrameReady;
#else
        pthread_mutex_t m_mutexCamFrame;
        pthread_cond_t m_cvCamFrameReady;
#endif
    };
}
