$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
[System.Environment]::SetEnvironmentVariable('ACRO_TD_THEME_MANAGER', $ScriptDir, 'User')
$env:ACRO_TD_THEME_MANAGER = $ScriptDir
Write-Host "ACRO_TD_THEME_MANAGER set to $ScriptDir"
