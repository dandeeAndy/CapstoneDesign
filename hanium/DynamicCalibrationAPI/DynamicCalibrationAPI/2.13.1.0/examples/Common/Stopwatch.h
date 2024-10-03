/*
**********************************************************************************************************
*                                                                                                       **
* INTEL CONFIDENTIAL                                                                                    **
* Copyright (2018 - 2020) Intel Corporation.                                                            **
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

#include <string>
#include <chrono>
#include <thread>

class Stopwatch
{
    using clock = std::chrono::high_resolution_clock;
    using milliseconds = std::chrono::milliseconds;
    using seconds = std::chrono::seconds;

    clock::time_point start_;

private:
    milliseconds intervalMs(const clock::time_point& t1, const clock::time_point& t0)
    {
        return std::chrono::duration_cast<milliseconds>(t1 - t0);
    }

    seconds intervalSeconds(const clock::time_point& t1, const clock::time_point& t0)
    {
        return std::chrono::duration_cast<seconds>(t1 - t0);
    }

    clock::time_point now()
    {
        return clock::now();
    }

public:
    Stopwatch() : start_(clock::now()) {}

    void Start()
    {
        start_ = clock::now();
    }

    clock::time_point Restart()
    {
        start_ = clock::now();
        return start_;
    }

    double ElapsedMilliseconds()
    {
        return 1.0 * intervalMs(now(), start_).count();
    }

    double ElapsedSeconds()
    {
        return 1.0 * intervalSeconds(now(), start_).count();
    }
};
