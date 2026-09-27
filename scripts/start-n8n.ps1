# Starts n8n configured for this project. Run from the repo root:
#   powershell -ExecutionPolicy Bypass -File scripts\start-n8n.ps1
# Then open http://localhost:5678

$Root = Split-Path -Parent $PSScriptRoot
$DataDir = Join-Path $Root "data"

# Load .env (NEWSAPI_KEY, optional) into this process only
$EnvFile = Join-Path $Root ".env"
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | Where-Object { $_ -match '^\s*[A-Za-z_][A-Za-z0-9_]*\s*=' } | ForEach-Object {
        $name, $value = $_ -split '=', 2
        [Environment]::SetEnvironmentVariable($name.Trim(), $value.Trim().Trim('"'), 'Process')
    }
    Write-Host "Loaded .env"
} else {
    Write-Host "No .env found - NewsAPI will be skipped (the other sources still run)."
}

$env:GROUNDLINE_DATA_DIR = $DataDir               # where the workflow writes files
$env:N8N_RESTRICT_FILE_ACCESS_TO = $DataDir       # n8n may only read/write inside data/
$env:N8N_BLOCK_ENV_ACCESS_IN_NODE = "false"       # lets the workflow read the two variables above
$env:N8N_DIAGNOSTICS_ENABLED = "false"

Write-Host "Data folder: $DataDir"
Write-Host "Starting n8n -> http://localhost:5678"
n8n start
