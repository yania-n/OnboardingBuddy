import subprocess
import time
import sys
import os

def main():
    """
    Spawns both the FastAPI backend and Vite frontend servers in concurrent processes.
    - Backend: Uvicorn listening on http://0.0.0.0:8000
    - Frontend: Vite listening on http://0.0.0.0:5173 (proxied to Backend /api)
    """
    print("Starting OnboardingBuddy FastAPI Backend on http://0.0.0.0:8000 ...")
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd=os.path.join(os.path.dirname(__file__), "backend")
    )

    time.sleep(2)

    print("Starting OnboardingBuddy React Frontend on http://127.0.0.1:5173 ...")
    frontend_cmd = "npm.cmd run dev" if sys.platform == "win32" else "npm run dev"
    frontend_proc = subprocess.Popen(
        frontend_cmd,
        shell=True,
        cwd=os.path.join(os.path.dirname(__file__), "frontend")
    )

    print("\nOnboardingBuddy is running!")
    print("  -> Backend API:  http://127.0.0.1:8000/docs")
    print("  -> Frontend App: http://127.0.0.1:5173\n")

    try:
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        backend_proc.terminate()
        frontend_proc.terminate()

if __name__ == "__main__":
    main()
