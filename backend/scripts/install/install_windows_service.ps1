# Windows服务安装脚本
# 需要以管理员身份运行PowerShell

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "宿舍电费监控系统 - Windows服务安装" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 检查管理员权限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[错误] 请以管理员身份运行此脚本" -ForegroundColor Red
    exit 1
}

# 获取脚本所在目录
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $scriptDir "..\.."

# 检查NSSM
$nssmPath = "nssm.exe"
if (-not (Get-Command $nssmPath -ErrorAction SilentlyContinue)) {
    Write-Host "[提示] 未找到nssm.exe，请先下载NSSM:" -ForegroundColor Yellow
    Write-Host "  下载地址: https://nssm.cc/download" -ForegroundColor Yellow
    Write-Host "  解压后将nssm.exe放到系统PATH或当前目录" -ForegroundColor Yellow
    Write-Host ""
    
    $nssmPath = Read-Host "请输入nssm.exe的完整路径（或按Enter跳过）"
    if ([string]::IsNullOrEmpty($nssmPath)) {
        Write-Host "[错误] 未提供NSSM路径，退出" -ForegroundColor Red
        exit 1
    }
}

# 获取Python路径
$pythonPath = (Get-Command python).Source
if (-not $pythonPath) {
    Write-Host "[错误] 未找到Python，请先安装Python" -ForegroundColor Red
    exit 1
}

Write-Host "Python路径: $pythonPath" -ForegroundColor Green
Write-Host "后端目录: $backendDir" -ForegroundColor Green
Write-Host ""

# 创建日志目录
$logDir = Join-Path $backendDir "logs"
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
}

# 安装服务
Write-Host "正在安装服务..." -ForegroundColor Yellow

& $nssmPath install DormPowerGuardBackend $pythonPath "$backendDir\run.py"
& $nssmPath set DormPowerGuardBackend AppDirectory $backendDir
& $nssmPath set DormPowerGuardBackend DisplayName "宿舍电费监控系统-后端"
& $nssmPath set DormPowerGuardBackend Description "宿舍电费监控系统后端服务"
& $nssmPath set DormPowerGuardBackend Start SERVICE_AUTO_START
& $nssmPath set DormPowerGuardBackend AppStdout "$logDir\stdout.log"
& $nssmPath set DormPowerGuardBackend AppStderr "$logDir\stderr.log"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "服务安装完成！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "启动服务: nssm start DormPowerGuardBackend" -ForegroundColor Yellow
Write-Host "停止服务: nssm stop DormPowerGuardBackend" -ForegroundColor Yellow
Write-Host "重启服务: nssm restart DormPowerGuardBackend" -ForegroundColor Yellow
Write-Host "查看状态: nssm status DormPowerGuardBackend" -ForegroundColor Yellow
Write-Host "删除服务: nssm remove DormPowerGuardBackend confirm" -ForegroundColor Yellow
Write-Host ""

$startNow = Read-Host "是否现在启动服务？(Y/N)"
if ($startNow -eq "Y" -or $startNow -eq "y") {
    & $nssmPath start DormPowerGuardBackend
    Start-Sleep -Seconds 2
    & $nssmPath status DormPowerGuardBackend
}
