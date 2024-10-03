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

#include "MainView.h"

namespace DynamicCalibrator
{
    class CliView : public MainView
    {
    public:
        CliView();
        virtual ~CliView();

        /* Initialization */
        int Initialize(void);

        /* Update calibration tables*/
        int UpdateCalibrationTablesComplete(std::string msg, bool bUpdated);

        /* Handling error message */
        void ErrorHandling(int errorCode);

        void OnDisplay();
        void OnKeyBoard(unsigned char key, int x, int y);

        void AddLog(std::string msg)
        {
            std::cout << msg << std::endl;
            m_logFile << msg << std::endl;
        }

    private:
        static void Control_C_Handler(int);

    private:
        int m_devIdx;
    };
}

