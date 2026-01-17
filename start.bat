@echo off
title Todo List App Launcher with Minikube
color 0A

:menu
cls
echo.
echo  =============================================
echo         Todo List App - Single Container
echo  =============================================
echo.
echo  0. Start/Stop Minikube (wajib untuk Kubernetes lokal)
echo  1. Build Docker image
echo  2. Jalankan lokal (Docker) - Akses http://localhost:8080
echo  3. Deploy ke Kubernetes (Minikube)
echo  4. Cek status pod ^& HPA
echo  5. Update aplikasi (restart deployment)
echo  6. Akses app di browser (via Minikube service)
echo  7. Hapus deployment (cleanup)
echo  8. Keluar
echo.
echo  Catatan: Pastikan Minikube ^& kubectl terinstall. Jika belum:
echo    - Download Minikube: https://minikube.sigs.k8s.io/docs/start/
echo    - kubectl: https://kubernetes.io/docs/tasks/tools/
echo.
set /p pilihan=Masukkan nomor pilihan : 

if "%pilihan%"=="0" goto minikube_manage
if "%pilihan%"=="1" goto build
if "%pilihan%"=="2" goto local
if "%pilihan%"=="3" goto deploy
if "%pilihan%"=="4" goto status
if "%pilihan%"=="5" goto update
if "%pilihan%"=="6" goto access
if "%pilihan%"=="7" goto cleanup
if "%pilihan%"=="8" goto exit
goto menu

:minikube_manage
cls
echo.
echo  =============================================
echo         Manage Minikube
echo  =============================================
echo  1. Start Minikube (jika belum jalan)
echo  2. Stop Minikube
echo  3. Cek status Minikube
echo  4. Kembali ke menu utama
echo.
set /p mk_choice=Pilih: 

if "%mk_choice%"=="1" goto start_minikube
if "%mk_choice%"=="2" goto stop_minikube
if "%mk_choice%"=="3" goto check_minikube
if "%mk_choice%"=="4" goto menu
goto minikube_manage

:start_minikube
echo.
echo Memeriksa apakah Minikube sudah jalan...
minikube status >nul 2>&1
if %errorlevel%==0 (
    echo Minikube sudah jalan.
) else (
    echo Starting Minikube dengan driver docker...
    minikube start --driver=docker
)
pause
goto minikube_manage

:stop_minikube
echo.
echo Stopping Minikube...
minikube stop
pause
goto minikube_manage

:check_minikube
echo.
echo Status Minikube:
minikube status
pause
goto minikube_manage

:build
echo.
echo Membangun Docker image...
docker build -t todo-app:latest ./app
echo.
echo Selesai build. Untuk Minikube, image lokal sudah siap (tidak perlu push).
pause
goto menu

:local
echo.
echo Menjalankan aplikasi secara lokal...
docker run --rm -p 8080:5000 -v %CD%/app/uploads:/uploads -v %CD%/app/data:/data --name todo-app-local todo-app:latest
pause
goto menu

:deploy
echo.
echo Memeriksa Minikube...
minikube status >nul 2>&1
if not %errorlevel%==0 (
    echo Minikube belum jalan. Jalankan menu 0 dulu!
    pause
    goto menu
)
echo Mendeploy ke Minikube...
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
kubectl apply -f kubernetes/hpa.yaml
echo.
echo Deploy selesai. Gunakan menu 6 untuk akses browser.
pause
goto menu

:status
echo.
echo Status Pod:
kubectl get pods -l app=todo-app
echo.
echo Status HPA:
kubectl get hpa todo-app-hpa
echo.
echo Status Service:
kubectl get svc todo-app-service
pause
goto menu

:update
echo.
echo Melakukan rolling update...
kubectl rollout restart deployment/todo-app
echo.
echo Tunggu beberapa detik... Cek status dengan menu 4.
pause
goto menu

:access
echo.
echo Mendapatkan URL service...
for /f "tokens=*" %%i in ('minikube service todo-app-service --url') do set SERVICE_URL=%%i
echo URL: %SERVICE_URL%
start %SERVICE_URL%
echo Buka di browser jika tidak otomatis.
pause
goto menu

:cleanup
echo.
set /p yakin=Hapus semua resource? (Y/N) : 
if /i "%yakin%"=="Y" (
    kubectl delete -f kubernetes/ --ignore-not-found=true
    echo Semua resource dihapus.
) else (
    echo Dibatalkan.
)
pause
goto menu

:exit
echo.
echo Terima kasih telah menggunakan launcher ini.
timeout /t 2 >nul
exit