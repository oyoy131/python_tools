@echo off
echo =====================================
echo    WebSocket 监控系统启动脚本
echo =====================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 检查依赖是否安装
echo 检查依赖包...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo 错误：依赖包安装失败
        pause
        exit /b 1
    )
)

echo 依赖检查完成！
echo.

REM 显示选择菜单
:menu
echo 请选择启动模式：
echo 1. 完整启动 (监控客户端 + Web界面)
echo 2. 仅启动监控客户端
echo 3. 仅启动Web界面
echo 4. 退出
echo.
set /p choice=请输入选择 (1-4): 

if "%choice%"=="1" (
    echo 启动完整监控系统...
    python main.py all
    goto end
)
if "%choice%"=="2" (
    echo 启动监控客户端...
    python main.py monitor
    goto end
)
if "%choice%"=="3" (
    echo 启动Web界面...
    python main.py web
    goto end
)
if "%choice%"=="4" (
    goto end
)

echo 无效选择，请重新输入
echo.
goto menu

:end
echo.
echo 监控系统已关闭
pause
