@echo off
chcp 65001 >nul
title 業務巡訪地圖系統啟動器

echo ========================================================
echo   🗺️  業務外勤巡訪地圖系統 (Field Sales Map)
echo ========================================================
echo.
echo [1] 正在本機啟動地圖瀏覽器...
echo.

set DIR=%~dp0
start "" "%DIR%index.html"

echo 系統已於預設瀏覽器開啟！
echo 若要在手機連線使用，可使用 python -m http.server 8000 分享區網。
echo.
timeout /t 3 >nul
exit
