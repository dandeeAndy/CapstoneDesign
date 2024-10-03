Summary
-------
  This folder contains usage examples for Dynamic Calibration API and IMU Custom Calibration R/W API.

  For details, please refer to the following document
    Intel® RealSense™ Depth Module D400 Series Software Calibration Tool Programmer's Guide
available at Intel® RealSense™ product website
    https://downloadcenter.intel.com/download/27955/Intel-RealSense-D400-Series-Calibration-Tools-and-API

Description
------------
  1) DynamicCalibrator
     Contains sources for the Intel.Realsense.DynamicCalibrator tool. This example demonstrate
     depth/RGB calibration D400 series devices through Dynamic Calibration API.

  2) CustomRW
     Contains sources for the Intel.Realsense.CustomRW tool. This example demonstrate the various
     interfaces for custom calibration data read and write, including depth/RGB, fisheye, and IMU.

  3) simple-rw
     Contains sources for a simple example to demonstrate Custom Calibration R/W API.

  4) simple-fe
     Contains sources for a simple example to demonstrate Fisheye custom calibration data read and write.

  5) CustomCalibration
     Contains sources for a working example for calibrating depth/RGB with user custom algorithms.
     For details, please refer to the white paper:
       Intel® RealSense™ Depth Module D400 Series Custom Calibration
   which is available on Intel® RealSense™ product website:
       https://www.intel.com/content/www/us/en/support/articles/000026725/emerging-technologies/intel-realsense-technology.html

  6) Common
     Common headers and sources shared in the examples

  7) ThirdParty
     3rd party libraries and tools used in the examples

Compilation
-----------
  The examples can be compiled with VisualStudio 2015 Update 3 on Windows and gcc 5.4.0 on Linux

  On Linux:
    cd /usr/share/doc/librscalibrationapi/examples
    sudo mkdir build
    cd build
    sudo cmake ..
    sudo make

Dependencies
------------
  The DSDynamicCalibrationAPI and rs2-crw-mm libraries have librealsense and OpenCV statically linked, so the libraries
  do have not have dynamic dependency on them. However, the examples will require a few dependencies to be compiled successfully:

  1) librealsense
     the examples require librealsense library
     on Intel platforms (Ubuntu 16.04 and Ubuntu 18.04), librealsense2-dev prebuilt package is available, see link below
     https://github.com/IntelRealSense/librealsense/blob/master/doc/distribution_linux.md
     sudo apt-get install librealsense2-dev

     on ARM  platforms (Ubuntu 16.04 and Ubuntu 18.04), no prebuilt librealsense package is available, please download
     librealsense source code and build locally, and then point LIBRS_LIBRARY_DIR and LIBRS_INCLUDE_DIR to your local
     folders where librealsense library and header files are located, for example,
     sudo cmake .. -DLIBRS_LIBRARY_DIR=~/Downloads/librealsense-2.23.0/build -DLIBRS_INCLUDE_DIR=~/Downloads/librealsense-2.23.0/include

  2) libusb-1.0
     sudo apt-get install libusb-dev libusb-1.0-0-dev

  3) libglfw, freeglut, and libpng
     DynamicCalibrator is an example with graphical interfaces, so it requires a few more graphics related libraries.
     sudo apt-get install libglfw3 libglfw3-dev
     sudo apt-get install freeglut3 freeglut3-dev

     Install libpng on Ubuntu 16.04
     sudo apt-get install libpng12-dev

     Install libpng on Ubuntu 18.04
     sudo apt-get install libpng-dev

