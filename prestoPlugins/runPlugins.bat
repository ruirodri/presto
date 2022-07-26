@echo off

start "PRESTO PLUGIN DATASOURCE" /D ".\data_source" python data_source.py
start "PRESTO PLUGIN STORE EXECS" /D ".\store_executions" python store_executions.py
start "PRESTO PLUGIN RESULTS EXPLORER" /D ".\results_explorer_app" python explorer.py