@echo off
echo 正在打包坦克大战游戏...
echo ========================================

REM 清理之前的构建文件
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__

echo 使用PyInstaller进行打包...
pyinstaller --clean --noconfirm tank.spec

echo ========================================
echo 打包完成！
echo.
echo 可执行文件位置: dist\TankBattle.exe
echo.
pause