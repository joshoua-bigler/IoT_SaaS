@echo off
setlocal

echo Starting Hub...
start "Hub" cmd /c "cd /d src_hub && venv\Scripts\activate && python hub\main.py"

echo Starting Device...
start "Device" cmd /c "cd /d src_device && venv\Scripts\activate && python edge_device\main.py"

echo Starting Device Management...
start "Device Management" cmd /c "cd /d src_device_mgmt && venv\Scripts\activate && python device_mgmt\main.py"

echo All services have been started.
endlocal
