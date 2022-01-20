@echo off

start "CALCULATOR SERVICE" /D ".\calculator_service" python calculator_service.py
start "CALCULATOR APP" /D ".\calculator_app" python calculator.py
