@echo off
setlocal enabledelayedexpansion

:: Répertoires source et destination
set "src=C:\Users\Cal\Documents\My Games\Beyond the Sword\Logs"
set "dst=E:\C2CModding\Input"

:: Initialisation de la variable date max
set "latestFile="
set "latestDate="

:: Trouver le fichier le plus récent dans le dossier
for %%F in ("%src%\*") do (
    if exist "%%F" (
        for %%T in ("%%F") do (
            if not defined latestDate (
                set "latestDate=%%~tT"
                set "latestFile=%%F"
            ) else (
                if "%%~tT" GTR "!latestDate!" (
                    set "latestDate=%%~tT"
                    set "latestFile=%%F"
                )
            )
        )
    )
)

:: Si aucun fichier trouvé
if not defined latestDate (
    echo Aucun fichier trouvé dans %src%
    pause
    exit /b
)

:: Extraire la date/heure du fichier le plus récent
:: Format renvoyé par %%~tF = jj/MM/aaaa hh:mm
for /f "tokens=1,2 delims= " %%a in ("!latestDate!") do (
    set "d=%%a"
    set "t=%%b"
)

:: Découpage date jj/MM/aaaa
for /f "tokens=1-3 delims=/" %%a in ("!d!") do (
    set "JJ=%%a"
    set "MM=%%b"
    set "YYYY=%%c"
)

:: Découpage heure hh:mm
for /f "tokens=1-2 delims=:" %%a in ("!t!") do (
    set "HH=%%a"
    set "Min=%%b"
)

:: Construire le nom du dossier
set "folder=Log_!YYYY!!MM!!JJ!_!HH!!Min!"

:: Créer le dossier destination daté
set "destdir=%dst%\!folder!"
mkdir "!destdir!"

:: Copier les fichiers
xcopy "%src%\*" "!destdir!\" /Y /I

echo Fichiers copies dans : "!destdir!"
echo Date de reference (dernier fichier modifie) : !latestDate!

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
