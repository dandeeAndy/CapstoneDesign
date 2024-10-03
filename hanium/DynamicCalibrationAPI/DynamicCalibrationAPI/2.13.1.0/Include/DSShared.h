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

#ifndef DS_SHARED_H_
#define DS_SHARED_H_

#pragma once

#include <map>

/// Error code
#define DC_SUCCESS                                              0   // successful
#define DC_ERROR_SCALE_DEPTH_TOO_SPARSE                         4   // depth too sparse on target (maybe reflection)
#define DC_ERROR_SCALE_DEPTH_NOT_CONSISTENT                     6   // target depth is not consistent between dense and sparse features
#define DC_ERROR_SCALE_TARGET_TILT_ANGLE_BIG                   10   // target tilt angle too big
#define DC_ERROR_SCALE_FAILED_COMPUTE                          11   // failed to calculate correction angle
#define DC_ERROR_SCALE_ALREADY_CAPTURED                        12   // already captured
#define DC_ERROR_SCALE_DEPTH_NOT_A_PLANE                       13   // depth not fit on a plane
#define DC_ERROR_RECTIFICATION_PHASE                           14   // incorrect rectification phase
#define DC_ERROR_SCALE_PHASE_START_FAILED                      15   // failed to start scale calibration phase
#define DC_ERROR_WRONG_PHASE                                   16   // wrong phase
#define DC_ERROR_GET_TARGETED_CALIBRATION_CORRECTION           17   // failed to get targeted calibration correction

#define DC_ERROR_RECT_INVALID_IMAGES                         1001   // images are invalid
#define DC_ERROR_RECT_TOO_SIMILAR                            1002   // images too similar
#define DC_ERROR_RECT_TARGET_NOT_FOUND_LEFT                  1003   // rectification target not found in left image
#define DC_ERROR_RECT_TARGET_NOT_FOUND_RIGHT                 1004   // rectification target not found in right image
#define DC_ERROR_RECT_TARGET_NOT_FOUND_BOTH                  1005   // target not detected in both left and right images
#define DC_ERROR_RECT_TARGET_NOT_CONSISTENT                  1006   // target not consistent between left and right images
#define DC_ERROR_RECT_GRID_FULL                              1007   // grid is full, no more images needed
#define DC_ERROR_RECT_INVALID_GRID_FILL                      1008   // invalid grid fill
#define DC_ERROR_RECT_TOO_MUCH_FEATURES                      1009   // too much features
#define DC_ERROR_RECT_NO_FEATURES                            1010   // no features

#define DC_ERROR_TARGET_UNSTABLE                             1011   // target not stable
#define DC_ERROR_TARGET_TOO_CLOSE                            1012   // too close
#define DC_ERROR_TARGET_TOO_FAR                              1013   // too far
#define DC_ERROR_PHASE_COMPLETED                             1014   // phase completed, no more image accepted

#define DC_ERROR_RECT_TARGET_NOT_FOUND_RGB                   1015   // rectification target not found in rgb image
#define DC_ERROR_RECT_TARGET_NOT_FOUND_LEFT_RGB              1016   // rectification target not found in left and rgb image
#define DC_ERROR_RECT_TARGET_NOT_FOUND_RIGHT_RGB             1017   // rectification target not found in right and rgb image
#define DC_ERROR_RECT_TARGET_NOT_FOUND_ALL                   1018   // rectification target not found in left, right and RGB images
#define DC_ERROR_LEFT_RIGHT_BAD_CALIBRATION                  1019   // The left and right cameras have bad calibration, cannot do UV mapping
#define DC_ERROR_RECT_TOO_EARLY                              1020   // The frame timestamp is too close to the previous processed frame timestamp

#define DC_ERROR_CUSTOM_INVALID_CAL_TABLE                    2000    //	custom calibration - invalid calibration table
#define DC_ERROR_CUSTOM_INVALID_LEFTRIGHT_RESOLUTION         2001    //	custom calibration - left and right camera resolution is not supported
#define DC_ERROR_CUSTOM_LEFT_INTRINSICS_UNREASONABLE         2002    // custom calibration - left camera intrinsics unreasonable
#define DC_ERROR_CUSTOM_RIGHT_INTRINSICS_UNREASONABLE        2003    // custom calibration - right camera intrinsics unreasonable
#define DC_ERROR_CUSTOM_INVALID_PARAMS                       2004    // custom calibration - one or more of the output variables not valid

#define DC_ERROR_FW_VERSION_OLD                              3100    // outdated firmware
#define DC_ERROR_TIME_OUT                                    3101    // session timed out
#define DC_ERROR_DEVICE_TIMEOUT                              3102    // device timeout
#define DC_ERROR_INCORRECT_OPTION_VALUE                      3103    // invalid option
#define DC_ERROR_CAMERA_NOT_PLUGGED                          3104    // device not plugged in
#define DC_ERROR_GIMBAL_NOT_START                            3105    // gimbal not started


#define DC_ERROR_EXCEPTION                                   9001    // exception
#define DC_ERROR_DEVICE_INVALID                              9002    // device is null, invalid
#define DC_ERROR_DEVICE_USB2                                 9003    // device is usb2, not supported

#define DC_ERROR_PREMATURE                                   9800    // basic requirement not satisfied, too early to call

#define DC_ERROR_RESOLUTION_NOT_SUPPORTED_V2                 9900    // version 2.0 coefficient table does not support 1280x800 resolution mode
#define DC_ERROR_TABLE_NOT_SUPPORTED                         9901    // calibration coefficient tablet version not supported
#define DC_ERROR_TABLE_NOT_VALID_RESOLUTION                  9902    // image width and height in calibration table is not valid.
#define DC_ERROR_TABLE_NOT_VALID_COEFF                       9903    // coefficient calibration table (0x19) not valid or corrupted
#define DC_ERROR_TABLE_NOT_VALID_DEPTH                       9904    // depth calibration table (0x1f) not valid or corrupted
#define DC_ERROR_TABLE_NOT_VALID_RGB                         9905    // rgb calibration table (0x20) not valid or corrupted
#define DC_ERROR_TABLE_READ_FAILED_COEFF                     9906    // coefficient calibration table (0x19) read from device failed
#define DC_ERROR_TABLE_READ_FAILED_DEPTH                     9907    // depth calibration table (0x1f) read from device failed
#define DC_ERROR_TABLE_READ_FAILED_RGB                       9908    // rgb calibration table (0x20) read from device failed
#define DC_ERROR_TABLE_WRITE_FAILED                          9909    // calibration table failed to write to device

#define DC_ERROR_RGB_NOT_SUPPORTED_ON_DEVICE                 9950    // device does not support rgb
#define DC_ERROR_SET_INTERMEDIATE_CALIB_TABLE                9951    // set intermediate calibration data failed

#define DC_ERROR_SET_STREAMING_MEDIA_MODE_FAILED             9986    // streaming profile not supported
#define DC_ERROR_INVALID_RGB_CALIBRATION_RESOLUTION          9987    // rgb calibration resolution width or height zero or not valid
#define DC_ERROR_MISMATCH_VISION_DATA_SIZE                   9988    // Vision calibration data should be either MIN_VISION_DATA_SIZE or MAX_VISION_DATA_SIZE in size
#define DC_ERROR_MISMATCH_CAL_TABLE_CRC                      9989    // The CRC field in calibration table does not match expected value from its content
#define DC_ERROR_MISMATCH_CAL_TABLE_SIZE                     9990    // The size field in calibration table provided does not match expected value
#define DC_ERROR_INVALID_CAL_TABLE_TYPE                      9991    // Invalid calibration table type
#define DC_ERROR_INVALID_BUFFER                              9992    // Invalid or NULL pointer to buffer provided
#define DC_ERROR_INVALID_CAL_SETTINGS                        9993    // Invalid calibration settings - currently only valid setting is CalibrationSettings::CAL_SETTINGS_GOLD
#define DC_ERROR_INVALID_PARAMETER                           9994    // Invalid arument passed in
#define DC_ERROR_NOT_APPLICABLE                              9995    // Feature or data not applicable to the current calibration flow or mode
#define DC_ERROR_NOT_IMPLEMENTED                             9996    // Interface or feature not implemented or not applicable
#define DC_ERROR_NOT_INITIALIZED                             9997    // dynamic calibration library not initialized
#define DC_ERROR_FAIL                                        9998    // generic error for failure where error code is not used
#define DC_ERROR_UNKNOWN                                     9999    // other errors for unknown reason


// calibration types target-less and targeted
// targeted consists of two phases - rectification and scale
enum DC_PHASE : int
{
    DC_TARGETLESS = -1,
    DC_TARGETED_RECTIFICATION_PHASE = 0,
    DC_TARGETED_SCALE_PHASE = 1
};

#endif //DS_SHARED_H_
