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


#ifndef _DS_CALDATA_H_
#define _DS_CALDATA_H_

// calibration tables for Intel RealSense D400 series depth cameras
// calibration data used by D400 devices are organized in three separate
// tables in Intel proprietary internal formats.
//   coefficient table (0x19) - required on every device
//   depth table (0x1F) - required on every device
//   rgb table (0x20) - only required when the device has rgb, for example, on device D415, D435, D435, etc.
// CustomRW tool can read/write these table individually to the device, but they work in sets together.
// sets of tables from one calibration cannot be mixed with other sets of tables from another calibration.
//
// calibration table size in bytes
#define DC_CALIB_COEFF_TABLE_SIZE     512   // coefficient table (0x19)
#define DC_CALIB_DEPTH_TABLE_SIZE     256   // depth table (0x1F)
#define DC_CALIB_RGB_TABLE_SIZE       256   // rgb table (0x20)

//  The Vision Calibration Data is an Intel prietary binary file lumped all tables together in the order
//     coefficient table (0x19) 512 bytes
//     depth table (0x1F)       256 bytes
//     rgb table (0x20)         256 bytes (only applies for devices with rgb)
//   since coeffcient table and depth table are required on every device, so the input file size is either
//   768 bytes or 1024 bytes.

// minimum vision data size 768 bytes (include coeffient and depth tables)
#define MIN_VISION_DATA_SIZE (DC_CALIB_COEFF_TABLE_SIZE + DC_CALIB_DEPTH_TABLE_SIZE)

// maximum vision data size 1024 bytes (include coeffient, depth, and rgb tables)
#define MAX_VISION_DATA_SIZE (DC_CALIB_COEFF_TABLE_SIZE + DC_CALIB_DEPTH_TABLE_SIZE + DC_CALIB_RGB_TABLE_SIZE)

#pragma pack(push, 1)

// Calibration coefficients table. Table ID = 0x19
struct DS5CoefficientsParamsTable
{
    uint8_t data[DC_CALIB_COEFF_TABLE_SIZE];
};

// Depth calibration table. Table ID = 0x1F
struct DS5DepthCalibrationParamsTable
{
    uint8_t data[DC_CALIB_DEPTH_TABLE_SIZE];
};

// RGB calibration table. TableID = 0x20
struct DS5RgbCalibrationParamsTable
{
    uint8_t data[DC_CALIB_RGB_TABLE_SIZE];
};

// only for targeted calibration
#define DC_CALIB_CALC_TABLE_SIZE      256

// CalibRecalc coefficient table
struct DS5CoefficientsUpdateParam
{
    uint8_t data[DC_CALIB_CALC_TABLE_SIZE];
};

// only for fisheye
#define DC_MM_FE_CUSTOM_DATA_SIZE     136   // 0x88

#pragma pack(pop)

#endif //_DS_CALDATA_H_
