param(
    [Parameter(Mandatory = $true)]
    [string]$SonarToken,

    [string]$SonarHostUrl = "http://localhost:9000",

    [string]$ScannerBat = "$HOME\Downloads\sonar-scanner-cli-8.0.1.6346-windows-x64\sonar-scanner-8.0.1.6346-windows-x64\bin\sonar-scanner.bat"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$runId = [guid]::NewGuid().ToString("N")
$tempRoot = Join-Path $repoRoot ".sonar_runs\$runId"
$stagingDir = Join-Path $tempRoot "repo"

New-Item -ItemType Directory -Path $stagingDir | Out-Null

$excludeDirs = @(
    ".git",
    ".sonar_tmp",
    ".sonar_runs",
    ".venv",
    ".pytest_tmp",
    ".pytest_cache",
    ".pytest_cache_local",
    ".scannerwork",
    "backend\.pytest_tmp",
    "backend\.pytest_cache",
    "backend\.pytest_cache_local",
    "frontend\node_modules",
    "frontend\dist"
)

$robocopyArgs = @(
    $repoRoot,
    $stagingDir,
    "/MIR",
    "/XD"
) + $excludeDirs + @(
    "/XF",
    "*.pyc",
    ".coverage",
    "/R:1",
    "/W:1",
    "/NFL",
    "/NDL",
    "/NJH",
    "/NJS"
)

& robocopy @robocopyArgs | Out-Null
if ($LASTEXITCODE -ge 8) {
    throw "Robocopy fallo al preparar la copia temporal para SonarQube."
}

$coverageReport = Join-Path $stagingDir "backend\coverage.xml"
if (Test-Path $coverageReport) {
    $coverageContent = Get-Content -LiteralPath $coverageReport -Raw
    $coverageContent = $coverageContent.Replace("<source>app</source>", "<source>backend/app</source>")
    Set-Content -LiteralPath $coverageReport -Value $coverageContent
}

$env:SONAR_HOST_URL = $SonarHostUrl
$env:SONAR_TOKEN = $SonarToken

Push-Location $stagingDir
try {
    & $ScannerBat
}
finally {
    Pop-Location
}
