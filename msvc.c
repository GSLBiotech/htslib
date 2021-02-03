#ifdef _MSC_VER

#include "htslib/hts_msvc.h"

#define WIN32_LEAN_AND_MEAN
#include <Windows.h>
#include <stdint.h> // uint64_t
#include <winsock2.h>  //struct timeval

int gettimeofday(struct timeval * tp, struct timezone * tzp)
{
    // This is the number of 100 nanosecond intervals since January 1, 1601 (UTC) until 00:00:00 January 1, 1970.
    static const uint64_t EPOCH = ((uint64_t) 116444736000000000ULL);

    SYSTEMTIME  system_time;
    FILETIME    file_time;
    uint64_t    time;

    GetSystemTime( &system_time );
    SystemTimeToFileTime( &system_time, &file_time );
    time =  ((uint64_t)file_time.dwLowDateTime )      ;
    time += ((uint64_t)file_time.dwHighDateTime) << 32;

    tp->tv_sec  = (long) ((time - EPOCH) / 10000000L);
    tp->tv_usec = (long) (system_time.wMilliseconds * 1000);
    return 0;
}
#endif
