@echo off
chcp 65001 >nul
title 结婚生育成本计算器

echo.
echo ╔══════════════════════════════════════╗
echo ║          结婚生育成本计算器            ║
echo ║                                      ║
echo ║  一个帮助您规划家庭财务的现代化工具     ║
echo ╚══════════════════════════════════════╝
echo.
echo 正在检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到Python环境，请先安装Python 3.7+
    echo    下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python环境正常
echo.
echo 正在检查依赖包...
python -c "import customtkinter, matplotlib, numpy" >nul 2>&1
if errorlevel 1 (
    echo ❌ 缺少必要的依赖包，正在安装...
    pip install customtkinter matplotlib numpy pillow
    if errorlevel 1 (
        echo ❌ 依赖包安装失败，请手动运行: pip install -r requirements.txt
        pause
        exit /b 1
    )
    echo ✅ 依赖包安装完成
) else (
    echo ✅ 依赖包已安装
)

echo.
echo 正在启动应用程序...
echo 提示：如果窗口没有显示，请检查杀毒软件是否拦截了程序
echo.
python marriage_calculator.py

if errorlevel 1 (
    echo.
    echo ❌ 程序运行出错，请检查错误信息
    echo.
)
echo.
echo 感谢使用结婚生育成本计算器！
pause