Set-Location $PSScriptRoot
$env:PYTHONUNBUFFERED = "1"

$gap = Start-Process -PassThru -NoNewWindow -FilePath python -ArgumentList "gap_trend_analysis.py" -RedirectStandardOutput gap_trend.log -RedirectStandardError gap_trend_err.log
$interp = Start-Process -PassThru -NoNewWindow -FilePath python -ArgumentList "self_exhaustion_interpolation.py" -RedirectStandardOutput interpolation.log -RedirectStandardError interpolation_err.log

Write-Host ""
Write-Host "gap_trend_analysis.py            PID=$($gap.Id)  log: gap_trend.log"
Write-Host "self_exhaustion_interpolation.py  PID=$($interp.Id)  log: interpolation.log"
Write-Host ""
Write-Host "Monitor with:"
Write-Host "  Get-Content gap_trend.log -Wait"
Write-Host "  Get-Content interpolation.log -Wait"
Write-Host ""
Write-Host "Kill with:"
Write-Host "  Stop-Process -Id $($gap.Id)"
Write-Host "  Stop-Process -Id $($interp.Id)"
