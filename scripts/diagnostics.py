#!/usr/bin/env python3
"""LUMI Voice Assistant — System Diagnostics.

Runs comprehensive checks on all dependencies, hardware, and services.
"""

import sys
import platform
import shutil
import subprocess


def check(name: str, func):
    try:
        ok, msg = func()
        status = "[OK]" if ok else "[!!]"
        print(f"  {status} {name}: {msg}")
        return ok
    except Exception as e:
        print(f"  [FAIL] {name}: {e}")
        return False


def check_python():
    v = sys.version_info
    ok = v >= (3, 10)
    return ok, f"Python {v.major}.{v.minor}.{v.micro} ({'OK' if ok else 'Need >=3.10'})"


def check_platform():
    return True, f"{platform.system()} {platform.release()} ({platform.machine()})"


def check_import(module_name: str, pip_name: str = None):
    def _check():
        try:
            mod = __import__(module_name)
            ver = getattr(mod, "__version__", "unknown")
            return True, f"{module_name} {ver}"
        except ImportError:
            install = pip_name or module_name
            return False, f"{module_name} not installed (pip install {install})"
    return _check


def check_sounddevice():
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        if not isinstance(devices, list):
            devices = [devices]
        inputs = sum(1 for d in devices if isinstance(d, dict) and d.get("max_input_channels", 0) > 0)
        outputs = sum(1 for d in devices if isinstance(d, dict) and d.get("max_output_channels", 0) > 0)
        return True, f"sounddevice {sd.__version__} — {inputs} input(s), {outputs} output(s)"
    except Exception as e:
        return False, f"sounddevice error: {e}"


def check_ollama():
    import httpx
    try:
        resp = httpx.get("http://localhost:11434/api/tags", timeout=5)
        data = resp.json()
        models = [m.get("name", "") for m in data.get("models", [])]
        return True, f"Ollama running, {len(models)} model(s): {', '.join(models[:5])}"
    except httpx.ConnectError:
        return False, "Ollama not running (start with: ollama serve)"
    except Exception as e:
        return False, f"Ollama error: {e}"


def check_piper():
    from pathlib import Path
    path = shutil.which("piper") or shutil.which("piper.exe")
    if not path:
        candidates = [
            Path("piper") / "piper.exe",
            Path("piper") / "piper",
            Path(__file__).parent.parent / "piper" / "piper.exe",
            Path(__file__).parent.parent / "piper" / "piper",
        ]
        for c in candidates:
            if c.exists():
                path = str(c)
                break
    if path:
        return True, f"Piper found at {path}"
    return False, "Piper not found in PATH or ./piper/. Download from https://github.com/rhasspy/piper/releases"


def check_ros2():
    try:
        import rclpy
        return True, "rclpy available"
    except ImportError:
        return False, "ROS 2 (rclpy) not available — optional for standalone use"


def check_disk_space():
    import os
    if hasattr(os, "statvfs"):
        st = os.statvfs(".")
        free_gb = (st.f_bavail * st.f_frsize) / (1024**3)
    else:
        # Windows
        import ctypes
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(
            ctypes.c_wchar_p("."), None, None, ctypes.pointer(free_bytes)
        )
        free_gb = free_bytes.value / (1024**3)
    return free_gb > 1.0, f"{free_gb:.1f} GB free"


def check_memory():
    try:
        import psutil
        mem = psutil.virtual_memory()
        return True, f"{mem.total / (1024**3):.1f} GB total, {mem.available / (1024**3):.1f} GB available"
    except ImportError:
        return True, "psutil not installed — cannot check memory details"


def main():
    print("\n" + "=" * 60)
    print("  LUMI Voice Assistant — System Diagnostics")
    print("=" * 60)

    print("\n[System]")
    check("Python", check_python)
    check("Platform", check_platform)
    check("Disk Space", check_disk_space)
    check("Memory", check_memory)

    print("\n[Python Packages]")
    check("numpy", check_import("numpy"))
    check("sounddevice", check_sounddevice)
    check("faster-whisper", check_import("faster_whisper", "faster-whisper"))
    check("httpx", check_import("httpx"))
    check("PySide6", check_import("PySide6"))
    check("pydantic", check_import("pydantic"))
    check("yaml", check_import("yaml", "pyyaml"))
    check("soundfile", check_import("soundfile"))
    check("scipy", check_import("scipy"))

    print("\n[External Services]")
    check("Ollama", check_ollama)
    check("Piper TTS", check_piper)
    check("ROS 2", check_ros2)

    print("\n" + "=" * 60)
    print("  Diagnostics complete.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
