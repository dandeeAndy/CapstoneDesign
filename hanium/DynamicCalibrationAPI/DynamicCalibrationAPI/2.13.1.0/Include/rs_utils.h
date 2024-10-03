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

#ifndef _RSD400_UTILS_H_
#define _RSD400_UTILS_H_

#include <string>
#include <iostream>
#include <fstream>
#include <sstream>
#include <algorithm>

using namespace std;


string dump_buffer_to_console(uint8_t* buffer, uint32_t size);
string rs_convert_err_to_string(int errCode);

#if defined(_WIN32)
inline char char_tolower(char c) { return tolower(c); }
inline char char_toupper(char c) { return toupper(c); }
#else
inline char char_tolower(char c) { return std::tolower(c); }
inline char char_toupper(char c) { return std::toupper(c); }
#endif

inline std::string to_lower(std::string x)
{
    transform(x.begin(), x.end(), x.begin(), char_tolower);
    return x;
}

inline std::string to_upper(std::string x)
{
    transform(x.begin(), x.end(), x.begin(), char_toupper);
    return x;
}

inline bool ends_with(const std::string& s, const std::string& suffix)
{
	auto i = s.rbegin(), j = suffix.rbegin();
	for (; i != s.rend() && j != suffix.rend() && *i == *j;
		i++, j++);
	return j == suffix.rend();
}

inline bool starts_with(const std::string& s, const std::string& prefix)
{
	auto i = s.begin(), j = prefix.begin();
	for (; i != s.end() && j != prefix.end() && *i == *j;
		i++, j++);
	return j == prefix.end();
}

inline void dc_copy(void* dst, void const* src, size_t size)
{
    auto from = reinterpret_cast<uint8_t const*>(src);
    std::copy(from, from + size, reinterpret_cast<uint8_t*>(dst));
}

inline bool file_exist(const char *name)
{
    std::ifstream f(name);
    return f.good();
}
#endif


#if defined(_WIN32)

#define DS_MEMCPY_S(a, b, c, d) memcpy_s(a, b, c, d)
#define DS_MEMCPY(a, c, d) memcpy_s(a, d, c, d)

#define vsnprintf _vsnprintf
#define snprintf _snprintf
#undef min
#undef max

#elif defined(__ANDROID__)

static inline void* memcpy_s(void *dest, size_t size, const void *src, size_t count)
{
    size_t n = (size < count) ? size : count;
    return memcpy(dest, src, n);
}

#define DS_MAX_PATH 4096
#define DS_SPRINTF snprintf
#define DS_PRINTF printf
#define DS_STRCPY(a, b, c) strlcpy(a, c, b)
#define DS_STRNCPY(a, b, c, d) strlcpy(a, c, d)
#define DS_STRCAT(a, b, c) strlcat(a, c, b)
#define DS_MEMMOVE(a, b, c, d) memmove(a, c, d)
#define DS_MEMCPY_S(a, b, c, d) memcpy_s(a ,b , c, d)
#define DS_MEMCPY(a, c, d) memcpy_s(a, d, c, d)

#define DS_STRCPY_X(a, b, c) strlcpy(a, b, c)
#define DS_STRNLEN_S(s, n) strnlen(s, n)

#else // !(WIN32 || ANDROID)
#define DS_MEMCPY_S(a, b, c, d) dc_copy(a, c, d)
#define DS_MEMCPY(a, c, d) dc_copy(a, c, d)

#endif

