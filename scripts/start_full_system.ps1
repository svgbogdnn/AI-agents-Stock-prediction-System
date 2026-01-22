$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $ProjectRoot

Write-Host "Starting system from $ProjectRoot"

# 1) Python venv
if (!(Test-Path "venv")) {
    py -3.11 -m venv venv
    .\venv\Scripts\python.exe -m pip install --upgrade pip
    .\venv\Scripts\pip.exe install -r requirements.txt
}

# 2) Node deps
if (!(Get-Command node -ErrorAction SilentlyContinue)) {
    throw "Node.js not found. Install Node.js 18+"
}
if (!(Test-Path "frontend\node_modules")) {
    Push-Location frontend
    npm install
    Pop-Location
}

# helper: kill process on port (Windows alternative to lsof)
function Stop-Port($port) {
    $pids = (netstat -ano | Select-String ":$port\s" | ForEach-Object {
        ($_ -split "\s+")[-1]
    }) | Sort-Object -Unique

    foreach ($pid in $pids) {
        if ($pid -match "^\d+$") {
            taskkill /PID $pid /F | Out-Null
        }
    }
}

# 3) Start agents (если у них фиксированные порты — иначе смотри их README/код)
# Пример: если агенты стартуют просто запуском .py (порты могут быть внутри кода)
$agentFiles = @(
  "agents\fundamental_analyst_server.py",
  "agents\technical_analyst_server.py",
  "agents\news_sentiment_analyst_server.py",
  "agents\macro_analyst_server.py",
  "agents\regulatory_analyst_server.py",
  "agents\predictor_agent_server.py"
)

New-Item -ItemType Directory -Force -Path "logs" | Out-Null

foreach ($f in $agentFiles) {
    if (Test-Path $f) {
        Start-Process -WindowStyle Hidden `
          -FilePath ".\venv\Scripts\python.exe" `
          -ArgumentList $f `
          -RedirectStandardOutput ("logs\" + (Split-Path $f -Leaf) + ".log") `
          -RedirectStandardError ("logs\" + (Split-Path $f -Leaf) + ".err")
    }
}

Start-Sleep -Seconds 5

# 4) Start backend (порт 8000 как в твоём .sh)
Stop-Port 8000
Start-Process -WindowStyle Hidden `
  -FilePath ".\venv\Scripts\python.exe" `
  -ArgumentList "frontend_api.py" `
  -RedirectStandardOutput "logs\fastapi.log" `
  -RedirectStandardError "logs\fastapi.err"

# 5) Start frontend (порт в скрипте 3001)
Stop-Port 3001
Push-Location frontend
Start-Process -WindowStyle Hidden `
  -FilePath "npm.cmd" `
  -ArgumentList "run","dev" `
  -RedirectStandardOutput "..\logs\nextjs.log" `
  -RedirectStandardError "..\logs\nextjs.err"
Pop-Location

Write-Host "Frontend: http://localhost:3001"
Write-Host "Backend:  http://localhost:8000"
