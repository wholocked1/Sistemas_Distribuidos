@echo off
echo [INFO] Compilando...
javac -cp ".;msgpack-core-0.9.0.jar" Cliente2.java
if errorlevel 1 pause & exit
echo [INFO] Executando...
java -cp ".;msgpack-core-0.9.0.jar" Cliente2
pause
