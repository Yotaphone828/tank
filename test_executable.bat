@echo off
echo 测试可执行文件...
echo ================================
echo.

REM 检查可执行文件是否存在
if not exist "dist\TankBattle.exe" (
    echo 错误：找不到可执行文件！
    echo 请先运行 build.bat 或使用 PyInstaller 打包
    pause
    exit /b 1
)

echo 找到可执行文件: dist\TankBattle.exe
echo 文件大小:
dir "dist\TankBattle.exe" | find "TankBattle.exe"
echo.

echo 尝试启动游戏...
echo 如果游戏窗口正常显示，说明打包成功！
echo 游戏控制：
echo - WASD 或 方向键：移动坦克
echo - 空格键 或 左Ctrl：射击
echo - ESC：退出游戏
echo.

timeout /t 3 >nul
start "Tank Battle Game" /B "dist\TankBattle.exe"

echo 游戏已启动，请检查是否有游戏窗口出现。
echo 如果游戏正常运行，说明打包成功！
echo.
pause