# Runs the pipeline headlessly (no browser): imports the workflow and executes it.
#   powershell -ExecutionPolicy Bypass -File scripts\run-pipeline.ps1
# Stop any running "n8n start" first - both use the same local database.

$Root = Split-Path -Parent $PSScriptRoot
$DataDir = Join-Path $Root "data"
$Workflow = Join-Path $Root "workflow\Salve_Agnel_A3_Workflow.json"

$EnvFile = Join-Path $Root ".env"
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | Where-Object { $_ -match '^\s*[A-Za-z_][A-Za-z0-9_]*\s*=' } | ForEach-Object {
        $name, $value = $_ -split '=', 2
        [Environment]::SetEnvironmentVariable($name.Trim(), $value.Trim().Trim('"'), 'Process')
    }
}

$env:GROUNDLINE_DATA_DIR = $DataDir
$env:N8N_RESTRICT_FILE_ACCESS_TO = $DataDir
$env:N8N_BLOCK_ENV_ACCESS_IN_NODE = "false"
$env:N8N_DIAGNOSTICS_ENABLED = "false"

n8n import:workflow --input="$Workflow"
n8n execute --id=GroundlineA3Pipe
Write-Host "`nDone. Results in $DataDir\clean"
