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

#ifndef __RS_HMC_H__
#define __RS_HMC_H__

#define DS5_CMD_LENGTH          24
#define DS5_OUTPUT_BUFFER_SIZE  1024
#define DS5_CMD_OPCODE_SIZE     4

static uint8_t gvd_cmd[DS5_CMD_LENGTH] = { 0x14, 0x0, 0xab, 0xcd, 0x10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
static uint8_t hw_reset_cmd[DS5_CMD_LENGTH] = { 0x14, 0x0, 0xab, 0xcd, 0x20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };


static uint8_t GetCoefficientsData_Cmd[DS5_CMD_LENGTH] = { 0x14, 0x0, 0xab, 0xcd, 0x15, 0, 0, 0, 0x19, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
static uint8_t SetCoefficientsData_Cmd[DS5_CMD_LENGTH] = { 0x14, 0x0, 0xab, 0xcd, 0x62, 0, 0, 0, 0x19, 0, 0, 0, 0x01, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
static uint8_t SetIntermediateCoefficientsData_Cmd[DS5_CMD_LENGTH] = { 0x14, 0x0, 0xab, 0xcd, 0x51, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };

static uint8_t GetDepthCalibrationData_Cmd[DS5_CMD_LENGTH] = { 0x14, 0x0, 0xab, 0xcd, 0x15, 0, 0, 0, 0x1f, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
static uint8_t SetDepthCalibrationData_Cmd[DS5_CMD_LENGTH] = { 0x14, 0x0, 0xab, 0xcd, 0x62, 0, 0, 0, 0x1f, 0, 0, 0, 0x01, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };

static uint8_t GetRgbCalibrationData_Cmd[DS5_CMD_LENGTH] = { 0x14, 0x0, 0xab, 0xcd, 0x15, 0, 0, 0, 0x20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
static uint8_t SetRgbCalibrationData_Cmd[DS5_CMD_LENGTH] = { 0x14, 0x0, 0xab, 0xcd, 0x62, 0, 0, 0, 0x20, 0, 0, 0, 0x01, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };

static uint8_t GetFisheyeCalibrationData_Cmd[DS5_CMD_LENGTH] = { 0x14, 0x0, 0xab, 0xcd, 0x15, 0, 0, 0, 0x21, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
static uint8_t SetFisheyeCalibrationData_Cmd[DS5_CMD_LENGTH] = { 0x14, 0x0, 0xab, 0xcd, 0x62, 0, 0, 0, 0x21, 0, 0, 0, 0x01, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };

static uint8_t MMER_Cmd[DS5_CMD_LENGTH] = { 0x14, 0x0, 0xab, 0xcd, 0x4F, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
static uint8_t MMEW_Cmd[DS5_CMD_LENGTH] = { 0x14, 0x0, 0xab, 0xcd, 0x50, 0, 0, 0, 0, 0, 0, 0, 0x01, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };

static uint8_t AMCSET[DS5_CMD_LENGTH] = { 0x14, 0x0, 0xab, 0xcd, 0x2B, 0, 0, 0, 0x09, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 }; // set advanced mode control - depth table control
static uint8_t AMCGET[DS5_CMD_LENGTH] = { 0x14, 0x0, 0xab, 0xcd, 0x2C, 0, 0, 0, 0x09, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 }; // get advanced mode control - depth table control

																															  // Reset calibration table to factory settings from gold tables from flash
static uint8_t CALIBRESTOREDEFAULT_Cmd[DS5_CMD_LENGTH] = { 0x14, 0x0, 0xab, 0xcd, 0x61, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };

typedef struct
{
	uint32_t depthUnits;
	int32_t  depthClampMin;
	int32_t  depthClampMax;
	uint32_t disparityMode;
	int32_t  disparityShift;
} DepthTableControl;

#endif