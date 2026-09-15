import pytest
import subprocess
import os

def test_startup_fails_without_production_auth():
    env = os.environ.copy()
    env["DEMO_MODE"] = "false"
    env["PYTHONPATH"] = "C:/Users/FIRSTHOUR/FIRST-HOUR/backend"
    
    # Try to run the app as a subprocess
    result = subprocess.run(
        ["python", "-m", "uvicorn", "app.main:app"],
        env=env,
        capture_output=True,
        text=True
    )
    
    assert result.returncode != 0
    assert "DEMO_MODE is false but no production authentication provider is configured" in result.stderr
