@echo off
call mvn clean -Pp01
call mvn clean -Pp02
call mvn clean -Pp03
call mvn clean -Pp04

start call mvn test -Pp01
start call mvn test -Pp02
rem start call mvn test -Pp03
rem start call mvn test -Pp04
