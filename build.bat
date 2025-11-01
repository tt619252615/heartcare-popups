@echo off
chcp 65001 >nul
echo ==========================================
echo    爱心关怀弹窗程序 - 打包工具
echo ==========================================
echo.

REM 检查是否指定了Python路径
if "%~1"=="" (
    REM 未指定，使用当前环境的python
    set PYTHON_CMD=python
    echo 使用当前环境的Python
) else (
    REM 指定了Python路径
    set PYTHON_CMD=%~1
    echo 使用指定的Python: %~1
)
echo.

REM 显示Python环境信息
echo [1/4] 检查Python环境...
echo.
%PYTHON_CMD% --version 2>nul
if errorlevel 1 (
    echo ❌ 错误: 找不到指定的Python！
    echo.
    echo 使用方法：
    echo   build.bat                          使用当前环境
    echo   build.bat python                   使用系统Python
    echo   build.bat C:\Python310\python.exe  使用指定Python
    echo   build.bat venv\Scripts\python.exe  使用虚拟环境
    echo.
    pause
    exit /b 1
)

echo Python路径: 
%PYTHON_CMD% -c "import sys; print(sys.executable)"
echo.

REM 检查是否在虚拟环境中
%PYTHON_CMD% -c "import sys; hasattr(sys, 'real_prefix') and print('✅ 虚拟环境(venv)') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix and print('✅ 虚拟环境')) or print('⚠️  系统Python')"
echo.

REM 检查依赖
echo [2/4] 检查依赖包...
%PYTHON_CMD% -c "import PyQt5; import numpy; import pydantic; import loguru; import keyboard; print('✅ 所有依赖包已安装')" 2>nul
if errorlevel 1 (
    echo ❌ 错误: 缺少必要的依赖包！
    echo.
    echo 正在尝试安装依赖...
    %PYTHON_CMD% -m pip install -r requirements.txt
    if errorlevel 1 (
        echo 安装失败！请手动运行: %PYTHON_CMD% -m pip install -r requirements.txt
        pause
        exit /b 1
    )
    echo ✅ 依赖安装完成
)
echo.

REM 检查PyInstaller
echo [3/4] 检查PyInstaller...
%PYTHON_CMD% -c "import PyInstaller; print(f'✅ PyInstaller {PyInstaller.__version__}')" 2>nul
if errorlevel 1 (
    echo ⚠️  未安装PyInstaller，正在安装...
    %PYTHON_CMD% -m pip install pyinstaller
    if errorlevel 1 (
        echo ❌ 安装失败！
        pause
        exit /b 1
    )
    echo ✅ PyInstaller 安装完成
)
echo.

echo [4/4] 开始打包程序...
echo.
echo 注意：打包过程可能需要几分钟，请耐心等待...
echo.

%PYTHON_CMD% -m PyInstaller build.spec --clean

if errorlevel 0 (
    echo.
    echo ==========================================
    echo    ✅ 打包完成！
    echo ==========================================
    echo.
    echo 📦 可执行文件: dist\HeartCarePopups.exe
    echo.
    echo 📋 使用说明：
    echo   1. 复制 dist\HeartCarePopups.exe
    echo   2. 确保 config.json 和 data 文件夹在同一目录
    echo   3. 右键 → 以管理员身份运行（ESC键功能需要）
    echo.
    echo 📁 完整的分发包应包含：
    echo   ├── HeartCarePopups.exe
    echo   ├── config.json
    echo   └── data/
    echo       └── messages.txt
    echo.
) else (
    echo.
    echo ==========================================
    echo    ❌ 打包失败
    echo ==========================================
    echo.
    echo 常见问题：
    echo   - 缺少依赖包：%PYTHON_CMD% -m pip install -r requirements.txt
    echo   - 路径问题：确保在项目根目录运行
    echo   - 权限问题：尝试以管理员身份运行此脚本
    echo.
)

pause
