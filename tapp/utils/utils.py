import os
import sys


def get_host():
    base_executable = os.path.basename(sys.executable)

    if base_executable.lower().startswith("maya"):
        return "maya"

    if base_executable.lower().startswith("nuke"):
        return "nuke"

    return "standalone"
