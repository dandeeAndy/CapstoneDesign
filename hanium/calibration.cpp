#include <librealsense2/rs.hpp>
#include <iostream>

int main() try
{
    // Create a Pipeline - this serves as a top-level API for streaming and processing frames
    rs2::pipeline pipe;

    // Configure and start the pipeline
    rs2::config cfg;
    cfg.enable_stream(RS2_STREAM_DEPTH, 640, 480, RS2_FORMAT_Z16, 30);
    cfg.enable_stream(RS2_STREAM_COLOR, 640, 480, RS2_FORMAT_RGB8, 30);
    pipe.start(cfg);

    // Get the stream profile and extract the intrinsics
    auto depth_stream = pipe.get_active_profile().get_stream(RS2_STREAM_DEPTH).as<rs2::video_stream_profile>();
    auto color_stream = pipe.get_active_profile().get_stream(RS2_STREAM_COLOR).as<rs2::video_stream_profile>();

    rs2_intrinsics depth_intrinsics = depth_stream.get_intrinsics();
    rs2_intrinsics color_intrinsics = color_stream.get_intrinsics();

    // Print depth camera intrinsics
    std::cout << "Depth camera intrinsics:" << std::endl;
    std::cout << "Focal Length: " << depth_intrinsics.fx << ", " << depth_intrinsics.fy << std::endl;
    std::cout << "Principal Point: " << depth_intrinsics.ppx << ", " << depth_intrinsics.ppy << std::endl;
    std::cout << "Distortion Model: " << depth_intrinsics.model << std::endl;
    std::cout << "Distortion Coefficients: ";
    for(int i = 0; i < 5; i++)
        std::cout << depth_intrinsics.coeffs[i] << " ";
    std::cout << std::endl << std::endl;

    // Print color camera intrinsics
    std::cout << "Color camera intrinsics:" << std::endl;
    std::cout << "Focal Length: " << color_intrinsics.fx << ", " << color_intrinsics.fy << std::endl;
    std::cout << "Principal Point: " << color_intrinsics.ppx << ", " << color_intrinsics.ppy << std::endl;
    std::cout << "Distortion Model: " << color_intrinsics.model << std::endl;
    std::cout << "Distortion Coefficients: ";
    for(int i = 0; i < 5; i++)
        std::cout << color_intrinsics.coeffs[i] << " ";
    std::cout << std::endl;

    return EXIT_SUCCESS;
}
catch (const rs2::error & e)
{
    std::cerr << "RealSense error calling " << e.get_failed_function() << "(" << e.get_failed_args() << "):\n    " << e.what() << std::endl;
    return EXIT_FAILURE;
}
catch (const std::exception& e)
{
    std::cerr << e.what() << std::endl;
    return EXIT_FAILURE;
}