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
#include <sstream>
#include <iostream>

#include "DSDynamicCalibration.h"
#include "ProcessDynCalibration.h"
#include "CaptureManager.h"
#include "MainView.h"

using namespace std;
using namespace DynamicCalibrator;
using namespace DynamicCalibrationAPI;

bool ProcessDynCalib::InitScaleCalibration()
{
    m_scaleFrameCount = 0;
    m_scalePhaseCompleted = false;
    m_framesRejected = 0;
    m_RejectedThreshold = DC_REJECTED_MAX;
    m_frameCountSuccess = 0;

	std::this_thread::sleep_for(std::chrono::milliseconds(1000));

    m_scaleStarted = true;

    m_elapsedTime.Restart();
    m_mainView->AddLog("Start scale calibration");

    if (m_saveFrame != SAVE_FRAME_NONE)
    {
        string dir = m_mainView->GetOutputDir();
        m_fileWrite.SetDirectory(dir + "/Scale");
    }

	if (m_mainView->pGimbal)
	{
		m_mainView->pGimbal->UpdateCalibrationState(CS_SCALE_WARMUP);
	}

    return true;
}

bool ProcessDynCalib::ContinueCalibrationToScalePhase()
{
	// check if rectification phase is completed
	bool rectphasedone = m_dcApi->IsRectificationPhaseComplete();

	if (!rectphasedone)
	{
		m_mainView->ErrorHandling(DC_ERROR_RECTIFICATION_PHASE);
		return false;
	}

	bool scalephase = m_dcApi->GoToScalePhase();

	if (!scalephase)
	{
		m_mainView->ErrorHandling(DC_ERROR_SCALE_PHASE_START_FAILED);
		return false;
	}

	return InitScaleCalibration();
}

bool ProcessDynCalib::StartScaleCalibrationOnly()
{
	// check if rectification phase is completed

	bool scalephase = m_dcApi->SkipToScalePhase();

	if (!scalephase)
	{
		m_mainView->ErrorHandling(DC_ERROR_SCALE_PHASE_START_FAILED);
		return false;
	}

	m_bWarmUpDone = false;

	return InitScaleCalibration();
}

void ProcessDynCalib::ProcessScaleFrames(const void *leftImage, const void *rightImage,
    const void *depthImage, const uint64_t timeStamp)
{
    if (m_scalePhaseCompleted == true) return;

    if (m_dcApi->GetPhase() != DC_TARGETED_SCALE_PHASE)
    {
        m_mainView->ErrorHandling(DC_ERROR_WRONG_PHASE);
		cout << "error wrong phase - not in scale phase" << endl;
        return;
    }

    if (m_dcApi->IsScalePhaseComplete())
    {
		cout << "scale phase completed. ignore image." << endl;
        return;
    }

	if (m_bWarmUpDone)
	{
		m_status = m_dcApi->AddImages((uint8_t *)leftImage, (uint8_t *)rightImage,
			(uint16_t *)depthImage, timeStamp);

		if (m_saveFrame != SAVE_FRAME_NONE)
		{
			if (m_saveFrame == SAVE_FRAME_ALL || m_status == (int)DC_SUCCESS)
			{
				m_fileWrite.SaveFrameToFile((uint8_t *)leftImage, (uint8_t *)rightImage,
					(uint16_t *)depthImage, m_width, m_height);
			}
		}

		if (m_status == (int)DC_SUCCESS)
		{
			m_dcApi->GetLastPhoneROILeftCamera(AckPhoneLoc[m_frameCountSuccess]);
			m_frameCountSuccess++;

			m_framesRejected = 0;

			if (m_AESweep == AE_SWEEP_AUTO)
			{
				m_RejectedThreshold += DC_REJECTED_STEP;
			}
		}
		else
		{
			// check if target not found for two reasons, target does not exists or target is over or under
			// exposured. sweep through the AE exposure setpoint so that a good exposure point can be found
			// and target can be recovered.
			if ((m_AESweep != AE_SWEEP_MANUAL) &&
				((m_status == (int)DC_ERROR_RECT_TARGET_NOT_FOUND_BOTH) ||
				(m_status == (int)DC_ERROR_SCALE_DEPTH_TOO_SPARSE) ||
					(m_status == (int)DC_ERROR_SCALE_DEPTH_NOT_CONSISTENT) ||
					(m_status == (int)DC_ERROR_SCALE_DEPTH_NOT_A_PLANE)))
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
		}

		m_scaleFrameCount++;
		//	cout << "scale total frame cout: " << m_scaleFrameCount << ", frames accepted: " << m_frameCountSuccess << ", frames rejected: " << m_framesRejected << ", current frame status: " << m_status << endl;
	}
	else
	{
		m_passedTime = duration_cast<milliseconds>(high_resolution_clock::now() - m_startTime);
		if (m_passedTime > m_warmupTime)
		{
			m_bWarmUpDone = true;

            if (m_mainView->pGimbal)
            {
                m_mainView->pGimbal->SetDeviceWarmUP(false);
                m_mainView->pGimbal->EnableTargetMode(true);
				m_mainView->pGimbal->UpdateCalibrationState(CS_SCALE);
            }

			m_prevGetRectErrorTime.Restart();
			m_elapsedTime.Restart();
		}
	}
	}

void* ProcessDynCalib::ScaleOnIdle()
{
    if (m_image == nullptr || m_scalePhaseCompleted)
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

    if (m_dcApi->IsScalePhaseComplete())
    {

        double rx = 0.0, ry = 0.0, rz = 0.0;
        if (!m_dcApi->GetTargetedCalibrationCorrection(rx, ry, rz))
        {
            m_mainView->ErrorHandling(DC_ERROR_GET_TARGETED_CALIBRATION_CORRECTION);

            return m_image;
        }

        m_mainView->RenderLastFrame();

        rx = rx * 180.0 / 3.14159;
        ry = ry * 180.0 / 3.14159;
        rz = rz * 180.0 / 3.14159;

        string calibCorrection;
        stringstream stream;

        stream << "Computed rotational correction angles in degrees: <rx, ry, rz> = <"
            << fixed << setprecision(3) << rx << ", "
            << fixed << setprecision(3) << ry << ", "
            << fixed << setprecision(3) << rz << ">";

        UpdateCalibrationTables(stream.str());

        m_scalePhaseCompleted = true;
    }
	else
	{
		if (m_mainView->pGimbal)
		{
			m_mainView->pGimbal->TargetNextMove();
		}
	}

    return m_image;
}

bool ProcessDynCalib::ScaleRender(int winWidth, int winHeight)
{
    if (m_scalePhaseCompleted)
        return false;

	float ratioImg = float(m_width) / m_height;
	float ratioWin = float(winWidth) / winHeight;

	float ratioX = 1.0;
	float ratioY = 1.0;

	if (ratioImg >= ratioWin)
		ratioY = ratioWin / ratioImg;
	else
		ratioX = ratioImg / ratioWin;

    m_mainView->RenderImage();

    std::vector<RECTANGLE> blocks;
    std::vector<POINT_D> points;
    std::vector<COLOR> colors;

    blocks.clear();
    colors.clear();

	if (m_bWarmUpDone == false)
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

		string textmsg = m_bGetRectErrorOnly ? "Waiting for camera to warm up..." : "Preparing camera for scale calibration. Please wait ...";
		m_mainView->RenderText(TEXT_ALIGN_CENTER, winHeight / 2 - 25, GLUT_BITMAP_HELVETICA_18,
			textmsg.c_str(), 1.0, 1.0, 1.0, 1.0);
	}
	else
	{
		int nTotal = min(m_dcApi->NumOfImagesCollected(), m_dcApi->m_numImages);
		double progress = ((double)nTotal) / ((double)m_dcApi->m_numImages);

		COLOR color = { 0, 255, 0, 100 };
		colors.push_back(color);

		double x0 = -1.0;
		double x1 = -1.0 + 2.0f*progress;
		double y0 = -1.0 + 0.08;
		double y1 = -1.0;
		RECTANGLE block = { x0, y0, x1, y1 };
		blocks.push_back(block);

		m_mainView->BlendBlocks(blocks, colors);

		color = { 0, 255, 0, 255 };

		POINT_D point;
		// render ROI tracking box
		// phoneLoc in TL.x TR.x BR.x BL.x TL.y TR.y BR.y BL.y order

		m_dcApi->GetLastPhoneROILeftCamera(m_phoneLoc);

		point.x = 1.0 * ratioX * (-1.0f + 2 * m_phoneLoc[0] / m_width);
		point.y = -1.0 * ratioY * (-1.0f + 2 * m_phoneLoc[1] / m_height);
		points.push_back(point);

		point.x = 1.0 * ratioX * (-1.0 + 2 * m_phoneLoc[2] / m_width);
		point.y = -1.0 * ratioY * (-1.0 + 2 * m_phoneLoc[3] / m_height);
		points.push_back(point);

		point.x = 1.0 * ratioX * (-1.0 + 2 * m_phoneLoc[4] / m_width);
		point.y = -1.0 * ratioY * (-1.0 + 2 * m_phoneLoc[5] / m_height);
		points.push_back(point);

		point.x = 1.0 * ratioX * (-1.0 + 2 * m_phoneLoc[6] / m_width);
		point.y = -1.0 * ratioY * (-1.0 + 2 * m_phoneLoc[7] / m_height);
		points.push_back(point);

		m_mainView->RenderLines(points, color, 2);

		// display accepted phone target locations
		color = { 0, 0, 255, 255 };

		for (int i = 0; i < nTotal; i++)
		{
			points.clear();
			point.x = 1.0 * ratioX * (-1.0 + 2 * AckPhoneLoc[i][0] / m_width);
			point.y = -1.0 * ratioY * (-1.0 + 2 * AckPhoneLoc[i][1] / m_height);
			points.push_back(point);

			point.x = 1.0 * ratioX * (-1.0 + 2 * AckPhoneLoc[i][2] / m_width);
			point.y = -1.0 * ratioY * (-1.0 + 2 * AckPhoneLoc[i][3] / m_height);
			points.push_back(point);

			point.x = 1.0 * ratioX * (-1.0 + 2 * AckPhoneLoc[i][4] / m_width);
			point.y = -1.0 * ratioY * (-1.0 + 2 * AckPhoneLoc[i][5] / m_height);
			points.push_back(point);

			point.x = 1.0 * ratioX * (-1.0 + 2 * AckPhoneLoc[i][6] / m_width);
			point.y = -1.0 * ratioY * (-1.0 + 2 * AckPhoneLoc[i][7] / m_height);
			points.push_back(point);

			m_mainView->RenderLines(points, color, 1);
		}

		// print on-screen instruction to guide user go through the scale phase
		string tips_msg = "Position device 600 - 850 mm away pointing to target so the bars are vertical in field of view\nMove slowly to position target bars on different locations in field of view until completion";

		if (m_width == 720 && m_height == 720)
		{
			tips_msg = "Position device 850 - 1000 mm away pointing to target so the bars are vertical in field of view\nMove slowly to position target bars on different locations in field of view until completion";
		}

		m_mainView->RenderText(TEXT_ALIGN_CENTER, TEXT_ALIGN_CENTER, GLUT_BITMAP_HELVETICA_18, tips_msg.c_str(), 1.0f, 1.0f, 1.0f, 1.0f);

		int ElapsedSeconds = (int)m_elapsedTime.ElapsedSeconds();
		if (ElapsedSeconds >= 1)
		{
			string msg = to_string(ElapsedSeconds) + " seconds";
			m_mainView->RenderText(TEXT_ALIGN_RIGHT, TEXT_ALIGN_TOP, GLUT_BITMAP_HELVETICA_12,
				msg.c_str(), 1.0f, 1.0f, 1.0f, 1.0f);
		}

		// targeted dynamic calibration status
		string status_msg = TranslateStatusToText(m_status);
		m_mainView->RenderText(TEXT_ALIGN_LEFT, winHeight - 35, GLUT_BITMAP_HELVETICA_12,
			status_msg.c_str(), 1.0f, 1.0f, 1.0f, 1.0f);

		string msg = to_string(nTotal) + "/" + to_string(m_dcApi->m_numImages) + " (" + to_string((int)(progress * 100)) + "%)";
		m_mainView->RenderText(TEXT_ALIGN_CENTER, winHeight - 10, GLUT_BITMAP_HELVETICA_12,
			msg.c_str(), 1.0f, 1.0f, 1.0f, 1.0f);

		float phoneZ = m_dcApi->GetLastTargetDistance() / 10.0f;

		if (phoneZ > 0)
		{
			stringstream stream;
			stream << "Target detected at " << fixed << setprecision(2) << phoneZ << "cm";
			string msg = stream.str();
			m_mainView->RenderText(TEXT_ALIGN_RIGHT, winHeight - 30, GLUT_BITMAP_HELVETICA_12,
				msg.c_str(), 1.0f, 1.0f, 1.0f, 1.0f);
			/*
					cout << msg << ", position: ";
					cout << "(" << m_phoneLoc[0] << "," << m_phoneLoc[1] << "), (" << m_phoneLoc[2] << "," << m_phoneLoc[3] << "),";
					cout << "(" << m_phoneLoc[4] << "," << m_phoneLoc[5] << "), (" << m_phoneLoc[6] << "," << m_phoneLoc[7] << ")";
					cout << endl;
			*/
		}
	}

    return true;
}
