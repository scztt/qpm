"""
Cross-platform way to set a file descriptor as non-blocking
Original code by anatoly technotik:
    https://stackoverflow.com/questions/34504970/non-blocking-read-on-os-pipe-on-windows
"""
import sys

if sys.platform != 'win32':
    import fcntl
    import os

    def set_fd_non_block_unix(fd):
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
else:
    import msvcrt
    from ctypes import windll, byref, wintypes, WinError
    from ctypes.wintypes import HANDLE, DWORD, POINTER, BOOL

    LPDWORD = POINTER(DWORD)
    PIPE_NOWAIT = wintypes.DWORD(0x00000001)

    def set_fd_non_block_win(fd):
        SetNamedPipeHandleState = windll.kernel32.SetNamedPipeHandleState
        SetNamedPipeHandleState.argtypes = [HANDLE, LPDWORD, LPDWORD, LPDWORD]
        SetNamedPipeHandleState.restype = BOOL

        h = msvcrt.get_osfhandle(fd)

        res = windll.kernel32.SetNamedPipeHandleState(h, byref(PIPE_NOWAIT), None, None)
        if res == 0:
            print(WinError())
            return False
        return True


if sys.platform != 'win32':
    def set_fd_non_block(fd):
        set_fd_non_block_unix(fd)
else:
    def set_fd_non_block(fd):
        set_fd_non_block_win(fd)
