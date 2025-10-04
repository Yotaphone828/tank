@echo off
echo 正在快速打包坦克大战游戏...
pyinstaller --onefile --windowed --name TankBattle main.py
echo 打包完成！可执行文件在dist文件夹中。
pause