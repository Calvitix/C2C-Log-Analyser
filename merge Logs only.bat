@echo off
setlocal enabledelayedexpansion

:: Dossier racine
set "root=E:\C2CModding\Input"

:: Trouver le dernier dossier Log_*
set "lastDir="

for /f "delims=" %%d in ('dir "%root%\Log_*" /b /ad /o-n') do (
    if not defined lastDir (
        set "lastDir=%%d"
    )
)

if not defined lastDir (
    echo Aucun dossier Log_ trouvé dans %root%
    pause
    exit /b
)

echo Dernier dossier = %lastDir%
set "target=%root%\%lastDir%"

:: Fusionner les fichiers
for /f "delims=" %%d in ('dir "%root%\Log_*" /b /ad /o-n') do (
    if /i not "%%d"=="%lastDir%" (
        echo Traitement du dossier %%d
        for %%f in ("%root%\%%d\*") do (
            set "fname=%%~nxf"
            echo Fusion de %%f >> "%target%\!fname!"
            type "%%f" >> "%target%\!fname!"
            echo. >> "%target%\!fname!"
        )
    )
)

:: Supprimer les anciens dossiers
for /f "delims=" %%d in ('dir "%root%\Log_*" /b /ad /o-n') do (
    if /i not "%%d"=="%lastDir%" (
        echo Suppression du dossier %%d
        rmdir /s /q "%root%\%%d"
    )
)

echo Fusion terminee. Tous les fichiers sont dans : %target%
pause
