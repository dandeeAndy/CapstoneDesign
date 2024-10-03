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
#include <string>
#include "MainView.h"

using namespace std;
using namespace DynamicCalibrator;

MainView::MainView()
{
    m_targeted = true;
    m_calibration_mode = 1;
    m_scaleCalibOnly = false;
    m_rgbCalib = false;
    m_hybrid = false;

    m_aesweepmode = AE_SWEEP_AUTO;

    m_aeSetpoint = 1000;
    m_aeSetpointMin = 0;
    m_aeSetpointMax = 4095;
    m_aeSetpointDefault = 1000;

    m_aeRgbBrightness = 0;
    m_aeRgbBrightnessMin = -64;
    m_aeRgbBrightnessMax =  64;
    m_aeRgbBrightnessDefault = 0;

    m_useLaser = true;
    m_autoExposureEnable = true;

    m_depthExposure = 6500;
    m_colorExposure = 300;
    m_depthExposureMin = 20;
    m_depthExposureMax = 166000;
    m_colorExposureMin = 39;
    m_colorExposureMax = 10000;

    m_width = 0;
    m_height = 0;

    m_width_rgb = 0;
    m_height_rgb = 0;

    m_winWidth = 0;
    m_winHeight = 0;

    m_image = nullptr;
    m_texture = 0;

    m_timeout = 0;
    m_sn.clear();
    m_runningStatus = STATUS_NOT_STARTED;
    m_errorCode = DC_SUCCESS;

    m_colorImage = nullptr;

    m_cameras.clear();

    for (int i = 0; i < 4; i++) m_viewport[i] = 0;

    m_skiprgb = false;
    max_target_images = MAX_NUM_TARGET_IMAGES;
    m_ignore_borders = false;
    m_loglevel = 0;

    pGimbal = NULL;
    m_device_target_same_orientation = false;
}

MainView::~MainView()
{
    if (m_logFile.is_open()) m_logFile.close();

    if (m_captureManager)
    {
        if (m_runningStatus == STATUS_RUNNING)
            m_captureManager->StopCapture();

        m_captureManager->~CaptureManager();
    }
}

void MainView::RenderImage()
{
    if (m_image == nullptr) return;

    glClearColor(0.0f, 0.0f, 0.0f, 1);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

    glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, m_width, m_height, 0, GL_LUMINANCE, GL_UNSIGNED_BYTE, m_image);

	/*
	float ratioImg = float(m_width) / m_height;
	float ratioWin = float(m_winWidth) / m_winHeight;

	cout << "render image: " << m_width << "," << m_height << ", ratioImg=" << ratioImg << " : ";
	cout << "glut window:" << m_winWidth << "," << m_winHeight << ", ratio win=" << ratioWin << " : ";

	GLfloat orig_width = m_winWidth;
	GLfloat orig_height = m_winHeight;

	GLfloat gl_width = m_winWidth;
	GLfloat gl_height = m_winHeight;

	// remember those to be able to center the quad on screen

	if (ratioImg > ratioWin)
		gl_height = gl_width / ratioImg;
	else
		gl_width = gl_height * ratioImg;

	cout << "gl quad:" << gl_width << "," << gl_height << " : ";
	// calculate image size

	double offset_x = 0 + (orig_width - gl_width)/ orig_width;
	double offset_y = 0 + (orig_height - gl_height) /orig_height;

	cout << "offset:" << offset_x << "," << offset_y;
	// center on screen

	cout << endl;
*/
	float ratioImg = float(m_width) / m_height;
	float ratioWin = float(m_winWidth) / m_winHeight;

	float ratioX = 1.0;
	float ratioY = 1.0;

	if (ratioImg >= ratioWin)
		ratioY = ratioWin / ratioImg;
	else
		ratioX = ratioImg / ratioWin;


    // Render image
    glEnable(GL_TEXTURE_2D);
	glBindTexture(GL_TEXTURE_2D, m_texture);

    glColor4ub(255, 255, 255, 255);
    
	glBegin(GL_QUADS);

    glTexCoord2d(0, 1);
    glVertex2d(-1.0 * ratioX, -1.0 * ratioY);
//	glVertex2f(offset_x - 1.0, offset_y - 1.0);
    
	glTexCoord2d(0, 0);
    glVertex2d(-1.0 * ratioX, 1.0 * ratioY);
//	glVertex2f(offset_x - 1.0, 1.0 - offset_y);


	glTexCoord2d(1, 0);
    glVertex2d(1.0 * ratioX, 1.0 * ratioY);
//	glVertex2f(1.0 - offset_x, 1.0 - offset_y);
    
	glTexCoord2d(1, 1);
    glVertex2d(1.0 * ratioX, -1.0 * ratioY);
//	glVertex2f(1.0 - offset_x, offset_y - 1.0);
    
	glEnd();
    glDisable(GL_TEXTURE_2D);
}

void MainView::RenderColorImage()
{
    if (m_image == nullptr || m_colorImage == nullptr) return;

    glClearColor(0.0f, 0.0f, 0.0f, 1);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

    if (m_rgbImage == nullptr)
        m_rgbImage = std::unique_ptr<uint32_t[]>(new uint32_t[m_width_rgb*(m_height_rgb + 1)]);

    uint32_t *rgbImage = m_rgbImage.get();
    ConvertYUY2ToRGBA((uint8_t *)m_colorImage, m_width_rgb, m_height_rgb, (uint8_t *)rgbImage);

	float ratioImg = float(m_width_rgb) / m_height_rgb;
	float ratioWin = float(m_winWidth) / m_winHeight;

	float ratioX = 1.0;
	float ratioY = 1.0;

	if (ratioImg >= ratioWin)
		ratioY = ratioWin / ratioImg;
	else
		ratioX = ratioImg / ratioWin;

    glClearColor(0.0f, 0.0f, 0.0f, 1);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

    // Render image
    glEnable(GL_TEXTURE_2D);
    glColor4ub(255, 255, 255, 255);

    glBindTexture(GL_TEXTURE_2D, m_textures[1]);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP);

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, m_width_rgb, m_height_rgb, 0, GL_RGBA, GL_UNSIGNED_BYTE, rgbImage);

    glBegin(GL_QUADS);
    glTexCoord2d(0, 1); glVertex2d(-1.0 * ratioX, -1.0 * ratioY);
    glTexCoord2d(0, 0); glVertex2d(-1.0 * ratioX, 1.0 * ratioY);
    glTexCoord2d(1, 0); glVertex2d(1.0 * ratioX, 1.0 * ratioY);
    glTexCoord2d(1, 1); glVertex2d(1.0 * ratioX, -1.0 * ratioY);
    glEnd();

    glBindTexture(GL_TEXTURE_2D, m_textures[0]);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP);

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, m_width, m_height, 0, GL_LUMINANCE, GL_UNSIGNED_BYTE, m_image);

    glBegin(GL_QUADS);
    glTexCoord2d(0, 1); glVertex2d(-1.0 * ratioX, -1.0 * ratioY);
    glTexCoord2d(0, 0); glVertex2d(-1.0 * ratioX, -0.5 * ratioY);
    glTexCoord2d(1, 0); glVertex2d(-0.5 * ratioX, -0.5 * ratioY);
    glTexCoord2d(1, 1); glVertex2d(-0.5 * ratioX, -1.0 * ratioY);
    glEnd();

    glDisable(GL_TEXTURE_2D);
}

void MainView::BlendBlocks(std::vector<RECTANGLE> blocks, std::vector<COLOR> colors)
{
	float ratioImg = float(m_width) / m_height;
	float ratioWin = float(m_winWidth) / m_winHeight;

	float ratioX = 1.0;
	float ratioY = 1.0;

	if (ratioImg >= ratioWin)
		ratioY = ratioWin / ratioImg;
	else
		ratioX = ratioImg / ratioWin;
	
	glEnable(GL_BLEND);
    glBegin(GL_QUADS);

    for (int i = 0; i < blocks.size(); i++)
    {
        glColor4ub(colors[i].R, colors[i].G, colors[i].B, colors[i].A);

//		cout << i << ":" << blocks[i].left << "," << blocks[i].right << "," << blocks[i].top << "," << blocks[i].bottom << endl;

        glVertex2d(blocks[i].left * ratioX, blocks[i].top * ratioY);
        glVertex2d(blocks[i].right * ratioX, blocks[i].top * ratioY);
        glVertex2d(blocks[i].right * ratioX, blocks[i].bottom * ratioY);
        glVertex2d(blocks[i].left * ratioX, blocks[i].bottom * ratioY);
    }

    glEnd();
    glDisable(GL_BLEND);
}

void MainView::RenderLines(std::vector<POINT_D> points, COLOR color, int lineWidth)
{
    glEnable(GL_BLEND);
    glLineWidth((GLfloat)lineWidth);

    glBegin(GL_LINE_LOOP);
    glColor4ub(color.R, color.G, color.B, color.A);

    for (int i = 0; i < points.size(); i++)
    {
        glVertex2d(points[i].x, points[i].y);
    }

    glEnd();
    glDisable(GL_BLEND);
}

void MainView::SetViewport(GLint x, GLint y, GLsizei width, GLsizei height)
{
    m_viewport[0] = x;
    m_viewport[1] = y;
    m_viewport[2] = width;
    m_viewport[3] = height;

    glViewport(x, y, width, height);
}

void MainView::RenderText(int x, int y, void *font, const char* message,
    float r, float g, float b, float a)
{
    int viewport_w = m_viewport[2];
    int viewport_h = m_viewport[3];

    glEnable(GL_BLEND);
    glPushAttrib(GL_ALL_ATTRIB_BITS);
    glMatrixMode(GL_PROJECTION);
    glPushMatrix();
    glLoadIdentity();
    gluOrtho2D(0, viewport_w, viewport_h, 0);

    glMatrixMode(GL_MODELVIEW);
    glPushMatrix();
    glLoadIdentity();

    glColor4f(r, g, b, a);

    int nStrLengthPixels = 0;

    if (x < 0)
    {
        for (char *p = (char*)message; *p; p++)
        {
            if (*p == '\n') break;
            nStrLengthPixels += glutBitmapWidth(font, *p);
        }
    }

    if (TEXT_ALIGN_LEFT == x)
    {
        x = 10;
    }
    else if (TEXT_ALIGN_CENTER == x)
    {
        // auto center x
        x = (viewport_w - nStrLengthPixels) >> 1;
    }
    else if (TEXT_ALIGN_RIGHT == x)
    {
        x = viewport_w - nStrLengthPixels - 10;
    }

    if (TEXT_ALIGN_TOP == y)
    {
        y = glutBitmapHeight(font);
    }
    else if (TEXT_ALIGN_CENTER == y)
    {
        // auto center y
        y = viewport_h >> 1;
    }
    else if (TEXT_ALIGN_BOTTOM == y)
    {
        y = viewport_h - glutBitmapHeight(font) - 10;
    }
    glRasterPos2f((GLfloat)x, (GLfloat)y);

    glutBitmapString(font, (const unsigned char*)message);

    // Restore GL state to what it was prior to this call
    glPopMatrix();
    glMatrixMode(GL_PROJECTION);
    glPopMatrix();
    glPopAttrib();
    glDisable(GL_BLEND);
}

int MainView::StartCapture(int idx)
{
    m_errorCode = DC_SUCCESS;

    // Start the calibration:
    camera_info camera = m_cameras[idx];

    // default stream profile for dynamic calibration
	m_width = 1280;
	m_height = 720;

	int fps = 30;

    // special device
	if (camera.pid.compare("0B0C") == 0)
	{
		m_width = 720;
		m_height = 720;
	}

	m_width_rgb = m_width;
	m_height_rgb = m_height;

    // For D455 and D450 USB devices and D457 MIPI devices, calibrate RGB at max resolution 1280 x 800 for better accuracy
    if (m_rgbCalib && (camera.pid.compare("0B5C") == 0 || camera.pid.compare("ABCD") == 0))
    {
        m_width = 1280;
        m_height = 720;

        m_width_rgb = 1280;
        m_height_rgb = 800;
    }

    bool bLaser = false;
    if (!m_targeted)
    {
        if ((camera.features & HAS_EMITTER) && (0 != m_useLaser))
        {
            bLaser = true;
        }
    }

	DSDynamicCalibration::CalibrationMode calibMode = m_rgbCalib ? DSDynamicCalibration::CalibrationMode::CAL_MODE_INTEL_RGB_CALIB :
        m_targeted ? DSDynamicCalibration::CalibrationMode::CAL_MODE_INTEL_TARGETED : DSDynamicCalibration::CalibrationMode::CAL_MODE_INTEL_TARGETLESS;

	if (m_scaleCalibOnly)
	{
		calibMode = DSDynamicCalibration::CalibrationMode::CAL_MODE_INTEL_TARGETED_SCALE_ONLY;
	}

	AddLog("Streamming Resolution: " + to_string(m_width) + "x" + to_string(m_height) + " at " + to_string(fps) + "(fps)");

	if (pGimbal)
	{
		switch (calibMode)
		{
		case DSDynamicCalibration::CalibrationMode::CAL_MODE_INTEL_TARGETLESS:
			pGimbal->EnableTargetMode(false);
			break;

		case DSDynamicCalibration::CalibrationMode::CAL_MODE_INTEL_TARGETED:
			break;

		case DSDynamicCalibration::CalibrationMode::CAL_MODE_INTEL_TARGETED_SCALE_ONLY:
			pGimbal->EnableTargetMode(true);
			break;

		case DSDynamicCalibration::CalibrationMode::CAL_MODE_INTEL_RGB_CALIB:
			pGimbal->EnableTargetMode(true);
			break;
		}

		pGimbal->SetDeviceWarmUP(true);
	}

    m_captureManager->EnableAutoExposure(m_autoExposureEnable);
    if (!m_autoExposureEnable)
    {
        m_captureManager->SetExposure(m_depthExposure, false);
        m_captureManager->SetExposure(m_colorExposure, true);
    }

    return m_captureManager->StartCapture(m_width, m_height, fps,
        calibMode, bLaser, m_aeSetpoint, camera.features, m_aesweepmode, m_device_target_same_orientation, max_target_images, m_ignore_borders, m_width_rgb, m_height_rgb, fps);
}

void MainView::InitializeGL(void *viewClass)
{
    int c = 0;

    // Open a GLUT window to display point cloud
    glutInit(&c, nullptr);
    glutInitDisplayMode(GLUT_RGBA | GLUT_DEPTH | GLUT_DOUBLE);

    int width = glutGet(GLUT_SCREEN_WIDTH);
    int height = glutGet(GLUT_SCREEN_HEIGHT);

	cout << "display size: " << width << "," << height << " with aspect ratio " << (float) width / height << endl;

    glutInitWindowSize( width * 0.75,  width * 0.75 / (1280.0 / 720.0));

    string AppName = "Intel RealSense Dynamic Calibrator";
    string AppTitle = AppName + " v" + DS_DYNAMIC_CALIBRATION_VERSION;
    glutCreateWindow(AppTitle.c_str());

    glutSetWindowData(viewClass);

    glutDisplayFunc([]() {
        MainView *pView = reinterpret_cast<MainView *>(glutGetWindowData());
        pView->OnDisplay();
    });
    glutCloseFunc([]() {
        MainView *pView = reinterpret_cast<MainView *>(glutGetWindowData());
        pView->OnClose();
    });
    glutReshapeFunc([](int width, int height) {
        MainView *pView = reinterpret_cast<MainView *>(glutGetWindowData());
        pView->OnReShape(width, height);
    });
    glutKeyboardFunc([](unsigned char key, int x, int y) {
        MainView *pView = reinterpret_cast<MainView *>(glutGetWindowData());
        pView->OnKeyBoard(key, x, y);
    });


    glutSetOption(GLUT_ACTION_ON_WINDOW_CLOSE, GLUT_ACTION_GLUTMAINLOOP_RETURNS);

    m_winWidth = glutGet(GLUT_WINDOW_WIDTH);
    m_winHeight = glutGet(GLUT_WINDOW_HEIGHT);
    SetViewport(0, 0, m_winWidth, m_winHeight);

	cout << "window size: " << m_winWidth << "," << m_winHeight << " with aspect ratio " << (float)m_winWidth / m_winHeight << endl;

    glGenTextures(1, &m_texture);

    glBindTexture(GL_TEXTURE_2D, m_texture);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP);

    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    glPointSize(3.0);

    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();

	glGenTextures(2, m_textures);
}


bool MainView::IsFwVersionSupported(camera_info info)
{
    std::string fw_version = info.fw_ver;

    int idx0 = (int)fw_version.find_first_of(".");
    int idx1 = (int)fw_version.find_first_of(".", idx0 + 1);
    int minor = stoi(fw_version.substr(idx0 + 1, idx1));
    idx0 = (int)fw_version.find_first_of(".", idx1 + 1);
    int patch = stoi(fw_version.substr(idx1 + 1, idx0));

    if ((minor < info.minFWVerMinor)
        || ((minor == info.minFWVerMinor) && (patch < info.minFWVerPatch))
        )
    {
        return false;
    }

    return true;
}

bool MainView::IsUsb2(camera_info info)
{
    bool res = false;

    if (starts_with(info.usb_type, "2"))
    {
        res = true;
    }

    return res;
}

bool MainView::IsUsb3(camera_info info)
{
    bool res = false;

    if (starts_with(info.usb_type, "3"))
    {
        res = true;
    }

    return res;
}

void MainView::OnIdle()
{
    m_image = m_captureManager->OnIdle();
}

void  MainView::OnReShape(int width, int height)
{
    m_winWidth = width;
    m_winHeight = height;

    SetViewport(0, 0, (GLsizei)width, (GLsizei)height);
    glutPostRedisplay();
}

void MainView::SetOptions(void)
{
    if (m_CmdOptions.bAESweepAuto)
    {
        m_aesweepmode = AE_SWEEP_AUTO;
    }
    else
    {
        m_aesweepmode = AE_SWEEP_MANUAL;
    }

    m_aeSetpoint = m_CmdOptions.AESetpoint;

    if (m_aeSetpoint < 0) m_aeSetpoint = 1000;
    if (m_aeSetpoint > 4095) m_aeSetpoint = 1000;

    m_useLaser = m_CmdOptions.UseLaser;

    m_timeout = m_CmdOptions.timeOut;
    m_sn = m_CmdOptions.CameraSerial;

    m_autoExposureEnable = !m_CmdOptions.bAutoExposureDisable;
    if (m_CmdOptions.depthExposure >= m_depthExposureMin)
        m_depthExposure = m_CmdOptions.depthExposure;
    if (m_CmdOptions.colorExposure >= m_colorExposureMin)
        m_colorExposure = m_CmdOptions.colorExposure;


	m_calibration_mode = m_CmdOptions.calibrationMode;

	// calibration mode
	// 0 - target-less rectification
	// 1 - targeted calibration (targeted rectification + targeted scale) (default)
	// 2 - hybrid calibration (target-less rectification + targeted scale calibration)
	// 3 - scale calibration
	// 4 - rgb calibration

	// settings per calibration mode 
	switch (m_calibration_mode)
	{
	case 0:
		m_targeted = false;
		m_scaleCalibOnly = false;
		m_rgbCalib = false;
		break;

	case 1:
		m_targeted = true;
		m_scaleCalibOnly = false;
		m_rgbCalib = false;
		break;

	case 2:
		m_targeted = false;
		m_scaleCalibOnly = false;
		m_rgbCalib = false;

		m_hybrid = true;
		break;

	case 3:
		m_targeted = true;
		m_scaleCalibOnly = true;
		m_rgbCalib = false;
		break;

	case 4:
		m_targeted = true;
		m_scaleCalibOnly = false;
		m_rgbCalib = true;
		break;
	}

//	cout << m_calibration_mode << ":" << m_targeted << "," << m_scaleCalibOnly << "," << m_rgbCalib << endl;


	m_skiprgb = m_CmdOptions.bSkipRGB;
	m_device_target_same_orientation = m_CmdOptions.bDevTargetAligned;

	if (m_CmdOptions.numScaleImages <= 0)
	{
		max_target_images = MAX_NUM_TARGET_IMAGES;

		if (m_hybrid)
		{
			if (m_device_target_same_orientation)
				max_target_images = MAX_NUM_TARGET_IMAGES_ROBOT_ALIGNED;
			else
				max_target_images = MAX_NUM_TARGET_IMAGES_ROBOT_UNALIGNED;
		}
	}
	else
	{
		max_target_images = m_CmdOptions.numScaleImages;
	}

	m_ignore_borders = m_CmdOptions.bIgnoreBorders;

	m_loglevel = m_CmdOptions.bVerbose == false ? 0 : 1;
}

void MainView::GetExposureValue(int idx)
{
    m_depthExposureMin = m_cameras[idx].depthExposureMin;
    m_depthExposureMax = m_cameras[idx].depthExposureMax;
    m_depthExposure = m_cameras[idx].depthExposure;

	m_aeSetpoint = m_cameras[idx].depthSetpoint;
	m_aeSetpointMin = m_cameras[idx].depthSetpointMin;
	m_aeSetpointMax = m_cameras[idx].depthSetpointMax;
	m_aeSetpointDefault = m_cameras[idx].depthSetpointDefault;

    if (m_cameras[idx].features & SKU_RGB)
    {
        m_colorExposureMin = m_cameras[idx].colorExposureMin;
        m_colorExposureMax = m_cameras[idx].colorExposureMax;
        m_colorExposure = m_cameras[idx].colorExposure;

		m_aeRgbBrightness = m_cameras[idx].rgbBrightness;
		m_aeRgbBrightnessMin = m_cameras[idx].rgbBrightnessMin;
		m_aeRgbBrightnessMax = m_cameras[idx].rgbBrightnessMax;
		m_aeRgbBrightnessDefault = m_cameras[idx].rgbBrightnessDefault;
    }
}

void MainView::ConvertYUY2ToRGBA(const uint8_t* image, int width, int height, uint8_t* output)
{
    int n = width*height;
    auto src = image;
    auto dst = output;
    for (; n; n -= 16, src += 32)
    {
        int16_t y[16] = {
            src[0], src[2], src[4], src[6],
            src[8], src[10], src[12], src[14],
            src[16], src[18], src[20], src[22],
            src[24], src[26], src[28], src[30],
        }, u[16] = {
            src[1], src[1], src[5], src[5],
            src[9], src[9], src[13], src[13],
            src[17], src[17], src[21], src[21],
            src[25], src[25], src[29], src[29],
        }, v[16] = {
            src[3], src[3], src[7], src[7],
            src[11], src[11], src[15], src[15],
            src[19], src[19], src[23], src[23],
            src[27], src[27], src[31], src[31],
        };

        uint8_t r[16], g[16], b[16];
        for (int i = 0; i < 16; i++)
        {
            int32_t c = y[i] - 16;
            int32_t d = u[i] - 128;
            int32_t e = v[i] - 128;

            int32_t t;
#define clamp(x)  ((t=(x)) > 255 ? 255 : t < 0 ? 0 : t)
            r[i] = clamp((298 * c + 409 * e + 128) >> 8);
            g[i] = clamp((298 * c - 100 * d - 208 * e + 128) >> 8);
            b[i] = clamp((298 * c + 516 * d + 128) >> 8);
#undef clamp
        }

        uint8_t out[16 * 4] = {
            r[0], g[0], b[0], 255, r[1], g[1], b[1], 255,
            r[2], g[2], b[2], 255, r[3], g[3], b[3], 255,
            r[4], g[4], b[4], 255, r[5], g[5], b[5], 255,
            r[6], g[6], b[6], 255, r[7], g[7], b[7], 255,
            r[8], g[8], b[8], 255, r[9], g[9], b[9], 255,
            r[10], g[10], b[10], 255, r[11], g[11], b[11], 255,
            r[12], g[12], b[12], 255, r[13], g[13], b[13], 255,
            r[14], g[14], b[14], 255, r[15], g[15], b[15], 255,
        };

        DS_MEMCPY_S((void *)dst, sizeof out, out, sizeof out);
        dst += sizeof out;
    }
}

void MainView::CreateLogDirectory(std::string serial)
{
	string datadir;

#ifdef _WIN32
	// local app data folder on Windows
	// %LocalAppData%
	// C:\Users\{username}\AppData\Local

	char* localapp = getenv("LocalAppData");

	if (localapp != NULL)
		datadir = localapp;
	else
		datadir = ".";

	datadir += "/Intel/";

	if (!file_exist(datadir.c_str()))
	{
		_mkdir(datadir.c_str());
	}

	datadir += "/DC/";

	if (!file_exist(datadir.c_str()))
	{
		_mkdir(datadir.c_str());
	}

	datadir += "/DyCalibResult/";
#else
	datadir = "DyCalibResult/";
#endif

    if (!file_exist(datadir.c_str()))
    {
#ifdef _WIN32
        _mkdir(datadir.c_str());
#else
         mkdir(datadir.c_str(), S_IRUSR | S_IWUSR | S_IXUSR);
#endif
    }

    m_dir = datadir + serial;
    if (!file_exist(m_dir.c_str()))
    {
#ifdef _WIN32
        _mkdir(m_dir.c_str());
#else
        mkdir(m_dir.c_str(), S_IRUSR | S_IWUSR | S_IXUSR);
#endif
    }

    m_dir = m_dir + "/DC";
    for (int i = 1; ; i++)
    {
        string DC = m_dir + to_string(i);

        if (!file_exist(DC.c_str()))
        {
            m_dir = DC;
            break;
        }
    }

#ifdef _WIN32
    _mkdir(m_dir.c_str());
#else
        mkdir(m_dir.c_str(), S_IRUSR | S_IWUSR | S_IXUSR);
#endif

    if (m_logFile.is_open()) m_logFile.close();

    string fileName = m_dir.c_str();
    fileName += "/log.txt";
    m_logFile.open(fileName, std::ios::out);
}
