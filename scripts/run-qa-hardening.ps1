param(
    [switch]$Quick,

    [switch]$SkipSonar,

    [string]$SonarToken,

    [string]$SonarHostUrl = "http://localhost:9000",

    [string]$ScannerBat = "$HOME\Downloads\sonar-scanner-cli-8.0.1.6346-windows-x64\sonar-scanner-8.0.1.6346-windows-x64\bin\sonar-scanner.bat"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $repoRoot "backend"
$sonarScript = Join-Path $PSScriptRoot "run-sonar-local.ps1"
$qaRunId = [guid]::NewGuid().ToString("N")
$pytestTempRoot = Join-Path $repoRoot ".pytest_tmp_runs"

function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,

        [Parameter(Mandatory = $true)]
        [scriptblock]$Action
    )

    Write-Host ""
    Write-Host "==> $Name"
    & $Action
}

function Assert-LastExitCode {
    param(
        [Parameter(Mandatory = $true)]
        [string]$CommandName
    )

    if ($LASTEXITCODE -ne 0) {
        throw "$CommandName fallo con codigo de salida $LASTEXITCODE."
    }
}

function Invoke-PythonInBackend {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    Push-Location $backendDir
    try {
        & py @Arguments
        Assert-LastExitCode -CommandName ("py " + ($Arguments -join " "))
    }
    finally {
        Pop-Location
    }
}

function Get-PytestBaseTemp {
    if ($Quick) {
        return Join-Path $pytestTempRoot ("quick-" + $qaRunId)
    }

    return Join-Path $pytestTempRoot ("full-" + $qaRunId)
}

function Ensure-PytestTempRoot {
    if (-not (Test-Path $pytestTempRoot)) {
        New-Item -ItemType Directory -Path $pytestTempRoot | Out-Null
    }
}

if (-not (Test-Path $sonarScript)) {
    throw "No se encontro el script de SonarQube esperado en $sonarScript"
}

if ($Quick -and -not $SkipSonar) {
    $SkipSonar = $true
}

if ((-not $Quick) -and (-not $SkipSonar) -and [string]::IsNullOrWhiteSpace($SonarToken)) {
    throw "El flujo completo requiere -SonarToken o usar -SkipSonar si solo deseas validar localmente sin SonarQube."
}

Ensure-PytestTempRoot

Invoke-Step -Name "PyTest" -Action {
    $baseTemp = Get-PytestBaseTemp
    if ($Quick) {
        Invoke-PythonInBackend -Arguments @("-m", "pytest", "-m", "unit", "--basetemp", $baseTemp)
        return
    }

    Invoke-PythonInBackend -Arguments @("-m", "pytest", "--basetemp", $baseTemp)
}

if (-not $Quick) {
    Invoke-Step -Name "Cobertura" -Action {
        $baseTemp = Get-PytestBaseTemp
        Invoke-PythonInBackend -Arguments @(
            "-m",
            "pytest",
            "--basetemp",
            $baseTemp,
            "--cov=app",
            "--cov-config=.coveragerc",
            "--cov-report=term-missing",
            "--cov-report=xml"
        )
    }
}

Invoke-Step -Name "Pylint" -Action {
    Push-Location $repoRoot
    try {
        & py -m pylint --rcfile=backend/.pylintrc backend/app backend/run.py
        Assert-LastExitCode -CommandName "py -m pylint"
    }
    finally {
        Pop-Location
    }
}

Invoke-Step -Name "Bandit" -Action {
    Push-Location $repoRoot
    try {
        & py -m bandit -c backend/bandit.yaml -r backend/app
        Assert-LastExitCode -CommandName "py -m bandit"
    }
    finally {
        Pop-Location
    }
}

if ($SkipSonar) {
    Write-Host ""
    Write-Host "==> SonarQube omitido"
    if ($Quick) {
        Write-Host "Modo rapido completado: se omitieron cobertura y SonarQube."
    }
    else {
        Write-Host "Validacion local completada sin SonarQube. Usa -SonarToken para ejecutar el flujo completo."
    }
    exit 0
}

Invoke-Step -Name "SonarQube" -Action {
    & $sonarScript -SonarToken $SonarToken -SonarHostUrl $SonarHostUrl -ScannerBat $ScannerBat
    Assert-LastExitCode -CommandName "run-sonar-local.ps1"
}
