@echo off
:: stop.bat — Stop ONLY the services started by start.bat (uses pids.txt file)
:: IMPORTANT: Only kills PIDs recorded in pids.txt — never uses taskkill /IM
:: which could accidentally kill other processes.

echo Stopping Verizon Customer Credit Platform services...

if exist pids.txt (
    for /f %%p in (pids.txt) do (
        taskkill /PID %%p /F >nul 2>&1
        if errorlevel 1 (
            echo   X PID %%p already stopped
        ) else (
            echo   OK Stopped PID %%p
        )
    )
    del pids.txt
    echo All services stopped
) else (
    echo No pids.txt found -- services may not be running or were stopped already
)

echo.
