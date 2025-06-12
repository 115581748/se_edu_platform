import subprocess
import time
from pathlib import Path
import requests
import sys
import shutil

ROOT = Path(__file__).resolve().parent
BACKEND_CMD = [sys.executable, "-m", "uvicorn", "app:app", "--port", "8000"]
FRONTEND_CMD = ["npm", "run", "dev", "--", "--port", "5173"]


def start_process(cmd, cwd=None):
    """Start a subprocess and return the handle."""
    exe = cmd[0]
    # Ensure command exists to avoid FileNotFoundError
    if shutil.which(exe) is None:
        raise RuntimeError(f"Command '{exe}' not found. Is it installed and on your PATH?")
    return subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def check_url(url, retries=5, delay=1):
    """Check whether a URL is reachable within given retries."""
    for _ in range(retries):
        try:
            resp = requests.get(url)
            if resp.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(delay)
    return False


def main():
    backend_dir = ROOT / "backend"
    backend_proc = start_process(BACKEND_CMD, cwd=backend_dir)
    time.sleep(5)
    backend_ok = check_url("http://localhost:8000/docs")

    frontend_dir = ROOT / "frontend"
    frontend_proc = start_process(FRONTEND_CMD, cwd=frontend_dir)
    time.sleep(5)
    frontend_ok = check_url("http://localhost:5173")

    backend_proc.terminate()
    frontend_proc.terminate()
    backend_proc.wait()
    frontend_proc.wait()

    if backend_ok and frontend_ok:
        print("Both backend and frontend started successfully.")
    else:
        print("Failed to start backend or frontend.")


if __name__ == "__main__":
    main()
