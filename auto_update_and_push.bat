@echo off
chcp 65001 > nul
echo ==================================================
echo  OMNISTAT CORE: AUTO FETCH MKETQUA.NET & GITHUB PUSH
echo ==================================================

python auto_update_and_push.py

pause
