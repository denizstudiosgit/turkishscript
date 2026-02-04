@echo off
setlocal enabledelayedexpansion
title TurkishCode v5 - EXE Derleme Araci
color 0b

echo ===========================================
echo    TURKISHCODE v5 DERLEME ASAMASI
echo ===========================================

:: 1. Sanal Ortam Kontrolü
if exist "compiler\Scripts\activate.bat" (
    echo [1/3] Sanal ortam aktif ediliyor...
    call "compiler\Scripts\activate.bat"
) else (
    color 0c
    echo [HATA] 'compiler' klasoru bulunamadi.
    echo Lutfen terminale su komutu yazin: python -m venv compiler
    pause
    exit
)

:: 2. cikti.py Kontrolü
if not exist "cikti.py" (
    color 0c
    echo [HATA] cikti.py dosyasi yok! TSM ceviri yapamamis olabilir.
    pause
    exit
)

:: 3. Temizlik
echo [2/3] Eski dosyalar temizleniyor...
if exist build rd /s /q build
if exist dist rd /s /q dist
if exist *.spec del /q *.spec

:: 4. Konsol Ayarı (TSM'den gelen degisken)
set "EXTRA_FLAGS="
if "%EXE_KONSOL%"=="YOK" (
    echo [BILGI] Uygulama pencere modunda derlenecek.
    set "EXTRA_FLAGS=--noconsole"
)

:: 5. PyInstaller Çalıştırma
echo [3/3] EXE uretiliyor, lutfen bekleyin...
:: Tırnak işaretleri klasör yolundaki boşluklar için kritiktir
python -m PyInstaller --onefile --add-data "grafik.py;." !EXTRA_FLAGS! "cikti.py"

:: 6. Sonuç Kontrolü
if exist "dist\cikti.exe" (
    echo.
    echo [OK] Derleme basarili! EXE tasiniyor...
    move /y "dist\cikti.exe" .
    
    :: Gereksizleri temizle
    rd /s /q build dist
    del /q *.spec
    
    color 0a
    echo ===========================================
    echo    ISLEM TAMAM: cikti.exe HAZIR!
    echo ===========================================
) else (
    color 0c
    echo.
    echo [HATA] EXE olusturulamadi. Yukaridaki Python hatalarini kontrol et!
)

pause