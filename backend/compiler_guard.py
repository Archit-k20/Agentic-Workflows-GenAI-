"""Restrict compiler filesystem access to toolchain and its isolated source directory.

Landlock is unprivileged on supported Linux kernels. Generated programs are not
executed. This bounds access to other sessions; it is not a code security audit.
"""

import ctypes
import os
from pathlib import Path
import sys


def restrict(source):
    if sys.platform != "linux":
        raise RuntimeError(
            "isolated compiler verification is unavailable outside the Linux container"
        )
    libc = ctypes.CDLL(None, use_errno=True)
    abi = libc.syscall(444, 0, 0, 1)
    if abi < 1:
        raise RuntimeError(
            "isolated compiler verification is unavailable: kernel has no Landlock support"
        )

    class Ruleset(ctypes.Structure):
        _fields_ = [("handled_access_fs", ctypes.c_uint64)]

    class PathRule(ctypes.Structure):
        _pack_ = 1
        _fields_ = [("allowed_access", ctypes.c_uint64), ("parent_fd", ctypes.c_int32)]

    all_access = (1 << 13) - 1
    attr = Ruleset(all_access)
    ruleset = libc.syscall(444, ctypes.byref(attr), ctypes.sizeof(attr), 0)
    if ruleset < 0:
        raise RuntimeError(
            "isolated compiler verification is unavailable: cannot create filesystem rules"
        )

    def allow(path, access):
        if not Path(path).exists():
            return
        descriptor = os.open(path, os.O_PATH | os.O_CLOEXEC)
        try:
            rule = PathRule(access, descriptor)
            if libc.syscall(445, ruleset, 1, ctypes.byref(rule), 0) < 0:
                raise RuntimeError(
                    "isolated compiler verification is unavailable: cannot allow toolchain files"
                )
        finally:
            os.close(descriptor)

    try:
        for path in [
            "/usr",
            "/lib",
            "/lib64",
            "/bin",
            "/sbin",
            "/etc/alternatives",
            "/etc/java-17-openjdk",
        ]:
            allow(path, 1 | 4 | 8)
        for path in [
            "/etc/ld.so.cache",
            "/etc/ssl/openssl.cnf",
            "/etc/localtime",
            "/dev/urandom",
            "/dev/random",
        ]:
            allow(path, 4)
        allow("/dev/null", 2 | 4)
        # All C/JS source files use a private directory prepared by the parent.
        allow(str(Path(source).resolve().parent), all_access)
        if libc.prctl(38, 1, 0, 0, 0) < 0 or libc.syscall(446, ruleset, 0) < 0:
            raise RuntimeError(
                "isolated compiler verification is unavailable: cannot enforce filesystem rules"
            )
    finally:
        os.close(ruleset)


if __name__ == "__main__":
    command = sys.argv[1:]
    try:
        source = next(
            arg for arg in command if Path(arg).suffix in {".js", ".java", ".c", ".cpp"}
        )
        restrict(source)
        os.execv(command[0], command)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(126)
