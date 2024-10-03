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

#ifndef DS_DYNAMIC_CALIBRATION_H_
#define DS_DYNAMIC_CALIBRATION_H_

#define DS_DYNAMIC_CALIBRATION_VERSION "2.13.1.0"

#define __D400_USE_LIBREALSENSE__

#include <cstdint>
#include "DSShared.h"
#include "DSCalData.h"

#ifdef DSDYNCAL_EXPORTS
#if defined(_WIN32) || defined(__WIN32__)
#define DSDYNCAL_API __declspec(dllexport)
#else
#if defined(__GNUC__) && defined(GCC_HASCLASSVISIBILITY)
#define DSDYNCAL_API __attribute__((visibility("default")))
#else
#define DSDYNCAL_API
#endif
#endif
#else
#if defined(_WIN32) || defined(__WIN32__)
#if defined(WIN_UWP)
#define DSDYNCAL_API
#else
#define DSDYNCAL_API __declspec(dllimport)
#endif
#else
#define DSDYNCAL_API
#endif
#endif

namespace DynamicCalibrationAPI
{
    const int PHONELOC_DIM = 8;
    const int SCALE_INIT_SKIP = 3;

    // number of target images required for scale and rgb calibrations
    // general cases
    const int MAX_NUM_TARGET_IMAGES = 15;

    // in cases where device movement is limited, for example, device installed on a robot which cannot move vertically
    // when device is mounted with its baseline direction perpendicular to the stripes of the target, for example, device mounted horizontally and target is placed vertically
	const int MAX_NUM_TARGET_IMAGES_ROBOT_UNALIGNED = 8;

    // when device is mounted with its baseline direction aligned with the stripes of the target, for example, device mounted vertically and target is placed also vertically
	const int MAX_NUM_TARGET_IMAGES_ROBOT_ALIGNED = 6;

	typedef struct DC_Intrinsics
	{
		int           width;     // width in pixels
		int           height;    // height in pixels
		float         ppx;       // principal point horizontal coordinate (pixel offset from the left edge of the image)
		float         ppy;       // principal point vertical coordinate (pixel offset from the top edge of the image)
		float         fx;        // focal length (multiple of pixel width)
		float         fy;        // focal length (multiple of pixel height)
		int           model;     // distortion model
		float         coeffs[5]; // distortion coefficients, for Brown-Conrady: [k1, k2, p1, p2, k3].
	} DC_Intrinsics;

    /** Dynamic calibration root class. Contains all methods needed to run the dynamic calibration */
    class DSDYNCAL_API DSDynamicCalibration
    {
    public:
		/** Calibration Modes */
		enum CalibrationMode
		{
			/** Intel target-less calibration (target-less depth rectification only)*/
			CAL_MODE_INTEL_TARGETLESS = 0,
			/** Intel targeted calibration (targeted depth rectification and targeted depth scale)*/
			CAL_MODE_INTEL_TARGETED = 1,
			/** Intel targeted depth scale calibration only */
			CAL_MODE_INTEL_TARGETED_SCALE_ONLY = 3,
			/** Intel targeted RGB calibration */
			CAL_MODE_INTEL_RGB_CALIB = 4,
			/** User custom algorithm */
			CAL_MODE_USER_CUSTOM = 99
		};

		/** Calibration Settings */
		enum CalibrationSettings
		{
			/** gold settings */
			CAL_SETTINGS_GOLD = 0
		};

        /** Calibration Tables in Intel proprietary internal formats */
        enum CalibrationTableType
        {
            CAL_TABLE_COEFF =   0x19,        // coefficient table, DC_CALIB_COEFF_TABLE_SIZE bytes
            CAL_TABLE_DEPTH =   0x1F,        // depth table, DC_CALIB_DEPTH_TABLE_SIZE bytes
            CAL_TABLE_RGB =     0x20,        // rgb table (only available on devices with rgb, for example, d415, d435, and d435i), DC_CALIB_RGB_TABLE_SIZE bytes
            CAL_TABLE_ALL =     0xFF         // not actual table but a lump of all above tables in Vision Calibration Data in the order 
											 //     coefficient table (0x19) DC_CALIB_COEFF_TABLE_SIZE bytes
											 //     depth table (0x1F)       DC_CALIB_DEPTH_TABLE_SIZE bytes
											 //     rgb table (0x20)         DC_CALIB_RGB_TABLE_SIZE bytes (only applies for devices with rgb)
											 // since coeffcient table and depth table are required on every D400 devices, so the Vision Calibration Data size
                                             // is either (DC_CALIB_COEFF_TABLE_SIZE + DC_CALIB_DEPTH_TABLE_SIZE) bytes for devices without RGB or
                                             // (DC_CALIB_COEFF_TABLE_SIZE + DC_CALIB_DEPTH_TABLE_SIZE + DC_CALIB_RGB_TABLE_SIZE) bytes for devices with RGB
        };


        /** Grid level enumeration quantifies the amount of the features in each cell of the grid */
        enum GridLevel
        {
            /** Low amount of features in the cell */
            GRID_LEVEL_LOW = 0,
            /** Medium amount of features in the cell */
            GRID_LEVEL_MEDIUM = 1,
            /** High amount of features in the cell */
            GRID_LEVEL_HIGH = 2,
            /** Very High amount of features in the cell */
            GRID_LEVEL_VERY_HIGH = 3,
            GRID_LEVEL_NOT_TRACKED = 255
        };

        /** Grid fill enumeration quantifies how the cells are filled with features in the next frame */
        enum GridFill
        {
            /** Normal - features are subject to aging if they are in the buffer for too long */
            GRID_FILL_NORMAL = 0,
            /** Add only - will retain any existing features but keeps adding new features until the buffer is full */
            GRID_FILL_ADD_ONLY = 1,
            /** Cell full - will retain any existing features and not add any new features and the feature detection isn't run in the cell */
            GRID_FILL_CELL_FULL = 2
        };

        /** Grid features enumeration quantifies the amount of the features in the last frame */
        enum GridFeatures
        {
            /** Level 0 - no to little amount features */
            GRID_FEATURES_L0 = 0,
            /** Level 1 - moderate amount of features */
            GRID_FEATURES_L1 = 1,
            /** Level 2 - good amount of features */
            GRID_FEATURES_L2 = 2
        };

        /** Constructor */
        DSDynamicCalibration();
        /** Destructor */
        virtual ~DSDynamicCalibration();

        /** Initialize dynamic calibrator. It needs to be called at the very begin of the process. It supports use cases both with and without a live D400 device:
         *  a) use cases with a live d400 device, for example, calibrating the device, target-less or targeted, with live captured images, read/write calibration data
         *     on the device, or write user custom calibration parameters directly into the d400 device. In such cases, a librealsense rs2::device handle is required
         *     to pass into the interface during initialization.
         *  b) use cases without a live d400 device, for example, convert user custom calibration parameters into d400 compatible binary calibration format or reverse
         *     conversion from any d400 calibration binary file into user readable high level calibration parameters. In this case, no device handle is required since
         *     there is no physical device interaction. Pass in a NULL pointer as a device handle.
         * 
         *  For target-less calibration with a live device,
		 *  1280x720 resolution is supported for all devices, and additional native resolution 1280x800 is supported for modules
		 *  with wide angle lens, for example, D420, D430, D435, and D435i devices.
		 *    for example,
		 *    rs2::device *rs400dev = ...
		 *    Initialize(rs400dev, DynamicCalibrationAPI::DSDynamicCalibration::CAL_MODE_INTEL_TARGETED);
         *
         *  
         *  For targeted calibration with a live device,
         *  1280x720 resolution is
		 *  supported across all devices except F400. On F400 devices, 720x720 resolution should be used.
		 *  The function will throw a runtime error if the resolution is different or the calibration parameters are not valid.
         *
         *    for example,
         *    rs2::device *rs400dev = ...
         *    Initialize(rs400dev, DynamicCalibrationAPI::DSDynamicCalibration::CAL_MODE_INTEL_TARGETLESS);
         *
         *  For user custom calibration with a live device, for example, read/write calibration parameters on the device,
         *    Pass in a librealsense rs2::device pointer as device handle and set mode to CAL_MODE_USER_CUSTOM
         *    for example,
         *    rs2::device *rs400dev = ...
         *    Initialize(rs400dev, DynamicCalibrationAPI::DSDynamicCalibration::CAL_MODE_USER_CUSTOM);
         *
         *  For non-device involved use cases (calibration data conversion)
         *    Pass in a NULL pointer as device handle and set mode to CAL_MODE_USER_CUSTOM
         *    for example,
         *    Initialize(NULL, DynamicCalibrationAPI::DSDynamicCalibration::CAL_MODE_USER_CUSTOM);
		 *
		 *  @param rs400Dev: opaque device handle, currently only librealsense rs2::device handle is supported on both Windows and Linux. For use cases where no physical
         *                   device is involved, Pass in a NULL pointer as a device handle.
         *  @param mode: any of the operating modes defined in CalibrationMode.
		 *  @param width: The width of the images that will be used for dynamic calibration
		 *  @param height: The height of the images that will be used for dynamic calibration
		 *  @param active: true for laser projector is active, false for not active
         *  @param coeffTable: pointer to coefficient calibration table (table id 0x19)
         *  @param depthTable: pointer to depth calibration table (table id 0x1F)
         *  @param rgbTable: pointer to rgb calibration table (table id 0x20)
         *
		 *  @return: returns DC_SUCCESS if no issue, error code otherwise:
         *      DC_ERROR_INVALID_PARAMETER - invalid parameter passed in
         *      DC_ERROR_RESOLUTION_NOT_SUPPORTED_V2 -  if 1280x800 resolution is requested for devices with old version 2 coefficient table, this is not supported
         *      DC_ERROR_TABLE_NOT_SUPPORTED - calibration coefficient table on device is not supported
         *      DC_ERROR_TABLE_NOT_VALID_RESOLUTION – calibration table resolution width or height not valid
         */
        int Initialize(void *rs400Dev, CalibrationMode mode = CAL_MODE_INTEL_TARGETLESS, int width = 1280, int height = 720, bool active = false, DS5CoefficientsParamsTable* coeffTable = NULL, DS5DepthCalibrationParamsTable* depthTable = NULL, DS5RgbCalibrationParamsTable* rgbTable = NULL);

	    /** Initialize RGB calibrator. It needs to be called after scale (targeted) calibration is completed, only 1280x720 resolution is
		 *  supported across all devices. The function will throw a runtime error if the resolution is different or the calibration
		 *  parameters are not valid.
		 *
         *  @param rs400Dev: opaque device handle, currently only librealsense handle is supported on both Windows and Linux
         *  @param width: The width of the images that will be used for dynamic calibration
         *  @param height: The height of the images that will be used for dynamic calibration
         *  @param width_rgb: The width of the color images that will be used for dynamic calibration
         *  @param height_rgb: The height of the color images that will be used for dynamic calibration
         *  @return: returns DC_SUCCESS if no issue, error code otherwise:
         *      DC_ERROR_INVALID_PARAMETER - invalid parameter passed in
         *      DC_ERROR_RESOLUTION_NOT_SUPPORTED_V2 -  if 1280x800 resolution is requested for devices with old version 2 coefficient table, this is not supported
         *      DC_ERROR_TABLE_NOT_SUPPORTED - calibration coefficient table on device is not supported
         *      DC_ERROR_TABLE_NOT_VALID_RESOLUTION - calibration table resolution width or height not valid
         */
         int InitializeRgbCalibrator(void *rs400Dev, int width = 1280, int height = 720, int width_rgb = 1280, int height_rgb = 720);

        /** Add a pair of left and right images to dynamic calibrator. The images must have
         *  the width and height as specified during initialization and must be in 8-bit
         *  grayscale format. In addition it is recommended to use 30 FPS.
         *
         *  @param leftImage: Pointer to captured left image buffer in byte format
         *  @param rightImage: Pointer to captured right image buffer in byte format
         *  @param depthImage: Pointer to captured depth image buffer in byte format
         *  @param timestamp: timestamp on the image pair in milliseconds
         *  @return:
         *      Target-less calibration:
         *          DC_SUCCESS if image added ok, otherwise returns error code.
         *          DC_ERROR_RECT_INVALID_IMAGES
         *          DC_ERROR_RECT_INVALID_GRID_FILL
         *          DC_ERROR_RECT_TOO_SIMILAR
         *          DC_ERROR_RECT_TOO_MUCH_FEATURES
         *          DC_ERROR_RECT_NO_FEATURES
         *          DC_ERROR_RECT_GRID_FULL
         *          DC_ERROR_UNKNOWN
         *      Targeted Calibration:
         *          DC_SUCCESS if image added ok, otherwise returns error code
         *          DC_ERROR_RECT_INVALID_IMAGES
         *          DC_ERROR_RECT_TOO_SIMILAR
         *          DC_ERROR_RECT_TARGET_NOT_FOUND_LEFT
         *          DC_ERROR_RECT_TARGET_NOT_FOUND_RIGHT
         *          DC_ERROR_RECT_TARGET_NOT_FOUND_BOTH
         *          DC_ERROR_SCALE_DEPTH_NOT_CONSISTENT
         *          DC_ERROR_TARGET_UNSTABLE
         *          DC_ERROR_TARGET_TOO_CLOSE
         *          DC_ERROR_TARGET_TOO_FAR
         *          DC_ERROR_SCALE_ALREADY_CAPTURED
         *          DC_ERROR_SCALE_DEPTH_TOO_SPARSE
         *          DC_ERROR_SCALE_DEPTH_NOT_A_PLANE
         *          DC_ERROR_SCALE_TARGET_TILT_ANGLE_BIG
         *          DC_ERROR_SCALE_FAILED_COMPUTE
         *          DC_ERROR_PHASE_COMPLETED
         *          DC_ERROR_UNKNOWN
         */
        int AddImages(const uint8_t * leftImage, const uint8_t * rightImage, const uint16_t * dcImage, const uint64_t timeStamp);

        /** Get last position of target (printed or phone) in left image
         *  position is defined by a quadrilateral plane boundary with four corner points
         *  @param ptr four corner points surrounding the target in the order
         *         top left corner x and y
         *         top right corner x and y
         *         bottom right corner x and y
         *         bottom left corner x and y
         *  @return error code indicate target location status
		 *      DC_SUCCESS if success
		 *      DC_ERROR_NOT_IMPLEMENTED if called in target-less mode
		 *      DC_ERROR_RECT_TARGET_NOT_FOUND_LEFT
         */
        int GetLastPhoneROILeftCamera(float ptr[PHONELOC_DIM]);

        /** Get last position of target (printed or phone) in right image
         *  position is defined by a quadrilateral plane boundary with four corner points
         *  @param ptr four corner points surrounding the target in the order
         *         top left corner x and y
         *         top right corner x and y
         *         bottom right corner x and y
         *         bottom left corner x and y
         *  @return error code indicate target location status
		 *      DC_SUCCESS if success
         *      DC_ERROR_NOT_IMPLEMENTED if called in target-less mode
         *      DC_ERROR_RECT_TARGET_NOT_FOUND_RIGHT
         */
        int GetLastPhoneROIRightCamera(float ptr[PHONELOC_DIM]);

		/** Get last position of target (printed or phone) in color image
		*  position is defined by a quadrilateral plane boundary with four corner points
		*  @param ptr four corner points surrounding the target in the order
		*         top left corner x and y
		*         top right corner x and y
		*         bottom right corner x and y
		*         bottom left corner x and y
		*  @return error code indicate target location status
		*      DC_SUCCESS if success
		*      DC_ERROR_NOT_IMPLEMENTED if called in target-less mode
		*      DC_ERROR_RECT_TARGET_NOT_FOUND_LEFT
		*/
		int GetLastPhoneROIRGBCamera(float ptr[PHONELOC_DIM]);

        /** get target distance during scale phase in targeted calibration
          * the last distance of the target/phone from camera. The distance is returned in millimeters
          * but generally can be considered as inaccurate as the updated calibration isn't ready by this time.
          * This function returns value only in the scale phase of the process.
          *  @return distance of the phone target in mm or -1.0 if the phone wasn't detected yet or
          *          not in scale phase of the process.
          */
        float GetLastTargetDistance();

        /** Returns the pointer you can use to access grid fill settings. You will want to update the grid
         *  after you add a new image to reflect grid level updates. You only need to call this function once at the beginning
         *  and then just use the pointer it returns.
         *
         *  @param grid: Returns a pointer to the grid array, which size is gridWidth * gridHeight, row major
         *  @param gridWidth: Returns width of the grid
         *  @param gridHeight: Returns height of the grid
         */
        void AccessGridFill(GridFill *& grid, int & gridWidth, int & gridHeight);

        /** Returns the current status of feature detection in the grid. The grid will update
         *  when you add a new image even if it is rejected. Please note that any cell set to DSDynamicCalibration::GRID_FILL_CELL_FULL
         *  will cause the algorithm not to run feature detection in the cell and thus will always report zero features regardless of the image.
         *  You only need to call this function once at the beginning and then just use the pointer it returns.
         *
         *  @param grid: Returns a pointer to the grid array, which size is gridWidth * gridHeight, row major
         *  @param gridWidth: Returns width of the grid
         *  @param gridHeight: Returns height of the grid
         */
        void GetLastFrameFeaturesGrid(const GridFeatures *& grid, int & gridWidth, int & gridHeight);

        /** Returns the current status of feature detection in the grid. The grid will update
         *  when you add a new image (which is not rejected). You only need to call this function once at the beginning
         *  and then just use the pointer it returns.
         *
         *  @param grid: Returns a pointer to the grid array, which size is gridWidth * gridHeight, row major
         *  @param gridWidth: Returns width of the grid
         *  @param gridHeight: Returns height of the grid
         */
        void GetGridLevels(const GridLevel *& grid, int & gridWidth, int & gridHeight);

        /** Evaluates the grid levels and returns a score of how well it's filled. 0.0 means empty grid,
         *  1.0 means grid level is at least high for every cell.
         *
         *  @return: The score of the grid levels between 0.0 and 1.0
         */
        float GetGridLevelScore();

        /** Indicates whether the dynamic calibration is completed. Whether the grid is full of features, i.e. each cell
         *  is DSDynamicCalibration::GRID_LEVEL_HIGH.
         *  Once the grid is full you don't need to add more images and proceed with updating the calibration.
         *
         *  @return: Whether the grid is full.
         *           False: Dynamic calibrator is still working on calibration.
         *           True: Dynamic calibration is completed.
         */
        bool IsGridFull();

        /** (Target-less only) Whether the device is out of calibration.
         *  You should only use this function when DSDynamicCalibration::IsGridFull returns true
         *
         *  @param outOfCalibration: Returns whether is out of calibration or not
         *  @return: error code
                 *           DC_SUCCESS if the evaluation was successful
                 *           DC_ERROR_FAIL if the evaluation failed
                 *           DC_ERROR_PREMATURE if the evaluation was called too early
         */
        int IsOutOfCalibration(bool & outOfCalibration);


        /** check if rectification phase is completed
         * @return true if completed otherwise false
         */
        bool IsRectificationPhaseComplete();

        /** scale calibration only
         *  skip rectification phase and go directly to scale phase
         */
        bool SkipToScalePhase();

        /** switch to scale calibration phase
         */
        bool GoToScalePhase();

        /* Check if scale calibration phase is completed
         * @return true if completed otherwise false
         */
        bool IsScalePhaseComplete();

		/* Check if RGB calibration phase is completed
		* @return true if completed otherwise false
		*/
		bool IsCaptureComplete();

        /** get number of image pairs collected in the current calibration phase
         *  @return number of image pairs (left/right for target-less calibration and left/right/depth
         *          for targeted calibration
         */
        int NumOfImagesCollected();

        /** (targeted calibration only) set the intermediate calibration results once the rectification phase is complete
         *  @return DC_SUCCESS on success, error code on failure.
         *      DC_ERROR_NOT_APPLICABLE when called in target-less calibration
         *      DC_ERROR_FAIL if there is problem and failed
		 */
        int SetIntermediateRectificationCalibration();

       /** Set the updated calibration table.
        *  for target-less, you should only use this function when DSDynamicCalibration::IsGridFull returns true
        *  for targeted, only use this function after scale calibration is completed
        *
        *  @return: Whether the function was successful
        *      DC_SUCCESS on success
        *      DC_ERROR_FAIL on failure
        */
        int UpdateCalibrationTables();

        /** get current calibration phase
        *   @return DC_TARGETLESS for target-less calibration
        *           DC_TARGETED_RECTIFICATION_PHASE for rectification phase, DC_TARGETED_SCALE_PHASE for scale phase
        */
        DC_PHASE GetPhase();

        /** (Target-less only) Get the calibration error RMS (not normalized) from target-less calibration.
         *
         *  This function is not part of the official process and it is not guaranteed that calibration calculated when DSDynamicCalibration::IsGridFull
         *  returns false will meet the specification.
         *
         *  @param calibrationError: Returns the calibration error
         *  @return: return DC_SUCCESS for targetless calibration if the evaluation was successful. For targeted
                 *           it returns DC_ERROR_NOT_APPLICABLE since it's not available
         */
        int GetCalibrationError(float & calibrationError);


        /** (targeted calibration only) Returns the updated calibration in rotation modification around the x/y/z axes once the scale phase is complete.
         *  This API require the scale phase is completed.
         *
         *  @param rx Returns rotation modification around the x-axis
         *         ry Returns rotation modification around the y-axis
         *         rz Returns rotation modification around the z-axis
         *  @return true on success, false on failure.
         */
        bool GetTargetedCalibrationCorrection(double& rx, double& ry, double& rz);

		/** (RGB calibration only) Returns the updated calibration in rotation modification around the x/y/z axes once the scale phase is complete.
		*  This API require the scale phase is completed.
		*
		*  @param rx Returns rotation modification around the x-axis
		*         ry Returns rotation modification around the y-axis
		*         rz Returns rotation modification around the z-axis
		*         tx Returns translation modification along the x-axis
		*         ty Returns translation modification along the y-axis
		*         tz Returns translation modification along the z-axis
		*  @return true on success, false on failure.
		*/
		bool GetRGBCalibrationCorrection(double& rx, double& ry, double& rz, double& tx, double& ty, double& tz);

        /** Get version of dynamic calibration as a string
         *
         * @return: Version of Dynamic Calibration API
         */
        static const char * GetVersion();


        /** Creates calibration tables based on supplied parameters, which assumes that left camera is the reference camera and is located at world origin.
         *
         *  @param resolutionLeftRight: The resolution of the left and right camera, specified as [width; height]
         *  @param focalLengthLeft: The focal length of the left camera, specified as [fx; fy] in pixels
         *  @param principalPointLeft: The principal point of the left camera, specified as [px; py] in pixels
         *  @param distortionLeft: The distortion of the left camera, specified as Brown's distortion model [k1; k2; p1; p2; k3]
         *  @param focalLengthRight: The focal length of the right camera, specified as [fx; fy] in pixels
         *  @param principalPointRight: The principal point of the right camera, specified as [px; py] in pixels
         *  @param distortionRight: The distortion of the right camera, specified as Brown's distortion model [k1; k2; p1; p2; k3]
         *  @param rotationLeftRight: The rotation from the right camera coordinate system to the left camera coordinate system, specified as a 3x3 row-major rotation matrix
         *  @param translationLeftRight: The translation from the right camera coordinate system to the left camera coordinate system, specified as a 3x1 vector in milimeters
         *  @param hasRGB: Whether RGB camera calibration parameters are supplied
         *  @param resolutionRGB: The resolution of the RGB camera, specified as [width; height]
         *  @param focalLengthRGB: The focal length of the RGB camera, specified as [fx; fy] in pixels
         *  @param principalPointRGB: The principal point of the RGB camera, specified as [px; py] in pixels
         *  @param distortionRGB: The distortion of the RGB camera, specified as Brown's distortion model [k1; k2; p1; p2; k3]
         *  @param rotationLeftRGB: The rotation from the RGB camera coordinate system to the left camera coordinate system, specified as a 3x3 row-major rotation matrix
         *  @param translationLeftRGB: The translation from the RGB camera coordinate system to the left camera coordinate system, specified as a 3x1 vector in milimeters
         *  @return When DC_SUCCESS then the tables were created successfully, otherwise, returns error code
         *          DC_ERROR_CUSTOM_INVALID_CAL_TABLE  - one or more of the calibration tables are not valid
         *          DC_ERROR_CUSTOM_INVALID_LEFTRIGHT_RESOLUTION  - left and right camera resolution is not supported
         *          DC_ERROR_CUSTOM_LEFT_INTRINSICS_UNREASONABLE  - left camera intrinsics unreasonable
         *          DC_ERROR_CUSTOM_RIGHT_INTRINSICS_UNREASONABLE - right camera intrinsics unreasonable
         */
        int WriteCustomCalibrationParameters(const int resolutionLeftRight[2], const double focalLengthLeft[2], const double principalPointLeft[2],
			const double distortionLeft[5], const double focalLengthRight[2], const double principalPointRight[2], const double distortionRight[5], const double rotationRight[9], const double translationRight[3], const bool hasRGB, const int resolutionRGB[2],
			const double focalLengthRGB[2], const double principalPointRGB[2], const double distortionRGB[5], const double rotationRGB[9], const double translationRGB[3]);

		/** Parses calibration tables from device into ordinary calibraiton parameters
		*
		*  @param coeffsTable: The calibration coefficients table
		*  @param depthTable: The depth calibration table
		*  @param rgbTable: The RGB calibration table - this parameter is optional and may be NULL
		*  @param resolutionLeftRight: The resolution of the left and right camera, specified as [width; height]
		*  @param focalLengthLeft: The focal length of the left camera, specified as [fx; fy] in pixels
		*  @param principalPointLeft: The principal point of the left camera, specified as [px; py] in pixels
		*  @param distortionLeft: The distortion of the left camera, specified as Brown's distortion model [k1; k2; p1; p2; k3]
		*  @param focalLengthRight: The focal length of the right camera, specified as [fx; fy] in pixels
		*  @param principalPointRight: The principal point of the right camera, specified as [px; py] in pixels
		*  @param distortionRight: The distortion of the right camera, specified as Brown's distortion model [k1; k2; p1; p2; k3]
		*  @param rotationLeftRight: The rotation from the right camera coordinate system to the left camera coordinate system, specified as a 3x3 rotation matrix
		*  @param translationLeftRight: The translation from the right camera coordinate system to the left camera coordinate system, specified as a 3x1 vector in milimeters
		*  @param hasRGB: Whether RGB camera calibration parameters are supplied
		*  @param resolutionRGB: The resolution of the RGB camera, specified as [width; height]
		*  @param focalLengthRGB: The focal length of the RGB camera, specified as [fx; fy] in pixels
		*  @param principalPointRGB: The principal point of the RGB camera, specified as [px; py] in pixels
		*  @param distortionRGB: The distortion of the RGB camera, specified as Brown's distortion model [k1; k2; p1; p2; k3]
		*  @param rotationLeftRGB: The rotation from the RGB camera coordinate system to the left camera coordinate system, specified as a 3x3 rotation matrix
		*  @param translationLeftRGB: The translation from the RGB camera coordinate system to the left camera coordinate system, specified as a 3x1 vector in milimeters
		*  @return When DC_SUCCESS then the tables were parsed successfully, otherwise, returns error code
		*          DC_ERROR_CUSTOM_INVALID_CAL_TABLE  - one or more of the calibration tables are not valid
		*          DC_ERROR_CUSTOM_INVALID_PARAMS  - one or more of the output variables not valid
		*/
		int ReadCalibrationParameters(int resolutionLeftRight[2], double focalLengthLeft[2], double principalPointLeft[2],
			double distortionLeft[5], double focalLengthRight[2], double principalPointRight[2], double distortionRight[5], double rotationRight[9], double translationRight[3], bool& hasRGB, int resolutionRGB[2], double focalLengthRGB[2], double principalPointRGB[2],
			double distortionRGB[5], double rotationRGB[9], double translationRGB[3]);

		/** Reset active calibration data on device to desired settings
		 *  @param setting: currently only CalibrationSettings::CAL_SETTINGS_GOLD is valid, depends on the calibrations performed on the device,
		 *                  this setting came from either factory calibration or OEM calibration
		 *  @return When DC_SUCCESS then calibration is reset to the desired setting
		 *          DC_ERROR_INVALID_CAL_SETTINGS - invalid setting provided
		 *          DC_ERROR_FAIL - failed to restore to the desired setting
		 */
		int ResetDeviceCalibration(CalibrationSettings setting = CalibrationSettings::CAL_SETTINGS_GOLD);

		/** Power cycle device
		*  @return When DC_SUCCESS then device is power cycled successfully
		*          DC_ERROR_FAIL - failed to power cycle the device
		*/
		int PowerCycleDevice();

        /** Read calibration table raw data from device into buffer
        *  @param table: user allocated buffer in type dependent size of DC_CALIB_COEFF_TABLE_SIZE, DC_CALIB_DEPTH_TABLE_SIZE, or DC_CALIB_RGB_TABLE_SIZE
        *  @param tableType: calibration table type including CAL_TABLE_COEFF, CAL_TABLE_DEPTH, CAL_TABLE_RGB
        *  @return When DC_SUCCESS then raw data read successfully
        *          DC_ERROR_NOT_INITIALIZED - library not initialized
        *          DC_ERROR_INVALID_BUFFER - invalid buffer
        *          DC_ERROR_INVALID_CAL_TABLE_TYPE - unsupported table type
        *          DC_ERROR_FAIL - failed to read the raw data from the device
        */
        int ReadCalibrationRawData(uint8_t* table, CalibrationTableType tableType);

        /** Write calibration table raw data to device
        *  @param table: user allocated buffer in type dependent size of DC_CALIB_COEFF_TABLE_SIZE, DC_CALIB_DEPTH_TABLE_SIZE, or DC_CALIB_RGB_TABLE_SIZE.
        *                The table content usually is saved from a device or generated from other Intel RealSense tools.
        *  @param tableType: calibration table type including CAL_TABLE_COEFF, CAL_TABLE_DEPTH, CAL_TABLE_RGB
        *  @return When DC_SUCCESS then raw data write successfully
        *          DC_ERROR_NOT_INITIALIZED - library not initialized
        *          DC_ERROR_INVALID_BUFFER - invalid buffer
        *          DC_ERROR_INVALID_CAL_TABLE_TYPE - unsupported table type
        *          DC_ERROR_FAIL - failed to write the raw data to the device
        */
        int WriteCalibrationRawData(uint8_t* table, CalibrationTableType tableType);

        /** Read FE custom data from device into buffer
        *  @param buffer: user allocated buffer in size of DC_MM_FE_CUSTOM_DATA_SIZE
        *  @return When DC_SUCCESS then data read successfully
        *          DC_ERROR_NOT_INITIALIZED - library not initialized
        *          DC_ERROR_INVALID_BUFFER - invalid buffer
        *          DC_ERROR_FAIL - failed to read data from the device
        */
        int ReadFECustomData(uint8_t* buffer);

        /** Write FE custom data buffer to device
        *  @param buffer: user allocated buffer in size of DC_MM_FE_CUSTOM_DATA_SIZE that contains custom data to be written to device
        *  @return When DC_SUCCESS then data written uccessfully
        *          DC_ERROR_NOT_INITIALIZED - library not initialized
        *          DC_ERROR_INVALID_BUFFER - invalid buffer
        *          DC_ERROR_FAIL - failed to write data to device
        */
        int WriteFECustomData(uint8_t* buffer);

        /** Validate user provided calibration table data
        *  @param table: user allocated buffer contains calibration table data to be validated
        *  @return When DC_SUCCESS then data is valid
        *          DC_ERROR_INVALID_CAL_TABLE_TYPE - data does not match with expected calibration table type
        *          DC_ERROR_MISMATCH_CAL_TABLE_SIZE - data size does not match expected calibration table size
        *          DC_ERROR_MISMATCH_CAL_TABLE_CRC - data content does not match expected calibration table content
        *          DC_ERROR_INVALID_BUFFER - invalid buffer
        */
        int ValidateTable(uint8_t* table, uint32_t table_size);

        /** Validate user provided Vision Calibration Data
        *  @param pVision: user allocated buffer contains vision calibration data to be validated
        *  @return When DC_SUCCESS then data is valid
        *          DC_ERROR_INVALID_CAL_TABLE_TYPE - data does not match with expected calibration table type
        *          DC_ERROR_MISMATCH_CAL_TABLE_SIZE - data size does not match expected calibration table size
        *          DC_ERROR_MISMATCH_CAL_TABLE_CRC - data content does not match expected calibration table content
        *          DC_ERROR_INVALID_BUFFER - invalid buffer
        */
        int ValidateVisionCalibration(uint8_t* pVision, bool rgb);

        /** World to left and right rotation matrix
        *  @param rleft: 3x3 rotation matrix, World to left rotation matrix (inverse rotation of the left camera in rectified coordinate system)
        *  @param rright: 3x3 rotation matrix, World to right rotation matrix (inverse rotation of the right camera in rectified coordinate system)
        *  @return DC_SUCCESS
        */
        int ReadCalibration_World_Rotation(float rleft[9], float rright[9]);

        /** RGB intrinsic
        *  @param intr: rgb intrinsic at specified width and height. If width and height not specified or zero, the width and height of rgb calibration will be used.
        *  @param width: rgb resolution width
        *  @param height: rgb resolution height
        *  @return When DC_SUCCESS then data is valid
        *          DC_ERROR_INVALID_CAL_TABLE_TYPE - data does not match with expected calibration table type
        *          DC_ERROR_MISMATCH_CAL_TABLE_SIZE - data size does not match expected calibration table size
        */
        int ReadCalibration_RGB_Intrinsic(DC_Intrinsics &intr, uint32_t width = 0, uint32_t height = 0);

        /** RGB extrinsic in rectified coordinate system
        *  @param rotation: 3x3 rotation matrix
        *  @param translation: translation vector, in milli-meters
        */
        int ReadCalibration_RGB_Extrinsic_Rectified(float rotation[9], float translation[3]);

    public:
        // target stripe orientation ir aligned with device baseline direction
        bool m_target_aligned;

        // force targeted scale calibration and rgb calibration to capture more or less number of target images than default
        int m_numImages;

        // force target-less calibration to ignore the blocks on the borders of FOV
		bool m_ignore_borders;

        // log level 0 - none, 1 - debug
        int m_log_level;

    private:
        void *m_Rs400Device;
		CalibrationMode m_CalMode;
        GridLevel * m_GridLevels;
        GridFill * m_GridFill;
        GridFeatures * m_LastFrameFeaturesGrid;
        bool m_GridFull;

        void * m_InternalPtr;
        bool m_InternalVar1;

        int m_width;
        int m_height;

        int m_width_rgb;
        int m_height_rgb;

        bool m_targeted;
        uint64_t m_startTime;
        bool m_started;
        int m_scaleFrameProcessed;

        void* mRectCache;
        void* mRectSwitchCache;
        void* mScaleCache;
		void* mRGBCache;

		uint8_t* mCyImage;

        DS5CoefficientsParamsTable m_coefficientsTable;
        DS5DepthCalibrationParamsTable m_depthTable;
        DS5RgbCalibrationParamsTable m_rgbTable;

        DS5RgbCalibrationParamsTable* m_pRgbTable;

        bool m_force_rgb;

        bool CreateRectCache(DS5CoefficientsParamsTable* calibrationCoeffs, DS5DepthCalibrationParamsTable* depthCalibrationTable);
        bool CreateScaleCache();
		bool CreateRGBCache();
        int AddImagesHelper(const uint8_t * leftImage, const uint8_t * rightImage, const uint16_t * dcImage, const uint64_t timeStamp);

        bool HwMonitorCmd_Get(void* rs400Dev, uint8_t* cmd, uint8_t* data, int length);
        bool HwMonitorCmd_Set(void* rs400Dev, uint8_t* cmd, uint8_t* data, int length);

		void ReleaseResources();
    };
}

#endif //DS_DYNAMIC_CALIBRATION_H_
