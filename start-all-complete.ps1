# 西华大学宿舍电费监控系统 - 完整启动脚本 (PowerShell版本)
# 功能：一键启动所有服务（后端、前端、NoneBot、NapCatQQ）

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 设置变量
$BackendPort = 8000
$FrontendPort = 3000
$NoneBotPort = 8080
$NapCatPath = "$env:USERPROFILE\Desktop\NapCatQQ.exe"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "西华大学宿舍电费监控系统 - 完整启动" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否在项目根目录
if (-not (Test-Path "backend\run.py")) {
    Write-Host "[错误] 请在项目根目录运行此脚本" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

Write-Host "[步骤 1/6] 检查环境..." -ForegroundColor Yellow
Write-Host ""

# 检查Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[检查] Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[错误] 未检测到Python" -ForegroundColor Red
    Write-Host "请确保Python已安装并添加到PATH环境变量" -ForegroundColor Yellow
    Read-Host "按回车键退出"
    exit 1
}

# 检查Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Host "[检查] Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "[警告] 未检测到Node.js，前端服务将无法启动" -ForegroundColor Yellow
    Write-Host "请安装Node.js: https://nodejs.org/" -ForegroundColor Yellow
    Write-Host ""
}

# 检查.env文件
if (-not (Test-Path "backend\.env")) {
    Write-Host "[警告] 未找到 backend\.env 文件" -ForegroundColor Yellow
    if (Test-Path "backend\.env.example") {
        Write-Host "[创建] 正在从 .env.example 创建..." -ForegroundColor Yellow
        Copy-Item "backend\.env.example" "backend\.env"
        Write-Host "[提示] 请编辑 backend\.env 文件配置数据库等信息" -ForegroundColor Yellow
        Write-Host ""
    } else {
        Write-Host "[错误] 未找到 .env.example 文件" -ForegroundColor Red
        Read-Host "按回车键退出"
        exit 1
    }
}

Write-Host "[步骤 2/6] 检查并停止已运行的服务..." -ForegroundColor Yellow
Write-Host ""

# 函数：停止占用端口的进程
function Stop-Port {
    param($Port, $ServiceName)
    
    $processes = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | 
        Select-Object -ExpandProperty OwningProcess -Unique
    
    if ($processes) {
        Write-Host "[停止] 正在停止 $ServiceName (端口 $Port)..." -ForegroundColor Yellow
        foreach ($pid in $processes) {
            try {
                Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            } catch {
                # 忽略错误
            }
        }
        Start-Sleep -Seconds 2
    }
}

# 停止已运行的服务
Stop-Port -Port $BackendPort -ServiceName "后端服务"
Stop-Port -Port $FrontendPort -ServiceName "前端服务"
Stop-Port -Port $NoneBotPort -ServiceName "NoneBot服务"

# 停止NapCatQQ
$napcatProcesses = Get-Process -Name "NapCatQQ" -ErrorAction SilentlyContinue
if ($napcatProcesses) {
    Write-Host "[停止] 正在停止 NapCatQQ..." -ForegroundColor Yellow
    $napcatProcesses | Stop-Process -Force
    Start-Sleep -Seconds 2
}

Write-Host ""
Write-Host "[步骤 3/6] 检查依赖..." -ForegroundColor Yellow
Write-Host ""

# 检查后端依赖
Set-Location backend
try {
    python -c "import fastapi" 2>&1 | Out-Null
    Write-Host "[检查] 后端依赖已安装" -ForegroundColor Green
} catch {
    Write-Host "[安装] 正在安装后端依赖..." -ForegroundColor Yellow
    python -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[错误] 后端依赖安装失败" -ForegroundColor Red
        Read-Host "按回车键退出"
        exit 1
    }
}

# 检查NoneBot依赖
Set-Location nonebot_bot
try {
    python -c "import nonebot" 2>&1 | Out-Null
    Write-Host "[检查] NoneBot 依赖已安装" -ForegroundColor Green
} catch {
    Write-Host "[安装] 正在安装 NoneBot 依赖..." -ForegroundColor Yellow
    pip install nonebot2 nonebot-adapter-onebot httpx
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[警告] NoneBot 依赖安装失败，QQ机器人功能可能无法使用" -ForegroundColor Yellow
    }
}
Set-Location ..\..

# 检查前端依赖
if (Test-Path "frontend\node_modules") {
    Write-Host "[检查] 前端依赖已安装" -ForegroundColor Green
} else {
    Write-Host "[安装] 正在安装前端依赖..." -ForegroundColor Yellow
    Set-Location frontend
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[警告] 前端依赖安装失败" -ForegroundColor Yellow
    }
    Set-Location ..
}

Write-Host ""
Write-Host "[步骤 4/6] 启动后端服务..." -ForegroundColor Yellow
Write-Host ""

# 启动后端（新窗口）
$backendScript = "cd /d `"$PWD\backend`" && python run.py"
Start-Process cmd -ArgumentList "/k", $backendScript -WindowStyle Normal
Start-Sleep -Seconds 5

# 检查后端是否启动成功
Write-Host "[检查] 正在检查后端服务状态..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
try {
    $response = Invoke-WebRequest -Uri "http://localhost:$BackendPort/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
    Write-Host "[成功] 后端服务已启动: http://localhost:$BackendPort" -ForegroundColor Green
} catch {
    Write-Host "[警告] 后端服务可能未正常启动，请检查后端窗口的错误信息" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[步骤 5/6] 启动 NoneBot QQ机器人..." -ForegroundColor Yellow
Write-Host ""

# 检查NapCat配置文件
$configDir = "$env:USERPROFILE\Desktop\config"
if (-not (Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir -Force | Out-Null
}

$configFile = "$configDir\onebot11.json"
if (-not (Test-Path $configFile)) {
    Write-Host "[配置] 正在复制 NapCat 配置文件..." -ForegroundColor Yellow
    Copy-Item "backend\nonebot_bot\napcat-config.json" $configFile -Force
    if (Test-Path $configFile) {
        Write-Host "[成功] 配置文件已复制" -ForegroundColor Green
    } else {
        Write-Host "[警告] 配置文件复制失败，请手动配置" -ForegroundColor Yellow
    }
}

# 启动NoneBot（新窗口）
$nonebotScript = "cd /d `"$PWD\backend\nonebot_bot`" && python bot.py"
Start-Process cmd -ArgumentList "/k", $nonebotScript -WindowStyle Normal
Start-Sleep -Seconds 5

# 检查NoneBot是否启动成功
Write-Host "[检查] 正在检查 NoneBot 服务状态..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
try {
    $response = Invoke-WebRequest -Uri "http://localhost:$NoneBotPort/docs" -TimeoutSec 2 -ErrorAction SilentlyContinue
    Write-Host "[成功] NoneBot 服务已启动: http://localhost:$NoneBotPort" -ForegroundColor Green
} catch {
    Write-Host "[警告] NoneBot 服务可能未正常启动，请检查 NoneBot 窗口的错误信息" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[步骤 6/6] 启动 NapCatQQ 和前端服务..." -ForegroundColor Yellow
Write-Host ""

# 检查NapCatQQ是否存在
if (Test-Path $NapCatPath) {
    Write-Host "[启动] 正在启动 NapCatQQ..." -ForegroundColor Yellow
    Start-Process $NapCatPath
    Start-Sleep -Seconds 3
    Write-Host "[提示] NapCatQQ 窗口已打开" -ForegroundColor Green
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "[重要] NapCatQQ 登录提示" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. 如果使用扫码登录：" -ForegroundColor White
    Write-Host "   - NapCatQQ 窗口会显示二维码" -ForegroundColor Gray
    Write-Host "   - 使用手机QQ扫描二维码登录" -ForegroundColor Gray
    Write-Host "   - 登录成功后会自动连接到 NoneBot" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. 如果使用账号密码登录：" -ForegroundColor White
    Write-Host "   - 在 NapCatQQ 窗口中输入QQ号和密码" -ForegroundColor Gray
    Write-Host "   - 登录成功后会自动连接到 NoneBot" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. 连接成功后，NoneBot 窗口会显示连接信息" -ForegroundColor White
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host "[警告] 未找到 NapCatQQ.exe" -ForegroundColor Yellow
    Write-Host "路径: $NapCatPath" -ForegroundColor Gray
    Write-Host ""
    Write-Host "请手动启动 NapCatQQ：" -ForegroundColor Yellow
    Write-Host "1. 下载 NapCatQQ: https://github.com/NapNeko/NapCatQQ/releases" -ForegroundColor Gray
    Write-Host "2. 将 NapCatQQ.exe 放到桌面" -ForegroundColor Gray
    Write-Host "3. 或修改脚本中的 `$NapCatPath` 变量" -ForegroundColor Gray
    Write-Host ""
}

# 启动前端
if (Test-Path "frontend\node_modules") {
    Write-Host "[启动] 正在启动前端服务..." -ForegroundColor Yellow
    $frontendScript = "cd /d `"$PWD\frontend`" && npm run dev"
    Start-Process cmd -ArgumentList "/k", $frontendScript -WindowStyle Normal
    Start-Sleep -Seconds 3
    Write-Host "[成功] 前端服务已启动: http://localhost:$FrontendPort" -ForegroundColor Green
} else {
    Write-Host "[跳过] 前端依赖未安装，跳过前端启动" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "启动完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "服务地址：" -ForegroundColor White
Write-Host "  - 后端服务:  http://localhost:$BackendPort" -ForegroundColor Gray
Write-Host "  - API文档:   http://localhost:$BackendPort/docs" -ForegroundColor Gray
Write-Host "  - 前端界面:  http://localhost:$FrontendPort" -ForegroundColor Gray
Write-Host "  - NoneBot:   http://localhost:$NoneBotPort" -ForegroundColor Gray
Write-Host ""
Write-Host "服务窗口：" -ForegroundColor White
Write-Host "  - 后端服务窗口：显示后端日志" -ForegroundColor Gray
Write-Host "  - NoneBot窗口：显示QQ机器人日志" -ForegroundColor Gray
Write-Host "  - NapCatQQ窗口：显示登录二维码（如需要）" -ForegroundColor Gray
Write-Host "  - 前端服务窗口：显示前端构建日志" -ForegroundColor Gray
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "[重要提示]" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. NapCatQQ 登录：" -ForegroundColor White
Write-Host "   - 查看 NapCatQQ 窗口，按提示扫码或输入账号密码" -ForegroundColor Gray
Write-Host "   - 登录成功后会自动连接到 NoneBot" -ForegroundColor Gray
Write-Host ""
Write-Host "2. 检查连接状态：" -ForegroundColor White
Write-Host "   - 查看 NoneBot 窗口，应该显示 `连接成功` 或类似信息" -ForegroundColor Gray
Write-Host "   - 如果连接失败，检查配置文件路径和端口设置" -ForegroundColor Gray
Write-Host ""
Write-Host "3. 停止服务：" -ForegroundColor White
Write-Host "   - 关闭各个服务窗口即可停止服务" -ForegroundColor Gray
Write-Host "   - 或运行 stop-all.bat 脚本停止所有服务" -ForegroundColor Gray
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Read-Host "按回车键退出"
