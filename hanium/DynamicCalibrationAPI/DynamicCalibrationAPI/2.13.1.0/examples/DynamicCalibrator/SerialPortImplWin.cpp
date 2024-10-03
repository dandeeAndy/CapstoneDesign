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

#include "SerialPortImplWin.h"

#include <iostream>

using namespace std;
using namespace GIMBAL;

SerialPort::SerialPort(string portName, char lineterminator)
{
    m_lineterminator = lineterminator;
    m_connected = false;

    m_hSerial = CreateFileA(portName.c_str(),
        GENERIC_READ | GENERIC_WRITE,
        0,
        0,
        OPEN_EXISTING,
        0,
        0);

    if (m_hSerial == INVALID_HANDLE_VALUE)
    {
        if (GetLastError() == ERROR_FILE_NOT_FOUND)
        {
            cout << "ERROR: Handle was not attached. Reason: " << portName << " not available." << endl;
        }
        else
        {
            cout << "ERROR!!! " << GetLastError() << endl;
        }

        return;
    }

    DCB dcb = { 0 };

    dcb.DCBlength = sizeof(DCB);
    if (!GetCommState(m_hSerial, &dcb))
    {
        cout << "failed to get current serial parameters!" << endl;

        return;
    }

    dcb.BaudRate = 19200;
    dcb.ByteSize = DATABITS_8;
    dcb.StopBits = ONESTOPBIT;
    dcb.Parity = (BYTE)PARITY_NONE;
    dcb.fDtrControl = 0;
    dcb.fRtsControl = 0;

    if (!SetCommState(m_hSerial, &dcb))
    {
        cout << "ALERT: Could not set Serial Port parameters" << endl;
    }
    else
    {
        // Clear the port of any existing data.
        PurgeComm(m_hSerial, PURGE_TXCLEAR | PURGE_RXCLEAR);

        ClearCommError(m_hSerial, NULL, NULL);

        m_connected = true;
    }
}

SerialPort::~SerialPort()
{
    if (m_connected)
    {
        m_connected = false;
        CloseHandle(m_hSerial);
    }
}

bool SerialPort::IsConnected(void)
{
    return m_connected;
}

string SerialPort::ReadLine(void)
{
    string line = "";
    char ch;
    DWORD bytesRead;

    while (true)
    {
        bytesRead = 0;

        if (ReadFile(m_hSerial, &ch, 1, &bytesRead, NULL)
            && (bytesRead == 1)
            )
        {
            if (ch == m_lineterminator)
            {
                break;
            }
            else
            {
                line += ch;
            }
        }
    }

    return line;
}

void SerialPort::WriteLine(string line)
{
    DWORD bytesSend;

    WriteFile(m_hSerial, line.c_str(), (DWORD)line.length(), &bytesSend, NULL);

    WriteFile(m_hSerial, &m_lineterminator, 1, &bytesSend, NULL);
}

