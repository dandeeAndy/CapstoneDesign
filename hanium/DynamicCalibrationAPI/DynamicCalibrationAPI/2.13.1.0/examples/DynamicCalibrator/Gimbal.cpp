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

#include "Gimbal.h"
#include "SerialPortImpl.h"

#include <algorithm>
#include <thread>
#include <iostream>
#include <cmath>

#include <stdarg.h>

using namespace std;
using namespace GIMBAL;
using namespace DynamicCalibrationAPI;

Gimbal::Gimbal(string serialPort)
{
    mProcessFailure = false;
    mErrorMessage = "";
    mWatch = nullptr;
    mLastCmdTimeMs = 0.0f;
    mIdling = false;
    mFastMode = false;
    mTakenCharacterizationShot = false;

    mEliminationModeReturnsLeft = 0;
    mEliminationEntryMode = ScanRight;
    Mode = ScanRight;

    m_SceneHasFeatures = false;
    m_mvDir = (MovementDirection)-1;

    mComport = new SerialPort(serialPort);

    if (mComport && mComport->IsConnected())
    {
        mExit = false;
    }
    else
    {
        mExit = true;
        mProcessFailure = true;
        mErrorMessage = "Failed to open serial port (" + serialPort + ") for gimbal!";
        cout << "Failed to open serial port (" + serialPort + ") for gimbal!" << endl;
    }

	VerticalMoveEnabled = true;
	Targeted = false;
	DeviceInWarmUp = false;

	mCS = CS_INIT;
}

Gimbal::~Gimbal()
{
	cout << "cleaning up gimbal setup ... " << endl;

    if (m_RunThread.joinable())
    {
        mExit = true;
        m_RunThread.join();
    }

    if (mComport) delete dynamic_cast<SerialPort *>(mComport);
}

string Gimbal::ReadLine(void)
{
    string ret = "";

    do
    {
        ret = mComport->ReadLine();
    } while ((ret == "") && !mExit);

    return ret;
}

void Gimbal::HandleMove(void)
{
    //GetStatus
    mComport->WriteLine("q");
    string response = ReadLine();

    if (response != "IDLE")
        return;

//	std::this_thread::sleep_for(std::chrono::milliseconds(1000));

	// Set the speed
	mComport->WriteLine(string_format("s 1 %d", SlowSpeed));
	ReadLine();
	mComport->WriteLine(string_format("s 2 %d", SlowSpeed));
	ReadLine();

	//GetStatus
	while (true)
	{
		std::this_thread::sleep_for(std::chrono::milliseconds(WaitInMs));

		// GetStatus
		mComport->WriteLine("q");
		string res = ReadLine();

		if (res == "IDLE")
			break;
	}

//	std::this_thread::sleep_for(std::chrono::milliseconds(1000));

	ScanModeRange[0][0] = -90.0f;
	ScanModeRange[0][1] = 90.0f;
	ScanModeRange[1][0] = -30.0f;
	ScanModeRange[1][1] = 0.0f;

    mIdling = true;

    if ((Mode != Elimination) && !mTakenCharacterizationShot)
        return;

    if (Mode != Elimination)
        mTakenCharacterizationShot = false;

    switch (Mode)
    {
    case ScanRight:
        // See if we need to switch mode after the command
		if ((mCurrentPoisition[0] - 2 * ScanModeStep[0]) <= ScanModeRange[0][0])
		{
			if (VerticalMoveEnabled)
				Mode = ScanUp;
			else
				Mode = ScanLeft;
		}

        // Execute the move
        mCurrentPoisition[0] = std::fmax(mCurrentPoisition[0] - ScanModeStep[0], ScanModeRange[0][0]);
        mComport->WriteLine(string_format("m 1 %.2f", mCurrentPoisition[0]));
        ReadLine();

        mLastCmdTimeMs = mWatch->ElapsedMilliseconds();
        mIdling = false;
        break;

    case ScanUp:
        // See if we need to switch mode after the command
        if ((mCurrentPoisition[1] - 2 * ScanModeStep[1]) <= ScanModeRange[1][0])
            Mode = ScanLeft;

        // Execute the move
        mCurrentPoisition[1] = std::fmax(mCurrentPoisition[1] - ScanModeStep[1], ScanModeRange[1][0]);
        mComport->WriteLine(string_format("m 2 %.2f", mCurrentPoisition[1]));
        ReadLine();
        mLastCmdTimeMs = mWatch->ElapsedMilliseconds();
        mIdling = false;
        break;

    case ScanLeft:
        // See if we need to switch mode after the command
		if ((mCurrentPoisition[0] + 2 * ScanModeStep[0]) >= ScanModeRange[0][1])
		{
			if (VerticalMoveEnabled)
				Mode = ScanDown;
			else
				Mode = ScanRight;
		}

        // Execute the move
        mCurrentPoisition[0] = std::fmin(mCurrentPoisition[0] + ScanModeStep[0], ScanModeRange[0][1]);
        mComport->WriteLine(string_format("m 1 %.2f", mCurrentPoisition[0]));
        ReadLine();
        mLastCmdTimeMs = mWatch->ElapsedMilliseconds();
        mIdling = false;
        break;

    case ScanDown:
        // See if we need to switch mode after the command
        if ((mCurrentPoisition[1] + 2 * ScanModeStep[1]) >= ScanModeRange[1][0])
            Mode = ScanFinish;

        // Execute the move
        mCurrentPoisition[1] = std::fmax(mCurrentPoisition[1] + ScanModeStep[1], ScanModeRange[1][1]);
        mComport->WriteLine(string_format("m 2 %.2f", mCurrentPoisition[1]));
        ReadLine();
        mLastCmdTimeMs = mWatch->ElapsedMilliseconds();
        mIdling = false;
        break;

    case ScanFinish:
        // Check if we're back to 0 - if we are, we've failed
        if (std::fabs(mCurrentPoisition[0] - ScanModeStep[0]) <= 5)
        {
            mErrorMessage = "Surrounding scene isn't good enough for dynamic calibration!";
            mProcessFailure = true;

            cout << "Surrounding scene isn't good enough for dynamic calibration!" << endl;
        }
        else
        {
            // Execute the move towards 0
            mCurrentPoisition[0] = std::fmax(mCurrentPoisition[0] - ScanModeStep[0], ScanModeRange[0][0]);
            mComport->WriteLine(string_format("m 1 %.2f", mCurrentPoisition[0]));
            ReadLine();
            mLastCmdTimeMs = mWatch->ElapsedMilliseconds();
            mIdling = false;
        }

        break;

    case Elimination:
        HandleElimination();
        break;
    } // switch (Mode)

//	cout << "RECT: Out - " << mCurrentPoisition[0] << "," << mCurrentPoisition[1] << ", Mode =  " << Mode << endl;
}

void Gimbal::HandleElimination(void)
{
    bool newFastMode = false;

    // Use the feedback to determine the next move
    if (-1 == m_mvDir)
        return;

    switch (m_mvDir)
    {
    case MD_TOP_LEFT:
        mEliminationModeBaseOffset[0] += EliminationModeStep[0];
        mEliminationModeBaseOffset[1] -= EliminationModeStep[1];

        if (mEliminationModeBaseOffset[0] > EliminationModeBoundary[0])
        {
            mEliminationModeBaseOffset[0] = -EliminationModeBoundary[0] + EliminationModeReturnMargin[0];
            newFastMode = true;
            mEliminationModeReturnsLeft--;
        }

        if (mEliminationModeBaseOffset[1] < -EliminationModeBoundary[1])
        {
            mEliminationModeBaseOffset[1] = EliminationModeBoundary[1] - EliminationModeReturnMargin[1];
            newFastMode = true;
            mEliminationModeReturnsLeft--;
        }
        break;

    case MD_TOP_RIGHT:
        mEliminationModeBaseOffset[0] -= EliminationModeStep[0];
        mEliminationModeBaseOffset[1] -= EliminationModeStep[1];

        if (mEliminationModeBaseOffset[0] < -EliminationModeBoundary[0])
        {
            mEliminationModeBaseOffset[0] = EliminationModeBoundary[0] - EliminationModeReturnMargin[0];
            newFastMode = true;
            mEliminationModeReturnsLeft--;
        }

        if (mEliminationModeBaseOffset[1] < -EliminationModeBoundary[1])
        {
            mEliminationModeBaseOffset[1] = EliminationModeBoundary[1] - EliminationModeReturnMargin[1];
            newFastMode = true;
            mEliminationModeReturnsLeft--;
        }
        break;

    case MD_BOTTOM_LEFT:
        mEliminationModeBaseOffset[0] += EliminationModeStep[0];
        mEliminationModeBaseOffset[1] += EliminationModeStep[1];

        if (mEliminationModeBaseOffset[0] > EliminationModeBoundary[0])
        {
            mEliminationModeBaseOffset[0] = -EliminationModeBoundary[0] + EliminationModeReturnMargin[0];
            newFastMode = true;
            mEliminationModeReturnsLeft--;
        }

        if (mEliminationModeBaseOffset[1] > -EliminationModeBoundary[1])
        {
            mEliminationModeBaseOffset[1] = -EliminationModeBoundary[1] + EliminationModeReturnMargin[1];
            newFastMode = true;
            mEliminationModeReturnsLeft--;
        }
        break;

    case MD_BOTTOM_RIGHT:
        mEliminationModeBaseOffset[0] -= EliminationModeStep[0];
        mEliminationModeBaseOffset[1] += EliminationModeStep[1];

        if (mEliminationModeBaseOffset[0] < -EliminationModeBoundary[0])
        {
            mEliminationModeBaseOffset[0] = EliminationModeBoundary[0] - EliminationModeReturnMargin[0];
            newFastMode = true;
            mEliminationModeReturnsLeft--;
        }

        if (mEliminationModeBaseOffset[1] > EliminationModeBoundary[1])
        {
            mEliminationModeBaseOffset[1] = -EliminationModeBoundary[1] + EliminationModeReturnMargin[1];
            newFastMode = true;
            mEliminationModeReturnsLeft--;
        }
        break;
    }

    if (mEliminationModeReturnsLeft <= 0)
    {
        // Looks like this scene isn't as good as we'd hoped, so go back to scanning
        mCurrentPoisition[0] = mEliminationModeBasePosition[0];
        mCurrentPoisition[1] = mEliminationModeBasePosition[1];
        Mode = mEliminationEntryMode;

        // Get fast regardless
        if (!mFastMode)
        {
            mComport->WriteLine(string_format("s 1 %d", FastSpeed));
            ReadLine();
            mComport->WriteLine(string_format("s 2 %d", FastSpeed));
            ReadLine();
            mFastMode = true;
        }
    }
    else
    {
        // Make the move
        mCurrentPoisition[0] = std::fmin(std::fmax(mEliminationModeBasePosition[0] + mEliminationModeBaseOffset[0], AxisRange[0][0]), AxisRange[0][1]);
        mCurrentPoisition[1] = std::fmin(std::fmax(mEliminationModeBasePosition[1] + mEliminationModeBaseOffset[1], AxisRange[1][0]), AxisRange[1][1]);

        if (mFastMode != newFastMode)
        {
            if (!newFastMode)
            {
                mComport->WriteLine(string_format("s 1 %d", SlowSpeed));
                ReadLine();
                mComport->WriteLine(string_format("s 2 %d", SlowSpeed));
                ReadLine();
            }
            else
            {
                mComport->WriteLine(string_format("s 1 %d", FastSpeed));
                ReadLine();
                mComport->WriteLine(string_format("s 2 %d", FastSpeed));
                ReadLine();
            }

            mFastMode = newFastMode;
        }
    }

	cout << mCurrentPoisition[0] << "," << mCurrentPoisition[1] << endl;

    mComport->WriteLine(string_format("m 1 %.2f", mCurrentPoisition[0]));
    ReadLine();

    mComport->WriteLine(string_format("m 2 %.2f", mCurrentPoisition[1]));
    ReadLine();

    mLastCmdTimeMs = mWatch->ElapsedMilliseconds();
    mIdling = false;
}

void Gimbal::SuggestNextMove(const int* grid, int gridWidth, int gridHeight)
{
    int reg[4];

    for (size_t i = 0; i < sizeof(reg) / sizeof(int); i++)
        reg[i] = 0;

    for (int y = 0; y < gridHeight; y++)
    {
        for (int x = 0; x < gridWidth; x++)
        {
            // The values are
            // GRID_LEVEL_LOW       -> 0
            // GRID_LEVEL_MEDIUM    -> 1
            // GRID_LEVEL_HIGH      -> 2
            // GRID_LEVEL_VERY_HIGH -> 3
            //
            // GRID_FEATURES_L0     -> 0
            // GRID_FEATURES_L1     -> 1
            // GRID_FEATURES_L2     -> 2
            //
            // However we do limit the collection of features between
            // GRID_LEVEL_HIGH and GRID_LEVEL_VERY_HIGH, so just count
            // GRID_LEVEL_VERY_HIGH as 2
            int v = min((int)grid[y * gridWidth + x], 2);

            if (x < gridWidth / 2)
            {
                if (y < gridHeight / 2)
                    reg[MD_TOP_LEFT] += v;
                else
                    reg[MD_BOTTOM_LEFT] += v;
            }
            else
            {
                if (y < gridHeight / 2)
                    reg[MD_TOP_RIGHT] += v;
                else
                    reg[MD_BOTTOM_RIGHT] += v;
            }
        }
    }

    // Prevent stalemates, so add one point if we have more than the opposite register
    if (reg[MD_TOP_LEFT] > reg[MD_BOTTOM_RIGHT])
        reg[MD_TOP_LEFT]++;
    else if (reg[MD_BOTTOM_RIGHT] > reg[MD_TOP_LEFT])
        reg[MD_BOTTOM_RIGHT]++;

    if (reg[MD_TOP_RIGHT] > reg[MD_BOTTOM_LEFT])
        reg[MD_TOP_RIGHT]++;
    else if (reg[MD_BOTTOM_LEFT] > reg[MD_TOP_RIGHT])
        reg[MD_BOTTOM_LEFT]++;

    if (reg[MD_TOP_LEFT] >= reg[MD_TOP_RIGHT] && reg[MD_TOP_LEFT] >= reg[MD_BOTTOM_LEFT] && reg[MD_TOP_LEFT] >= reg[MD_BOTTOM_RIGHT])
        m_mvDir = MD_TOP_LEFT;
    else if (reg[MD_TOP_RIGHT] >= reg[MD_TOP_LEFT] && reg[MD_TOP_RIGHT] >= reg[MD_BOTTOM_LEFT] && reg[MD_TOP_RIGHT] >= reg[MD_BOTTOM_RIGHT])
        m_mvDir = MD_TOP_RIGHT;
    else if (reg[MD_BOTTOM_LEFT] >= reg[MD_TOP_LEFT] && reg[MD_BOTTOM_LEFT] >= reg[MD_TOP_RIGHT] && reg[MD_BOTTOM_LEFT] >= reg[MD_BOTTOM_RIGHT])
        m_mvDir = MD_BOTTOM_LEFT;
    else
        m_mvDir = MD_BOTTOM_RIGHT;
}

void Gimbal::SuggestNextMove(const DSDynamicCalibration::GridLevel* gridLevels,
    int gridWidth, int gridHeight, bool bSceneHasFeatures)
{
    if (!gridLevels)
        throw runtime_error("gridLevels is NULL!");

    m_SceneHasFeatures = bSceneHasFeatures;
    SuggestNextMove((const int*)gridLevels, gridWidth, gridHeight);
}

void Gimbal::SuggestNextMove(const DSDynamicCalibration::GridFeatures* gridFeatures,
    int gridWidth, int gridHeight, bool bSceneHasFeatures)
{
    if (!gridFeatures)
        throw runtime_error("gridFeatures is NULL!");

    m_SceneHasFeatures = bSceneHasFeatures;
    SuggestNextMove((const int*)gridFeatures, gridWidth, gridHeight);
}

void Gimbal::TargetNextMove()
{
//	Mode = ScanLeft;
}

void Gimbal::EnableVerticalMove(bool on)
{
	VerticalMoveEnabled = on;
}

void Gimbal::UpdateCalibrationState(CalibrationState cs)
{
	mCS = cs;
//	cout << "updated cs to " << mCS;
}

void Gimbal::EnableTargetMode(bool on)
{
	Targeted = on;
}

void Gimbal::HandleMoveTargeted(void)
{
	std::this_thread::sleep_for(std::chrono::milliseconds(WaitInMs));

	//GetStatus
	mComport->WriteLine("q");
	string response = ReadLine();

	if (response != "IDLE")
		return;

//	std::this_thread::sleep_for(std::chrono::milliseconds(1000));

	// Set the speed
	mComport->WriteLine(string_format("s 1 %d", TargetModeSpeed));
	ReadLine();
	mComport->WriteLine(string_format("s 2 %d", TargetModeSpeed));
	ReadLine();

	//GetStatus
	while (true)
	{
		std::this_thread::sleep_for(std::chrono::milliseconds(WaitInMs));

		// GetStatus
		mComport->WriteLine("q");
		string res = ReadLine();

		if (res == "IDLE")
			break;
	}

	ScanModeRange[0][0] = -30;
	ScanModeRange[0][1] = 30;
	ScanModeRange[1][0] = 0;
	ScanModeRange[1][1] = 0;

	ScanModeStep[0] = 15;
	ScanModeStep[1] = 15;

	switch (Mode)
	{
	case ScanLeft:
		// See if we need to switch mode after the command
//		cout << "In: Mode="<<Mode << "," << "mCurrentPoisition[0]=" << mCurrentPoisition[0] << ", ScanModeRange[0][0]=" << ScanModeRange[0][0] << ",";

		if ((mCurrentPoisition[0] - ScanModeStep[0]) <= ScanModeRange[0][0])
			Mode = ScanRight;

		// Execute the move
		mCurrentPoisition[0] = std::fmax(mCurrentPoisition[0] - ScanModeStep[0], ScanModeRange[0][0]);

		mComport->WriteLine(string_format("m 1 %.2f", mCurrentPoisition[0]));
		ReadLine();

		mLastCmdTimeMs = mWatch->ElapsedMilliseconds();

		break;

	case ScanRight:
//		cout << "In: Mode=" << Mode << "," << "mCurrentPoisition[0]=" << mCurrentPoisition[0] << ", ScanModeRange[0][0]=" << ScanModeRange[0][1] << ",";


		// See if we need to switch mode after the command
		if ((mCurrentPoisition[0] + ScanModeStep[0]) >= ScanModeRange[0][1])
			Mode = ScanLeft;

		// Execute the move
		mCurrentPoisition[0] = std::fmin(mCurrentPoisition[0] + ScanModeStep[0], ScanModeRange[0][1]);

		mComport->WriteLine(string_format("m 1 %.2f", mCurrentPoisition[0]));
		ReadLine();

		mLastCmdTimeMs = mWatch->ElapsedMilliseconds();

		break;
	} // switch (Mode)

//	cout << "Out: Mode=" << Mode << "," << mCurrentPoisition[0] << "," << mCurrentPoisition[1] << endl;
//	std::this_thread::sleep_for(std::chrono::milliseconds(5000));
}

void Gimbal::HandleWarmUp(void)
{
	std::this_thread::sleep_for(std::chrono::milliseconds(WaitInMs));

	//GetStatus
	mComport->WriteLine("q");
	string response = ReadLine();

	if (response != "IDLE")
		return;

	// Set the speed
	mComport->WriteLine(string_format("s 1 %d", SlowSpeed));
	ReadLine();
	mComport->WriteLine(string_format("s 2 %d", SlowSpeed));
	ReadLine();

	//GetStatus
	while (true)
	{
		std::this_thread::sleep_for(std::chrono::milliseconds(WaitInMs));

		// GetStatus
		mComport->WriteLine("q");
		string res = ReadLine();

		if (res == "IDLE")
			break;
	}


	if (mCS == CS_SCALE_WARMUP)
	{
		if (mCurrentPoisition[0] != -30)
		{
			//	std::this_thread::sleep_for(std::chrono::milliseconds(1000));
//			cout << "SCALE Warm up - In: Mode=" << Mode << "," << "mCurrentPoisition[0]=" << mCurrentPoisition[0] << ",";

			mCurrentPoisition[0] = -30;

			mComport->WriteLine(string_format("m 1 %.2f", mCurrentPoisition[0]));
			ReadLine();

//			cout << "SCALE Warm up - Out: Mode=" << Mode << "," << mCurrentPoisition[0] << endl;
		}
	}
	else if (mCS == CS_RGB_WARMUP)
	{
		if (mCurrentPoisition[0] != 30)
		{
			//	std::this_thread::sleep_for(std::chrono::milliseconds(1000));
//			cout << "RGB Warm up - In: Mode=" << Mode << "," << "mCurrentPoisition[0]=" << mCurrentPoisition[0] << ",";

			mCurrentPoisition[0] = 30;

			mComport->WriteLine(string_format("m 1 %.2f", mCurrentPoisition[0]));
			ReadLine();

//			cout << "RGB Warm up - Out: Mode=" << Mode << "," << mCurrentPoisition[0] << endl;
		}
	}

	//	std::this_thread::sleep_for(std::chrono::milliseconds(5000));
}

void Gimbal::SetDeviceWarmUP(bool warmingup)
{
	DeviceInWarmUp = warmingup;

//	cout << "set device in warm up: " << warmingup << endl;
}


std::string Gimbal::GetErrorMsg(void)
{
    return mErrorMessage;
}

std::string Gimbal::string_format(const char * format, ...)
{
    // Format output string
    va_list args;

    va_start(args, format);

    char buffer[1024];
#if defined(_WIN32) || defined(__WIN32__)
    vsnprintf_s(buffer, sizeof(buffer), format, args);
#else
    vsnprintf(buffer, sizeof(buffer), format, args);
#endif
    va_end(args);

    return std::string(buffer);
}

bool Gimbal::IsConnected(void)
{
    return mComport && mComport->IsConnected();
}

void Gimbal::Run(void)
{

	cout << "setting up gimbal ..." << endl;

    // Setup
    if (mExit
        || (nullptr == mComport)
        || !mComport->IsConnected()
        )
    {
        mErrorMessage = "Failed to start run thread";
        mProcessFailure = true;

		cout << mErrorMessage << endl;
        return;
    }

    mIdling = false;
    mTakenCharacterizationShot = false;
    mFastMode = false;

    Mode = ScanRight;

    mEliminationModeReturnsLeft = 0;
    mEliminationEntryMode = ScanRight;

    mWatch = new Stopwatch();
    mWatch->Start();
    mLastCmdTimeMs = 0.0f;

	cout << "starting gimbal thread ..." << endl;

    m_RunThread = std::thread([this]()
    {
		std::this_thread::sleep_for(std::chrono::milliseconds(WaitInMs));

		cout << "resetting gimbal ..." << endl;
        // Reset

		mComport->WriteLine("r");

        while (!mExit)
        {
            string res = ReadLine();

            if (res == "READY")
                break;
        }

		cout << "setting speed to " << SlowSpeed << endl;
        // Set the speed
        mComport->WriteLine(string_format("s 1 %d", SlowSpeed));
        ReadLine();
        mComport->WriteLine(string_format("s 2 %d", SlowSpeed));
        ReadLine();

		cout << "moving to initial position " << mCurrentPoisition[0] << "," << mCurrentPoisition[1] << endl;
        // Move to initial position
        mComport->WriteLine(string_format("m 1 %.2f", mCurrentPoisition[0]));
        ReadLine();
        mComport->WriteLine(string_format("m 2 %.2f", mCurrentPoisition[1]));
        ReadLine();

        // Wait for it to get there
        while (!mExit)
        {
            // GetStatus
            mComport->WriteLine("q");
            string res = ReadLine();

            if (res == "IDLE")
                break;
        }

		int loops = 0;

        while (!mExit && !mProcessFailure)
        {
//			cout << endl << "looping ..." << loops << endl;

			loops++;

			if (mCS != CS_RECT &&  mCS != CS_SCALE && mCS != CS_RGB)
			{
//				cout << "waiting device to warm up ..." << endl;
				std::this_thread::sleep_for(std::chrono::milliseconds(WaitInMs));

				HandleWarmUp();
				continue;
			}

			if (Targeted)
			{
				HandleMoveTargeted();
			}
			else
			{

				if (-1 == m_mvDir)
				{
					std::this_thread::sleep_for(std::chrono::milliseconds(WaitInMs));
					continue;
				}

				if ((mWatch->ElapsedMilliseconds() - mLastCmdTimeMs) > CmdPauseTimeMs)
				{
					HandleMove();
				}

				if (mIdling && !mTakenCharacterizationShot && (Mode != Elimination))
				{
					mTakenCharacterizationShot = true;

					if (m_SceneHasFeatures)
					{
						mFastMode = false;

						for (int i = 0; i < 2; i++)
						{
							mEliminationModeBasePosition[i] = mCurrentPoisition[i];
							mEliminationModeBaseOffset[i] = 0.0f;
						}

						mEliminationEntryMode = Mode;
						mEliminationModeReturnsLeft = EliminationModeMaxReturns;

						if (VerticalMoveEnabled)
							Mode = Elimination;
						else
						{
//							if (Mode == ScanLeft)
//								Mode = ScanRight;
//							else
//								Mode = ScanLeft;
						}
					}
				}
			}

            std::this_thread::sleep_for(std::chrono::milliseconds(WaitInMs));
        } // end of while()

          // CenterAllServos
        mComport->WriteLine("c");
        ReadLine();
    });
}
