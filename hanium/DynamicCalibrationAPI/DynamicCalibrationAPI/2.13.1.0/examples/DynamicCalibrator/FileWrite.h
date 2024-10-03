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

#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <iomanip>
#ifdef _WIN32
#include <direct.h>
#else
#include <sys/stat.h>
#endif
#include <stdlib.h>
#include <stdio.h>

using namespace std;

namespace DynamicCalibrator
{
    class FileWrite
    {
#define DTTMFMT "%Y-%m-%d-%H-%M-%S"
#define DTTMSZ 32
#define MAX_PATH_LEN 260

    public:
        FileWrite()
		{
			mSaveRgb = false;
			mIndex = 0;
		};

        ~FileWrite() {};

        void SetDirectory(string dir)
        {
            mIndex = 0;
            mDir = dir;

            mSaveRgb = false;
            if (dir.find("RGB") != string::npos || dir.find("rgb") != string::npos)
                mSaveRgb = true;
#ifdef _WIN32
            _mkdir(mDir.c_str());
#else
            mkdir(mDir.c_str(), S_IRUSR | S_IWUSR | S_IXUSR);
#endif
        }

        void SaveFrameToFile(uint8_t * leftImage, uint8_t * rightImage, uint16_t * otherImage,
            int w, int h)
        {
            SaveImageToFiles(leftImage, rightImage, otherImage, w, h);
        }

    private:
        void WriteBinFile(const char *fileName, uint8_t *image, int filesize)
        {
            ofstream myFile(fileName, ios::out | ios::binary);

            myFile.write((const char*)image, filesize);

            myFile.close();
        }

        void SaveImageToFiles(uint8_t * leftImage, uint8_t * rightImage, uint16_t * otherImage, int w, int h)
        {
            mIndex += 1;
            stringstream ss;
            ss << std::setw(3) << std::setfill('0') << mIndex;

            string leftFileName = mDir + "/leftImage" + ss.str() + ".bin";
            WriteBinFile(leftFileName.c_str(), leftImage, w * h);

            string rightFileName = mDir + "/rightImage" + ss.str() + ".bin";
            WriteBinFile(rightFileName.c_str(), rightImage, w * h);

            if (otherImage)
            {
                if (!mSaveRgb)
                {
                    string depthFileName = mDir + "/depthImage" + ss.str() + ".bin";
                    WriteBinFile(depthFileName.c_str(), (uint8_t *)otherImage, w * h * sizeof(uint16_t));
                }
                else
                {
                    string colorFileName = mDir + "/colorImage" + ss.str() + ".bin";
                    WriteBinFile(colorFileName.c_str(), (uint8_t *)otherImage, w * h * sizeof(uint16_t));
                }
            }
        }

    private:
        int mIndex;
        string mDir;
        bool mSaveRgb;
    };
}
