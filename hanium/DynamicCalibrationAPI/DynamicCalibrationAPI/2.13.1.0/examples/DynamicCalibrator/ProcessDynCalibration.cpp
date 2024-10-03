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

#include <iomanip>
#include <iostream>

#include "DSDynamicCalibration.h"
#include "ProcessDynCalibration.h"
#include "CaptureManager.h"
#include "MainView.h"
#include "CalibParamXmlWrite.h"

using namespace std;
using namespace DynamicCalibrator;
using namespace DynamicCalibrationAPI;
using namespace GIMBAL;

ProcessDynCalib::ProcessDynCalib(MainView* mainView, CaptureManager* captureManager,
    int saveFrame, bool bGetRectErrorOnly)
{
    m_mainView = mainView;
    m_captureManager = captureManager;
    m_dcApi = nullptr;
    m_image = nullptr;
    m_colorImage = nullptr;
    m_saveFrame = saveFrame;
    m_bGetRectErrorOnly = bGetRectErrorOnly;

    m_width = 0;
    m_height = 0;

    m_width_rgb = 0;
    m_height_rgb = 0;

    m_gridWidth = 0;
    m_gridHeight = 0;
    m_ExposureLeftEdge = 0;
    m_ExposureRightEdge = 0;
    m_ExposureTopEdge = 0;
    m_ExposureBottomEdge = 0;
    m_Region = 0;
    m_sku = 0;

    m_gridLevels = nullptr;
    m_gridFills = nullptr;
    m_gridFeatures = nullptr;
    m_gridIsFull = false;
    m_bAEenabled = false;
    m_SceneHasFeatures = false;
    m_bTargeted = false;
    m_bWarmUpDone = false;
    m_ae_setpoint = 0;
    m_AESweep = AE_SWEEP_MANUAL;
    m_status = 0;

    last_frame_time = std::chrono::high_resolution_clock::now();

    m_numFramesReceived = 0;
    m_numFramesProcessed = 0;
    m_framesRejected = 0;
    m_RejectedThreshold = DC_REJECTED_MAX;
    m_imageNum = 0;

    m_scaleStarted = false;
    m_scaleFrameCount = 0;
    m_scalePhaseCompleted = false;;
    m_frameCountSuccess = 0;

	m_scaleonly = false;

    m_bRgbCalib = false;
    m_rgbFrameCount = 0;

    m_warmupTime = milliseconds(10000);
    m_passedTime = milliseconds(0);

    m_elapsedTime.Start();
    m_prevGetRectErrorTime.Start();

#ifdef _WIN32
    InitializeCriticalSection(&m_mutexCamFrame);
    InitializeConditionVariable(&m_cvCamFrameReady);
#else
    if (0 != pthread_mutex_init(&m_mutexCamFrame, NULL)) throw std::runtime_error("pthread_mutex_init failed");
    if (0 != pthread_cond_init(&m_cvCamFrameReady, NULL)) throw std::runtime_error("pthread_cond_init failed");
#endif

	m_rgbBrightness = 0;
	m_rgbBrightnessMin = -64;
	m_rgbBrightnessMax = 64;

	m_rgbBrightnessDefault = 0;

	m_rgbFramesRejected = 0;
	m_autoExposure = false;

	m_rgbPhaseCompleted = false;
}

ProcessDynCalib::~ProcessDynCalib()
{
#ifndef _WIN32
    if (0 != pthread_mutex_destroy(&m_mutexCamFrame)) throw std::runtime_error("pthread_mutex_destroy failed");
    if (0 != pthread_cond_destroy(&m_cvCamFrameReady)) throw std::runtime_error("pthread_mutex_destroy failed");
#endif
}

void ProcessDynCalib::ProcessFrames(const void *leftImage, const void *rightImage,
    const void *mainImage, const uint64_t timeStamp)
{
    m_numFramesReceived++;
    last_frame_time = std::chrono::high_resolution_clock::now();

    if (m_bRgbCalib)
    {
        ProcessRgbCalibFrames(leftImage, rightImage, mainImage, timeStamp);
        return;
    }

    MUTEX_LOCK(&m_mutexCamFrame);

    m_image = (void *)leftImage;

    COND_SIGNAL(&m_cvCamFrameReady);
    MUTEX_UNLOCK(&m_mutexCamFrame);

    if (m_scaleStarted)
    {
        ProcessScaleFrames(leftImage, rightImage, mainImage, timeStamp);
        return;
    }

    // Adding Images
    if (m_bWarmUpDone)
    {
        if (!m_dcApi->IsGridFull())
        {
            m_status = m_dcApi->AddImages((uint8_t *)leftImage, (uint8_t *)rightImage,
                (uint16_t *)mainImage, timeStamp);

            if (m_saveFrame == SAVE_FRAME_ALL)
            {
                m_fileWrite.SaveFrameToFile((uint8_t *)leftImage, (uint8_t *)rightImage, nullptr, m_width, m_height);
            }

            if (!m_bTargeted && m_bGetRectErrorOnly && (m_prevGetRectErrorTime.ElapsedMilliseconds() >= 5000)) {

                //print out initial rectification error
                float rectificationError;
                m_dcApi->GetCalibrationError(rectificationError);
                float gridlevelscore = m_dcApi->GetGridLevelScore();
                m_prevGetRectErrorTime.Restart();
                string rectErrorStr = rectificationError < 0.3 ? "Good" : rectificationError > 1.0 ? "Bad" : "Okay";
                //string confStr = gridlevelscore > 0.5 ? "high" : (gridlevelscore < 0.25 ? "low" : "medium");
				string confStr = "medium";
				if (gridlevelscore > 0.5) confStr = "high";
				else if (gridlevelscore < 0.25) confStr = "low";

				cout << endl << "Current rectification error is " << fixed << setprecision(3) << " at " << rectificationError << " pixels ("<< rectErrorStr << ")."<<endl;
                cout << "The confidence of this error is " << confStr;
                if (gridlevelscore < 0.25)
                    cout << ", try moving the camera to more interesting scenes or use larger timeout value (-t)." << endl;
                else
                    cout << "." << endl;
            }
            if (m_status == (int)DC_SUCCESS)
            {

                DynCalAddImagesSuccess();

                if (m_AESweep == AE_SWEEP_AUTO)
                {
                    m_RejectedThreshold += DC_REJECTED_STEP;
                }
            }
            else
            {
                DynCalAddImagesFailure(m_status);
            }

        }
    }
    else
    {
        m_passedTime = duration_cast<milliseconds>(high_resolution_clock::now() - m_startTime);
        if (m_passedTime > m_warmupTime)
        {
            m_bWarmUpDone = true;
            m_prevGetRectErrorTime.Restart();
            m_elapsedTime.Restart();

            if (m_mainView->pGimbal)
            {
                m_mainView->pGimbal->SetDeviceWarmUP(false);
                m_mainView->pGimbal->EnableTargetMode(false);
				m_mainView->pGimbal->UpdateCalibrationState(CS_RECT);
            }
        }

        if (!m_bAEenabled && (m_passedTime > m_warmupTime / 3))
        {
            m_captureManager->SetAeControl(m_ae_setpoint);
            m_bAEenabled = true;
        }
    }

    m_numFramesProcessed += 1;
}

void ProcessDynCalib::DynCalAddImagesSuccess()
{
    // Increment number of image which is added
    m_imageNum++;

    m_framesRejected = 0;

    if (m_bTargeted == false)
    {
        m_dcApi->GetLastPhoneROILeftCamera(m_phoneLoc);
    }

    m_dcApi->GetGridLevels(m_gridLevels, m_gridWidth, m_gridHeight);

    // If the grid level score is high enough then enable AE ROI
    bool useAEROI = (m_dcApi->GetGridLevelScore() >= AE_ROI_THRESHOLD_SCORE) ? true : false;
    int aeroiX = 0, aeroiY = 0;
    SetGridFill(m_gridLevels, m_gridWidth, m_gridHeight, useAEROI, m_gridFills, aeroiX, aeroiY);

    // Set the AE ROI based on the cell
    int region = -1;

    if (useAEROI && (aeroiX != -1) && (aeroiY != -1))
    {
        int cellW = m_width / m_gridWidth;
        int cellH = m_height / m_gridHeight;

        if ((m_width % m_gridWidth) != 0)
            cellW++;
        if ((m_height % m_gridHeight) != 0)
            cellH++;

        m_ExposureLeftEdge = (aeroiX * cellW);
        m_ExposureRightEdge = min(((aeroiX + 1) * cellW) - 1, m_width - 1);
        m_ExposureTopEdge = (aeroiY * cellH);
        m_ExposureBottomEdge = min(((aeroiY + 1) * cellH) - 1, m_height - 1);
        region = aeroiY * m_gridWidth + aeroiX;
    }
    else
    {
        m_ExposureLeftEdge = 0;
        m_ExposureRightEdge = m_width - 1;
        m_ExposureTopEdge = 0;
        m_ExposureBottomEdge = m_height - 1;
        region = -1;
    }

    if (region != m_Region)
    {
//		cout << "ROI: " << m_bROIEnabled << "," << m_bTargeted << "," << m_ExposureTopEdge << "," << m_ExposureBottomEdge << "," << m_ExposureLeftEdge <<"," << m_ExposureRightEdge << endl;

        // disable for now pending ROI in production FW
        if (m_bROIEnabled && (m_bTargeted == false))
        {
            m_captureManager->SetROI(m_ExposureTopEdge, m_ExposureBottomEdge, m_ExposureLeftEdge, m_ExposureRightEdge);
        }

        m_Region = region;
        m_bROIEnabled = true;
    }
}

void ProcessDynCalib::DynCalAddImagesFailure(int ImageStatus)
{
    for (int i = 0; i < (int)PHONELOC_DIM; i++) m_phoneLoc[i] = 0.0f;

    // check if target not found for two reasons, target does not exists or target is over or under
    // exposured. sweep through the AE exposure setpoint so that a good exposure point can be found
    // and target can be recovered.
    if ((ImageStatus == (int)DC_ERROR_RECT_TARGET_NOT_FOUND_BOTH)
        && (m_AESweep != AE_SWEEP_MANUAL)
        )
    {
        m_framesRejected++;

        if (m_framesRejected > m_RejectedThreshold)
        {
            UpdateSetPointValue();
            m_captureManager->SetAeControl(m_ae_setpoint);
            m_framesRejected = 0;

            m_RejectedThreshold -= DC_REJECTED_STEP;

			if (m_RejectedThreshold < DC_REJECTED_MAX)
			{
				m_RejectedThreshold = DC_REJECTED_MAX;
			}
        }
    }
    else
    {
        m_framesRejected = 0;
    }

    m_ROIResetCout++;

    if ((m_ROIResetCout > 5) && (m_bTargeted == false))
    {
        m_ExposureLeftEdge = 0;
        m_ExposureRightEdge = m_width - 1;
        m_ExposureTopEdge = 0;
        m_ExposureBottomEdge = m_height - 1;

        m_captureManager->SetROI(m_ExposureTopEdge, m_ExposureBottomEdge,
            m_ExposureLeftEdge, m_ExposureRightEdge);

        m_ROIResetCout = 0;
        m_Region = -1;
    }
}

void ProcessDynCalib::SetGridFill(const DSDynamicCalibration::GridLevel* gridLevels,
    int gridWidth, int gridHeight, bool useAEROI,
    DSDynamicCalibration::GridFill* gridFills, int& aeroiX, int& aeroiY)
{
    // Init
    aeroiX = -1;
    aeroiY = -1;

    // Do grid settings
    for (int y = 0; y < gridHeight; y++)
    {
        for (int x = 0; x < gridWidth; x++)
        {
            // The way this works, depending on the grid level in each cell
            //
            // GRID_LEVEL_VERY_HIGH: Set GRID_FILL_ADD_ONLY / GRID_FILL_CELL_FULL depending if AE ROI is used
            // GRID_LEVEL_HIGH:      Leave it as it was before (i.e. keeps filling new features
            //                       if changed from GRID_LEVEL_MEDIUM
            //                       or retains features if declined from GRID_LEVEL_VERY_HIGH
            // GRID_LEVEL_MEDIUM
            // and
            // GRID_LEVEL_LOW:       Set GRID_FILL_NORMAL

            if (gridLevels[y * gridWidth + x] == DSDynamicCalibration::GRID_LEVEL_VERY_HIGH)
            {
                // Cells with lots of features retain them and prevent them from aging
                // but we can add more until the buffers are full
                //
                // However if we're close to completion, mark them as completely full,
                //
                // Note that ransac is still active and features may disappear in the cells,
                // this only affects how new features are handled

                if (useAEROI)
                    gridFills[y * gridWidth + x] = DSDynamicCalibration::GRID_FILL_CELL_FULL;
                else
                    gridFills[y * gridWidth + x] = DSDynamicCalibration::GRID_FILL_ADD_ONLY;
            }
            else if (gridLevels[y * gridWidth + x] == DSDynamicCalibration::GRID_LEVEL_HIGH)
            {
                if (useAEROI && gridFills[y * gridWidth + x] == DSDynamicCalibration::GRID_FILL_ADD_ONLY)
                    gridFills[y * gridWidth + x] = DSDynamicCalibration::GRID_FILL_CELL_FULL;
                else if (!useAEROI && gridFills[y * gridWidth + x] == DSDynamicCalibration::GRID_FILL_CELL_FULL)
                    gridFills[y * gridWidth + x] = DSDynamicCalibration::GRID_FILL_ADD_ONLY;
            }
			else if (gridLevels[y * gridWidth + x] == DSDynamicCalibration::GRID_LEVEL_NOT_TRACKED)
			{
				gridFills[y * gridWidth + x] = DSDynamicCalibration::GRID_FILL_CELL_FULL;
			}
            else
            {
                // It dropped below high level, so set fill level back to normal,
                // features are probably false matches
                gridFills[y * gridWidth + x] = DSDynamicCalibration::GRID_FILL_NORMAL;

                // Select the first cell that has less than GRID_FILL_HIGH
                if (useAEROI && (aeroiX == -1) && (aeroiY == -1))
                {
                    aeroiX = x;
                    aeroiY = y;
                }
            }
        }
    }
}

void ProcessDynCalib::UpdateSetPointValue()
{
	if (m_AESweep == AE_SWEEP_MANUAL)
	{
		return;
	}

    unsigned int step = 0;

    if (m_ae_setpoint <= 600)
    {
        step = DC_SETPOINT_STEP >> 1;
    }
    else if ((m_ae_setpoint > 600) && (m_ae_setpoint <= 1200))
    {
        step = DC_SETPOINT_STEP;
    }
    else if ((m_ae_setpoint > 1200) && (m_ae_setpoint <= 2000))
    {
        step = 2 * DC_SETPOINT_STEP;
    }
    else if ((m_ae_setpoint > 2000) && (m_ae_setpoint <= 3000))
    {
        step = 4 * DC_SETPOINT_STEP;
    }
    else
    {
        step = 6 * DC_SETPOINT_STEP;
    }

    m_ae_setpoint -= step;

    if (m_ae_setpoint < DC_SETPOINT_LOW)
    {
        m_ae_setpoint = DC_SETPOINT_HIGH;
    }

//	cout << "setpoint: " << m_ae_setpoint << endl;
}

void ProcessDynCalib::SetSweepMode(int sweep)
{
	m_AESweep = (AE_SWEEP_MODE) sweep;
}

void* ProcessDynCalib::OnIdle()
{
    auto now = high_resolution_clock::now();
    auto passed_ns = now - last_frame_time;
    auto passed_ms = duration_cast<milliseconds>(passed_ns).count();

//    cout << "frames received: " << m_numFramesReceived << ", gap time: " << passed_ms << endl;
//	cout << __LINE__ << endl;
	std::this_thread::sleep_for(std::chrono::milliseconds(5));

    if (m_numFramesReceived > 0 && passed_ms > 500000)
    {
        m_mainView->ErrorHandling(DC_ERROR_DEVICE_TIMEOUT);
    }

    if (m_bRgbCalib)
        return RgbCalibOnIdle();

    if (m_scaleStarted)
        return ScaleOnIdle();

    if ((m_image == nullptr) || m_gridIsFull)
        return m_image;

    MUTEX_LOCK(&m_mutexCamFrame);
#ifdef _WIN32
    SleepConditionVariableCS(&m_cvCamFrameReady, &m_mutexCamFrame, 1000);
#else
    struct timespec req;
    req.tv_sec = 1;
    req.tv_nsec = 0;
    (void)pthread_cond_timedwait(&m_cvCamFrameReady, &m_mutexCamFrame, &req);
#endif
    MUTEX_UNLOCK(&m_mutexCamFrame);

    if (m_dcApi->IsGridFull())
    {
        m_gridIsFull = true;

        if (m_bTargeted)
        {
            if (m_dcApi->SetIntermediateRectificationCalibration() == DC_SUCCESS)
            {
                std::this_thread::sleep_for(std::chrono::milliseconds(200));

				ContinueCalibrationToScalePhase();
            }
            else
            {
                m_mainView->ErrorHandling(DC_ERROR_SET_INTERMEDIATE_CALIB_TABLE);
            }
        }
        else
        {
            stringstream stream;

            float calibrationError;
            m_dcApi->GetCalibrationError(calibrationError);
            stream << "Initial rectification error " << fixed << setprecision(3) << calibrationError;

			if (m_bGetRectErrorOnly)
			{
				cout << stream.str() << endl;
			}
			else
			{
				int ret = UpdateCalibrationTables(stream.str());

				if (ret != DC_SUCCESS)
					m_mainView->ErrorHandling(ret);
			}
        }
    }
    else
    {
        // Update UI
        m_dcApi->GetLastFrameFeaturesGrid(m_gridFeatures, m_gridWidth, m_gridHeight);
        m_SceneHasFeatures = SceneHasFeatures(m_gridFeatures, m_gridWidth, m_gridHeight);

		if (m_mainView->pGimbal)
		{
			m_mainView->pGimbal->SuggestNextMove(m_gridLevels, m_gridWidth, m_gridHeight, m_SceneHasFeatures);
		}
    }

    return m_image;
}

int ProcessDynCalib::UpdateCalibrationTables(std::string msg)
{
	int ret = DC_SUCCESS;

    m_captureManager->StopDevice();

    bool isOutOfCalibration = false;
    m_dcApi->IsOutOfCalibration(isOutOfCalibration);

    string calibCorrection = msg;

    if (isOutOfCalibration)
        calibCorrection += "\nOut of calibration.";

    bool bUpdated = (m_dcApi->UpdateCalibrationTables() == DC_SUCCESS) ? true : false;

    if (bUpdated)
    {
        string fileName;
        if (!m_bRgbCalib)
        {
            fileName = m_mainView->GetOutputDir() + "/CalibrationTable.xml";
        }
        else
        {
            fileName = m_mainView->GetOutputDir() + "/RgbCalibrationTable.xml";
        }

        bool hasRGB;
        int resolutionLeftRight[2], resolutionRGB[2];
        double focalLengthLeft[2], focalLengthRight[2], focalLengthRGB[2];
        double principalPointLeft[2], principalPointRight[2], principalPointRGB[2];
        double distortionLeft[5], distortionRight[5], distortionRGB[5];
        double rotationLeftRight[9], rotationLeftRGB[9];
        double translationLeftRight[3], translationLeftRGB[3];

        // Read back from device to confirm
        m_dcApi->ReadCalibrationParameters(resolutionLeftRight, focalLengthLeft, principalPointLeft, distortionLeft, focalLengthRight, principalPointRight,
            distortionRight, rotationLeftRight, translationLeftRight, hasRGB, resolutionRGB, focalLengthRGB, principalPointRGB, distortionRGB, rotationLeftRGB, translationLeftRGB);

        CalibParamXmlWrite::WriteCustomCalibrationParametersToFile(fileName, resolutionLeftRight, focalLengthLeft, principalPointLeft, distortionLeft, focalLengthRight,
            principalPointRight, distortionRight, rotationLeftRight, translationLeftRight, hasRGB, resolutionRGB, focalLengthRGB, principalPointRGB,
            distortionRGB, rotationLeftRGB, translationLeftRGB);
    }

    return m_mainView->UpdateCalibrationTablesComplete(calibCorrection, bUpdated);
}

bool ProcessDynCalib::Render(int winWidth, int winHeight)
{
    if (m_bRgbCalib)
        return RgbCalibRender(winWidth, winHeight);

    if (m_scaleStarted)
        return ScaleRender(winWidth, winHeight);

    if (m_numFramesProcessed == 0)
    {
        return false;
    }

    m_mainView->RenderImage();

    std::vector<RECTANGLE> blocks;
    std::vector<POINT_D> points;
    std::vector<COLOR> colors;

    blocks.clear();
    colors.clear();

    if (m_passedTime <= (m_warmupTime / 3))
    {
        m_mainView->RenderText(TEXT_ALIGN_CENTER, TEXT_ALIGN_CENTER, GLUT_BITMAP_TIMES_ROMAN_24,
            "Intel RealSense Dynamic Calibrator",
            0.0f, 174.0f / 255.0f, 239.0f / 255.0f, 200.0f / 255.0f);
    }
    else if (m_bWarmUpDone == false)
    {
        double progress = ((double)m_passedTime.count()) / ((double)m_warmupTime.count());
        COLOR color = { 0, 255, 0, 100 };
        colors.push_back(color);
        double x0 = -0.75;
        double x1 = -0.75 + 0.75 * 2.0 * progress;
        double y0 = 0.01;
        double y1 = -0.01;
        RECTANGLE block = { x0, y0, x1, y1 };
        blocks.push_back(block);
        m_mainView->BlendBlocks(blocks, colors);

        string textmsg = m_bGetRectErrorOnly ? "Waiting for camera to warm up..." : "Preparing camera for calibration. Please wait ...";
        m_mainView->RenderText(TEXT_ALIGN_CENTER, winHeight / 2 - 25, GLUT_BITMAP_HELVETICA_18,
            textmsg.c_str(), 1.0, 1.0, 1.0, 1.0);
    }
    else
    {
        double invW = 1.0 / m_gridWidth;
        double invH = 1.0 / m_gridHeight;
        int numGridFilled = 0;

        for (int y = 0; y < m_gridHeight; y++)
        {
            for (int x = 0; x < m_gridWidth; x++)
            {
                COLOR color;
                RECTANGLE block;
                DSDynamicCalibration::GridLevel v = m_gridLevels[y * m_gridWidth + x];
                DSDynamicCalibration::GridFill f = m_gridFills[y * m_gridWidth + x];

                if (f != DSDynamicCalibration::GRID_FILL_NORMAL)
                    color = { 191, 191, 0, 50 }; // Render yellow for a cell with sufficient amount of features
                else if (v == DSDynamicCalibration::GRID_LEVEL_HIGH || v == DSDynamicCalibration::GRID_LEVEL_VERY_HIGH)
                {
                    color = { 0, 0, 0, 0 }; // Render no color for high level
                    numGridFilled++;
                }
                else if (v == DSDynamicCalibration::GRID_LEVEL_MEDIUM)
                    color = { 0, 66, 128, 100 }; // Render light blue for medium level
                else if (v == DSDynamicCalibration::GRID_LEVEL_NOT_TRACKED)
                {
                    color = { 0, 0, 0, 0 };
                    numGridFilled++;
                }
                else
                    color = { 0, 66, 128, 200 }; // Render blue for low level

                colors.push_back(color);

                double x0 = -1 + 2 * x * invW;
                double x1 = -1 + 2 * (x + 1) * invW;
                double y0 = 1 - 2 * y * invH;
                double y1 = 1 - 2 * (y + 1) * invH;
                block = { x0, y0, x1, y1 };
                blocks.push_back(block);
            }
        }

        if (!m_bGetRectErrorOnly)
            m_mainView->BlendBlocks(blocks, colors);

        if (!m_gridIsFull)
        {
            string msg = "Used frames: " + to_string(m_numFramesProcessed);
            m_mainView->RenderText(TEXT_ALIGN_RIGHT, winHeight - 30, GLUT_BITMAP_HELVETICA_12,
                msg.c_str(), 1.0f, 1.0f, 1.0f, 1.0f);

            int ElapsedSeconds = (int)m_elapsedTime.ElapsedSeconds();
            if (ElapsedSeconds >= 1)
            {
                string msg = to_string(ElapsedSeconds) + " seconds";
                m_mainView->RenderText(TEXT_ALIGN_RIGHT, TEXT_ALIGN_TOP, GLUT_BITMAP_HELVETICA_12,
                    msg.c_str(), 1.0f, 1.0f, 1.0f, 1.0f);
            }

            if (m_bTargeted)
            {
                if ((m_phoneLoc[0] != 0) || (m_phoneLoc[1] != 0) || (m_phoneLoc[4] != 0) || (m_phoneLoc[5] != 0))
                {
                    // render target ROI tracking box
                    // phoneLoc in (TL.x TL.y), (TR.x TR.y), (BR.x BR.y), (BL.x BL.y) order
                    POINT_D point;
                    point.x = 1.0 * (-1.0 + 2 * m_phoneLoc[0] / m_width);
                    point.y = -1.0 * (-1.0 + 2 * m_phoneLoc[1] / m_height);
                    points.push_back(point);
                    point.x = 1.0 * (-1.0 + 2 * m_phoneLoc[2] / m_width);
                    point.y = -1.0 * (-1.0 + 2 * m_phoneLoc[3] / m_height);
                    points.push_back(point);
                    point.x = 1.0 * (-1.0 + 2 * m_phoneLoc[4] / m_width);
                    point.y = -1.0 * (-1.0 + 2 * m_phoneLoc[5] / m_height);
                    points.push_back(point);
                    point.x = 1.0 * (-1.0 + 2 * m_phoneLoc[6] / m_width);
                    point.y = -1.0 * (-1.0 + 2 * m_phoneLoc[7] / m_height);
                    points.push_back(point);

                    COLOR color = { 0, 255, 0, 255 };
                    m_mainView->RenderLines(points, color, 1);
                }

                if (numGridFilled < m_gridWidth*m_gridHeight)
                {
                    string tips_msg = "Position device 600 - 850 mm away pointing to target so the bars are vertical in field of view\nMove slowly to position target bars over the blue squares until all are cleared";

                    if (m_width == 720 && m_height == 720)
                    {
                        tips_msg = "Position device 850 - 1000 mm away pointing to target so the bars are vertical in field of view\nMove slowly to position target bars over the blue squares until all are cleared";
                    }

                    m_mainView->RenderText(TEXT_ALIGN_CENTER, TEXT_ALIGN_CENTER, GLUT_BITMAP_HELVETICA_18, tips_msg.c_str(), 1.0, 1.0, 1.0, 1.0);
                }
                else
                {
                    m_mainView->RenderText(TEXT_ALIGN_CENTER, TEXT_ALIGN_CENTER, GLUT_BITMAP_HELVETICA_18,
                        "Continue to move slowly around the center",
                        1.0, 1.0, 1.0, 1.0);
                }

                // targeted dynamic calibration status
                string status_msg = TranslateStatusToText(m_status);
                m_mainView->RenderText(TEXT_ALIGN_LEFT, winHeight - 35, GLUT_BITMAP_HELVETICA_12,
                    status_msg.c_str(), 1.0f, 1.0f, 1.0f, 1.0f);
            }
            else
            {
                string msg;
                if (m_SceneHasFeatures)
                    msg = "Has Features: Yes";
                else
                    msg = "Has Features: No";

                m_mainView->RenderText(10, winHeight - 35, GLUT_BITMAP_HELVETICA_12,
                    msg.c_str(), 1.0f, 1.0f, 1.0f, 1.0f);


				// Render targetless AE ROI box
                    double aeroiTop, aeroiLeft, aeroiBottom, aeroiRight;
                    POINT_D point;

                    aeroiTop = -1.0 * (-1.0 + max((int)m_ExposureTopEdge, 0) / (m_height / 2.0));
                    aeroiLeft = 1.0 * (-1.0 + max((int)m_ExposureLeftEdge, 0) / (m_width / 2.0));
                    aeroiBottom = -1.0 * (-1.0 + min((int)m_ExposureBottomEdge, m_height) / (m_height / 2.0));
                    aeroiRight = 1.0 * (-1.0 + min((int)m_ExposureRightEdge, m_width) / (m_width / 2.0));

                    point.x = aeroiLeft;
                    point.y = aeroiTop;
                    points.push_back(point);
                    point.x = aeroiRight;
                    point.y = aeroiTop;
                    points.push_back(point);
                    point.x = aeroiRight;
                    point.y = aeroiBottom;
                    points.push_back(point);
                    point.x = aeroiLeft;
                    point.y = aeroiBottom;
                    points.push_back(point);

                    COLOR color = { 0, 191, 0, 255 };
                    m_mainView->RenderLines(points, color, 1);

					if (m_mainView->pGimbal)
					{
						if (!m_mainView->pGimbal->GetErrorMsg().empty())
						{
							// Gimbal error message:
							m_mainView->RenderText(TEXT_ALIGN_CENTER, TEXT_ALIGN_CENTER, GLUT_BITMAP_HELVETICA_18,
								m_mainView->pGimbal->GetErrorMsg().c_str(), 1.0f, 0.0f, 0.0f, 1.0f);
						}
						else
						{
							m_mainView->RenderText(TEXT_ALIGN_CENTER, TEXT_ALIGN_CENTER, GLUT_BITMAP_HELVETICA_18,
								"Gimbal is moving your camera. Please wait ...",
								1.0f, 1.0f, 1.0f, 1.0f);
						}
					}
					else
					{
						string textmsg = m_bGetRectErrorOnly ? "Move or turn the camera slowly to interesting scenes for a few seconds..." :
							"Move slowly until all the blue squares are cleared.";

						m_mainView->RenderText(TEXT_ALIGN_CENTER, TEXT_ALIGN_CENTER, GLUT_BITMAP_HELVETICA_18,
							textmsg.c_str(), 1.0, 1.0, 1.0, 1.0);
					}
            }
        }
    }

    return true;
}

bool ProcessDynCalib::SceneHasFeatures(const DSDynamicCalibration::GridFeatures* gridFeatures,
    int gridWidth, int gridHeight)
{
    float score = 0.0f;

    for (int i = 0; i < gridWidth * gridHeight; i++)
        score += (float)gridFeatures[i];

    score /= (gridWidth * gridHeight) * (int)DSDynamicCalibration::GRID_FEATURES_L2;

    bool passiveSKU = (m_sku & SKU_PASSIVE) ? true : false;
    bool wideSKU = (m_sku & SKU_WIDE) ? true : false;
    if (passiveSKU)
        return wideSKU ? (score >= SCENE_HAS_FEATURES_THRESHOLD_SCORE_PWG) : (score >= SCENE_HAS_FEATURES_THRESHOLD_SCORE_PSR);

    return wideSKU ? (score >= SCENE_HAS_FEATURES_THRESHOLD_SCORE_AWG) : (score >= SCENE_HAS_FEATURES_THRESHOLD_SCORE_ASR);
}

int ProcessDynCalib::InitDynCalParams(int width, int height, DSDynamicCalibration::CalibrationMode calibMode, int width_rgb, int height_rgb, bool bAutoExposure, int aePoint, int sku, int sweep, bool aligned, bool active, int max_num_images, bool ignore_borders, int loglevel)
{
	m_mainView->AddLog("initialize dynamic calibration parameters ...");

    m_sku = sku;
    m_width = width;
    m_height = height;
    m_width_rgb = width_rgb;
    m_height_rgb = height_rgb;

    m_bTargeted = ((DSDynamicCalibration::CalibrationMode)calibMode == DSDynamicCalibration::CalibrationMode::CAL_MODE_INTEL_TARGETED || calibMode == DSDynamicCalibration::CalibrationMode::CAL_MODE_INTEL_TARGETED_SCALE_ONLY) ? true : false;
    m_bRgbCalib = ((DSDynamicCalibration::CalibrationMode)calibMode == DSDynamicCalibration::CalibrationMode::CAL_MODE_INTEL_RGB_CALIB) ? true : false;
	m_scaleonly = (calibMode == DSDynamicCalibration::CalibrationMode::CAL_MODE_INTEL_TARGETED_SCALE_ONLY) ? true : false;

    m_autoExposure = bAutoExposure;
	m_AESweep = (AE_SWEEP_MODE) sweep;

    if (m_AESweep == AE_SWEEP_MANUAL)
    {
        m_ae_setpoint = (unsigned int)aePoint;
    }
    else
    {
        m_ae_setpoint = 1000;
    }

    m_image = nullptr;

    m_bROIEnabled = false;
    m_ROIResetCout = 0;
    m_ExposureLeftEdge = 0;
    m_ExposureRightEdge = 0;
    m_ExposureTopEdge = 0;
    m_ExposureBottomEdge = 0;
    m_Region = -1;

    m_bWarmUpDone = false;

    m_framesRejected = 0;
    m_imageNum = 0;
    m_gridIsFull = false;
    m_bAEenabled = false;

    m_scaleStarted = false;

	last_frame_time = std::chrono::high_resolution_clock::now();

	m_numFramesReceived = 0;
    m_numFramesProcessed = 0;

    m_dcApi = new DSDynamicCalibration();
    void *devHandle = m_captureManager->GetRs400DeviceHandle();

	m_dcApi->m_target_aligned = aligned;
	m_dcApi->m_numImages = max_num_images;
	m_dcApi->m_ignore_borders = ignore_borders;
	m_dcApi->m_log_level = loglevel;

    int ret = 0;

    if (!m_bRgbCalib)
    {
		m_mainView->AddLog("Start Initialize device ...");

        ret = m_dcApi->Initialize(devHandle, calibMode, width, height, active);

		if (ret != DC_SUCCESS)
		{
			m_mainView->AddLog("initialization failed.");
			return ret;
		}

        if (m_saveFrame != SAVE_FRAME_NONE)
        {
            string dir = m_mainView->GetOutputDir();
            m_fileWrite.SetDirectory(dir + "/Rectify");
        }
    }
    else
    {
		m_mainView->AddLog("Start InitRgbCalibration");
        ret = InitRgbCalibration();
        if (m_saveFrame != SAVE_FRAME_NONE)
        {
            string dir = m_mainView->GetOutputDir();
            m_fileWrite.SetDirectory(dir + "/RGBCalib");
        }
    }

    if (ret != DC_SUCCESS)
    {
        m_mainView->ErrorHandling(ret);
        return ret;
    }

    if (!m_bRgbCalib && !m_scaleonly)
    {
        // Get the grids (width and height is the same for all)
        m_dcApi->GetGridLevels(m_gridLevels, m_gridWidth, m_gridHeight);
        m_dcApi->AccessGridFill(m_gridFills, m_gridWidth, m_gridHeight);
        m_dcApi->GetLastFrameFeaturesGrid(m_gridFeatures, m_gridWidth, m_gridHeight);

        m_mainView->AddLog("Start rectification ...");
    }

	if (m_scaleonly)
	{
		m_mainView->AddLog("Start InitScaleCalibration");
		if (InitScaleCalibration())
		{
			ret = DC_SUCCESS;
		}
		else
		{
			ret = DC_ERROR_FAIL;
		}
	}

    // Record start time
    m_startTime = high_resolution_clock::now();

    return ret;
}

void ProcessDynCalib::StopProcessing()
{
    COND_SIGNAL(&m_cvCamFrameReady);

    m_dcApi->~DSDynamicCalibration();
    m_dcApi = nullptr;

    m_image = nullptr;
    m_numFramesProcessed = 0;
}

string ProcessDynCalib::TranslateStatusToText(int status)
{
    std::string status_msg = "";

    switch (status)
    {
    case DC_ERROR_RECT_TARGET_NOT_FOUND_LEFT:
        status_msg = "Target not detected in left image. Please position target towards middle of view.";
        break;

    case DC_ERROR_RECT_TARGET_NOT_FOUND_RIGHT:
        status_msg = "Target not detected in right image. Please position target towards middle of view.";
        break;

    case DC_ERROR_SCALE_DEPTH_TOO_SPARSE:
        status_msg = "Target detected but depth too sparse on target. Possibly due to reflection on target.";
        break;

    case DC_ERROR_SCALE_DEPTH_NOT_CONSISTENT:
        status_msg = "Target detected but target depth is not consistent between dense and sparse features.";
        break;

    case DC_ERROR_SCALE_TARGET_TILT_ANGLE_BIG:
        status_msg = "Target detected but tilted too much!";
        break;

    case DC_ERROR_SCALE_FAILED_COMPUTE:
        status_msg = "Target detected but failed to compute correction angle!";
        break;

    case DC_SUCCESS:
        status_msg = "";
        break;

    case DC_ERROR_TARGET_UNSTABLE:
        status_msg = "Slow down!";
        break;

    case DC_ERROR_RECT_TARGET_NOT_FOUND_BOTH:
        status_msg = "Target is not detected in both left and right images! Target may be too bright or dark, has relfection, too close, or too far.";
        break;

    case DC_ERROR_SCALE_DEPTH_NOT_A_PLANE:
        status_msg = "Depth does not fit on a plane!";
        break;

    case DC_ERROR_RECT_TOO_SIMILAR:
    case DC_ERROR_RECT_TOO_EARLY:
    case DC_ERROR_SCALE_ALREADY_CAPTURED:
        status_msg = "Keep moving!";
        break;

    case DC_ERROR_EXCEPTION:
        status_msg = "";
        break;

    case DC_ERROR_TARGET_TOO_CLOSE:
        status_msg = "Target is too close. Keep camera approximately 50 to 100 cm away.";
        break;

    case DC_ERROR_TARGET_TOO_FAR:
        status_msg = "Target is too far. Keep camera approximately 50 to 100 cm away.";
        break;

    case DC_ERROR_RECT_TARGET_NOT_FOUND_RGB:
        status_msg = "Target not detected in RGB image. Please position target towards middle of view.";
        break;

    case DC_ERROR_RECT_TARGET_NOT_FOUND_LEFT_RGB:
        status_msg = "Target is not detected in both left and RGB images! Please position target towards middle of view.";
        break;

    case DC_ERROR_RECT_TARGET_NOT_FOUND_RIGHT_RGB:
        status_msg = "Target is not detected in both right and RGB images! Please position target towards middle of view.";
        break;

    case DC_ERROR_RECT_TARGET_NOT_FOUND_ALL:
        status_msg = "Target is not detected in left, right and RGB images! Target may be too bright or dark, has relfection, too close, or too far.";
        break;

    case DC_ERROR_LEFT_RIGHT_BAD_CALIBRATION:
        status_msg = "The left and right cameras have bad calibration, please restart the calibration.";
        break;

    default:
        status_msg = "Status reference code: " + to_string(status);
        break;
    }

    return status_msg;
}
