@echo off
rem Existing compile_item invokes this twice; -g forces a real engine run each time.
latexmk -xelatex -g %*
exit /b %errorlevel%
