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

#include <string>
#include <chrono>
#include <thread>

#include "SerialPortInterface.h"
#include "DSDynamicCalibration.h"
#include "Stopwatch.h"

namespace GIMBAL
{
	//
	enum CalibrationState
	{
		CS_INIT = 0,
		CS_RECT_WARMUP = 1,
		CS_RECT = 2,
		CS_SCALE_WARMUP = 3,
		CS_SCALE = 4,
		CS_RGB_WARMUP = 5,
		CS_RGB = 6,
		CS_FINISH = 7
	};

    // Gimbal movement direction
    enum MovementDirection
    {
        MD_TOP_LEFT = 0,
        MD_TOP_RIGHT = 1,
        MD_BOTTOM_LEFT = 2,
        MD_BOTTOM_RIGHT = 3,
    };

    class Gimbal
    {
        enum ModeType
        {
            ScanRight,
            ScanUp,
            ScanLeft,
            ScanDown,
            ScanFinish,
            Elimination
        };

    public:
        Gimbal(std::string serialPort);
        ~Gimbal();
        // Suggests next move for the gimbal based on the collected features
        void SuggestNextMove(const DynamicCalibrationAPI::DSDynamicCalibration::GridLevel* gridLevels,
            int gridWidth, int gridHeight, bool bSceneHasFeatures);

        // Suggests next move for the gimbal based on the features in the current frame
        void SuggestNextMove(const DynamicCalibrationAPI::DSDynamicCalibration::GridFeatures* gridFeatures,
            int gridWidth, int gridHeight, bool bSceneHasFeatures);

		void EnableVerticalMove(bool on);
		void EnableTargetMode(bool on);
		void TargetNextMove();

		void SetDeviceWarmUP(bool warmingup);
		void UpdateCalibrationState(CalibrationState cs);

        void Run(void);
        std::string GetErrorMsg(void);
        bool IsConnected(void);

    private:
        std::string ReadLine(void);
        void HandleMove(void);
        void HandleElimination(void);
        void SuggestNextMove(const int* grid, int gridWidth, int gridHeight);
        std::string string_format(const char * format, ...);

		void HandleMoveTargeted(void);
		void HandleWarmUp(void);

    private:
        const float AxisRange[2][2] = { { -165.0f, 165.0f }, { -90.0f, 15.0f } };

		const int TargetModeSpeed = 3;
		const int SlowSpeed = 10;
		const int FastSpeed = 10;

		bool VerticalMoveEnabled = true;
		bool Targeted = false;
		bool DeviceInWarmUp = false;

		CalibrationState mCS;

        const float EliminationModeBoundary[2] = { 90.0f, 25.0f };
        const float EliminationModeStep[2] = { 6.0f, 2.5f };
        const float EliminationModeReturnMargin[2] = { 18.0f, 7.5f };
        const int EliminationModeMaxReturns = 3;

        float ScanModeRange[2][2] = { { -135.0f, 135.0f },{ -45.0f, 0.0f } };
        float ScanModeStep[2] = { 45.0f, 45.0f };

        const float CmdPauseTimeMs = 100.0f;

        const int WaitInMs = 20;

        SerialPortInterface *mComport;
        bool mExit;
        std::string mErrorMessage;
        bool mProcessFailure;
        Stopwatch *mWatch;

        double mLastCmdTimeMs;
        bool mIdling, mFastMode;
        bool mTakenCharacterizationShot;

        int mEliminationModeReturnsLeft;
        ModeType mEliminationEntryMode;
        ModeType Mode;

        bool m_SceneHasFeatures;
        MovementDirection m_mvDir;

        float mCurrentPoisition[2] = { 0.0f, 0.0f };
        float mEliminationModeBasePosition[2] = { 0.0f, 0.0f };
        float mEliminationModeBaseOffset[2] = { 0.0f, 0.0f };
        std::thread m_RunThread;
    };
}
