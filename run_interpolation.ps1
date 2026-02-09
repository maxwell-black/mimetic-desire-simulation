Set-Location $PSScriptRoot
$env:PYTHONUNBUFFERED = "1"
python self_exhaustion_interpolation.py | Tee-Object -FilePath interpolation.log
