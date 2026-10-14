@echo off
title Mise a jour GitHub (avec tests)
setlocal enabledelayedexpansion

REM Se placer a la racine du projet (ce script y est stocke)
cd /d "%~dp0"

echo ============================================
echo   Mise a jour GitHub - avec tests
echo ============================================
echo.

REM --- Git installe ? ---
where git >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Git n'est pas installe ou pas dans le PATH.
    echo Telecharge-le sur https://git-scm.com/download/win
    goto :fail
)

REM --- Depot cible : c'est ICI que tu choisis ou ca part ---
set "TARGET_URL=https://github.com/marcle-bert26-ui/fs-telemetry-V2.git"

REM --- Depot Git ? (cherche aussi dans les dossiers parents) ---
git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
    echo Premiere utilisation : creation du depot Git dans :
    echo     !CD!
    echo.
    git init -b main
    git remote add origin "!TARGET_URL!"
    echo Recuperation de l'historique distant...
    git fetch origin
    if errorlevel 1 (
        echo [ERREUR] Impossible de joindre le depot distant. Verifie l'URL et tes droits.
        goto :fail
    )
    git remote set-head origin -a >nul 2>&1
    set "RB="
    for /f "delims=" %%h in ('git symbolic-ref --short refs/remotes/origin/HEAD 2^>nul') do set "RB=%%h"
    if defined RB (
        set "RBRANCH=!RB:origin/=!"
        git symbolic-ref HEAD refs/heads/!RBRANCH!
        git reset !RB! >nul 2>&1
        echo Depot relie sur la branche !RBRANCH!
    ) else (
        echo Depot distant vide : nouvelle branche main.
    )
    if not exist ".gitignore" (
        echo Creation d'un .gitignore de base...
        > .gitignore echo node_modules/
        >> .gitignore echo __pycache__/
        >> .gitignore echo *.pyc
        >> .gitignore echo .venv/
        >> .gitignore echo .env
    )
    echo.
)

REM --- Se placer a la racine reelle du depot ---
for /f "delims=" %%t in ('git rev-parse --show-toplevel') do cd /d "%%t"
echo Racine du depot : %CD%

REM --- Branche courante ---
for /f "delims=" %%b in ('git rev-parse --abbrev-ref HEAD') do set "BRANCH=%%b"
echo Branche : %BRANCH%

set "REMOTE="
for /f "delims=" %%r in ('git remote get-url origin 2^>nul') do set "REMOTE=%%r"

if not defined REMOTE (
    echo Aucun depot "origin" : ajout de !TARGET_URL!
    git remote add origin "!TARGET_URL!"
    set "REMOTE=!TARGET_URL!"
)

if /i not "!REMOTE!"=="!TARGET_URL!" (
    echo [ATTENTION] origin pointe actuellement vers :
    echo     !REMOTE!
    echo Le depot cible voulu est :
    echo     !TARGET_URL!
    set /p "SWITCH=Faire pointer origin vers le depot cible ? (o/N) : "
    if /i not "!SWITCH!"=="o" (
        echo Envoi annule.
        goto :fail
    )
    git remote set-url origin "!TARGET_URL!"
    set "REMOTE=!TARGET_URL!"
)

echo Depot   : !REMOTE!
echo.

REM ============================================
REM   ETAPE 1 : TESTS (detection automatique)
REM ============================================
echo [1/4] Lancement des tests...
echo.

set "TESTED=0"

if exist "package.json" (
    echo Projet Node.js detecte : npm test
    call npm test
    if errorlevel 1 goto :tests_failed
    set "TESTED=1"
)

if exist "pytest.ini" set "PYPROJ=1"
if exist "pyproject.toml" set "PYPROJ=1"
if exist "requirements.txt" set "PYPROJ=1"
if exist "setup.py" set "PYPROJ=1"
if exist "tests" set "PYPROJ=1"
if exist "test" set "PYPROJ=1"
if defined PYPROJ if "%TESTED%"=="0" (
    echo Projet Python detecte : pytest
    python -m pytest --version >nul 2>&1
    if errorlevel 1 (
        echo pytest n'est pas installe : installation automatique...
        python -m pip install pytest
        if errorlevel 1 (
            echo [ERREUR] Installation de pytest impossible.
            goto :tests_failed
        )
        if exist "requirements.txt" python -m pip install -r requirements.txt
    )
    python -m pytest -q
    if errorlevel 6 goto :tests_failed
    if errorlevel 5 (
        echo [ATTENTION] Aucun test trouve dans le projet : on continue.
    ) else (
        if errorlevel 1 goto :tests_failed
    )
    set "TESTED=1"
)

if exist "pom.xml" if "%TESTED%"=="0" (
    echo Projet Maven detecte : mvn test
    call mvn -q test
    if errorlevel 1 goto :tests_failed
    set "TESTED=1"
)

if exist "Cargo.toml" if "%TESTED%"=="0" (
    echo Projet Rust detecte : cargo test
    cargo test
    if errorlevel 1 goto :tests_failed
    set "TESTED=1"
)

if exist "go.mod" if "%TESTED%"=="0" (
    echo Projet Go detecte : go test
    go test ./...
    if errorlevel 1 goto :tests_failed
    set "TESTED=1"
)

if "%TESTED%"=="0" (
    echo [ATTENTION] Aucun framework de tests detecte.
    set /p "CONT=Continuer l'envoi sans tests ? (o/N) : "
    if /i not "!CONT!"=="o" (
        echo Envoi annule.
        goto :fail
    )
)

echo.
echo Tests OK.
echo.

REM ============================================
REM   ETAPE 2 : COMMIT
REM ============================================
echo [2/4] Preparation du commit...
git add -A

git diff --cached --quiet
if not errorlevel 1 (
    echo Aucune modification locale a committer.
    goto :push
)

for /f "delims=" %%d in ('powershell -NoProfile -Command "Get-Date -Format 'yyyy-MM-dd HH:mm'"') do set "NOW=%%d"
set "COMMITMSG=Mise a jour - %NOW% (tests OK)"

git commit -m "%COMMITMSG%"
if errorlevel 1 (
    echo [ERREUR] Le commit a echoue.
    goto :fail
)

REM ============================================
REM   ETAPE 3 : SYNCHRO AVEC GITHUB
REM ============================================
:push
echo.
echo [3/4] Recuperation des changements distants...
git ls-remote --exit-code --heads origin !BRANCH! >nul 2>&1
if not errorlevel 1 (
    git pull --rebase origin !BRANCH!
    if errorlevel 1 (
        echo.
        echo [ERREUR] La synchro avec GitHub a echoue ^(conflit possible^).
        echo Resous les conflits, puis lance : git rebase --continue
        echo ^(ou annule avec : git rebase --abort^)
        goto :fail
    )
) else (
    echo Branche distante absente : premier envoi.
)

REM ============================================
REM   ETAPE 4 : PUSH
REM ============================================
echo.
echo [4/4] Envoi vers GitHub...
git push -u origin %BRANCH%
if errorlevel 1 (
    echo.
    echo [ERREUR] L'envoi a echoue. Verifie ta connexion et tes identifiants GitHub.
    goto :fail
)

echo.
echo ============================================
echo   Termine ! Tests OK et GitHub a jour.
echo ============================================
echo.
timeout /t 5 >nul
endlocal
exit /b 0

:tests_failed
echo.
echo ============================================
echo   [ERREUR] Les tests ont echoue.
echo   Rien n'a ete envoye vers GitHub.
echo ============================================
echo.
pause
endlocal
exit /b 1

:fail
echo.
pause
endlocal
exit /b 1
