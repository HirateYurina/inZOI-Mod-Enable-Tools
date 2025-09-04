@echo off

:: 检查Python是否安装
where python >nul 2>nul
if %errorlevel% equ 0 (
    python "inZOI Mod Enable Tools.py"
) else (
    echo 错误：未检测到Python环境
    
    :: 检查操作系统版本
    ver | findstr /i "10.0.1" >nul
    if %errorlevel% equ 0 (
        echo 检测到您使用的是Windows 10或Windows 11系统
        echo 建议通过Microsoft Store搜索并安装Python以快速使用
    ) else (
        echo 请先安装Python并添加到系统环境变量
    )
)
pause