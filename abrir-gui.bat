@echo off
rem Doble clic para abrir la interfaz grafica de html2pptx
cd /d "%~dp0"
start "" pythonw -m html2pptx.gui
