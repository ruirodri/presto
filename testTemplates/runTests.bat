@echo off

call ..\prestoPlugins\data_source\resetData.bat
start "API TEST" /D ".\testAPI" python runMultipleAPI.py
start "WEB APP TEST" /D ".\testWWW" fourParallel.bat