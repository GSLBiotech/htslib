#ifndef MSVC_H
#define MSVC_H

#include <BaseTsd.h>
typedef SSIZE_T ssize_t;
typedef SIZE_T size_t;

#define _USE_MATH_DEFINES // M_SQRT2, M_PI

#define STDIN_FILENO  _fileno(stdin)
#define STDOUT_FILENO _fileno(stdout)
#define STDERR_FILENO _fileno(stderr)

#include <io.h>

#define R_OK 4 /* Test for read permission.  */
#define W_OK 2 /* Test for write permission.  */
#define F_OK 0 /* Test for existence.  */

#define access      _access
#define strcasecmp  _stricmp
#define strncasecmp _strnicmp
#define strtok_r    strtok_s

#ifndef PATH_MAX
#define PATH_MAX _MAX_PATH
#endif

#ifndef S_ISDIR
  #define S_ISDIR(mode) (((mode) & S_IFMT) == S_IFDIR)
#endif

#ifndef S_ISREG
  #define S_ISREG(mode)  (((mode) & S_IFMT) == S_IFREG)
#endif

#include <winsock2.h>  //struct timeval

#define usleep Sleep

#ifndef SSIZE_MAX /* SSIZE_MAX is POSIX 1 */
  #define SSIZE_MAX LONG_MAX
#endif

#endif //MSVC_H
