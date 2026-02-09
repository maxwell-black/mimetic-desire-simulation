# Experiment Battery: Setup & Monitoring

## Claude Code Prompt

```
I have 5 Python experiment scripts in my Downloads folder that need to be moved
to my mimetic simulation repo (the folder containing girard_2x2_v3.py). The files are:

  exp1_ultralong_n500.py
  exp2_scaling_law.py
  exp3_param_sensitivity.py
  exp4_2x2_n200.py
  exp5_topology_n200.py

All import from girard_2x2_v3.py and must live in the same directory.

Please:
1. Move all 5 files from ~/Downloads/ to the repo directory.
2. Verify each one parses without syntax errors (python -c "import exp1_ultralong_n500" etc).
3. Tell me the result.
```

---

## PowerShell: Launch Each in a Separate Terminal

Save each block below as a .ps1 file, or just paste into separate PowerShell tabs.
Adjust `$repo` to your actual repo path.

### run_exp1.ps1
```powershell
$repo = "C:\Users\Max\path\to\mimetic-sim"  # <-- EDIT THIS
Set-Location $repo
python exp1_ultralong_n500.py 2>&1 | Tee-Object -FilePath exp1_ultralong_n500_results.txt
```

### run_exp2.ps1
```powershell
$repo = "C:\Users\Max\path\to\mimetic-sim"  # <-- EDIT THIS
Set-Location $repo
python exp2_scaling_law.py 2>&1 | Tee-Object -FilePath exp2_scaling_law_results.txt
```

### run_exp3.ps1
```powershell
$repo = "C:\Users\Max\path\to\mimetic-sim"  # <-- EDIT THIS
Set-Location $repo
python exp3_param_sensitivity.py 2>&1 | Tee-Object -FilePath exp3_param_sensitivity_results.txt
```

### run_exp4.ps1
```powershell
$repo = "C:\Users\Max\path\to\mimetic-sim"  # <-- EDIT THIS
Set-Location $repo
python exp4_2x2_n200.py 2>&1 | Tee-Object -FilePath exp4_2x2_n200_results.txt
```

### run_exp5.ps1
```powershell
$repo = "C:\Users\Max\path\to\mimetic-sim"  # <-- EDIT THIS
Set-Location $repo
python exp5_topology_n200.py 2>&1 | Tee-Object -FilePath exp5_topology_n200_results.txt
```

---

## Monitoring: Early Error Detection

All five scripts print per-seed progress with `flush=True`, so you can see
output in real time in each terminal tab. But if you want a single pane to
watch all of them at once, open a 6th PowerShell tab and run:

### monitor.ps1 -- tail all logs
```powershell
$repo = "C:\Users\Max\path\to\mimetic-sim"  # <-- EDIT THIS
Set-Location $repo

Write-Host "=== Waiting for log files to appear... ===" -ForegroundColor Yellow
Start-Sleep -Seconds 30

while ($true) {
    Clear-Host
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "=== EXPERIMENT MONITOR [$timestamp] ===" -ForegroundColor Cyan
    Write-Host ""

    foreach ($exp in @("exp1_ultralong_n500", "exp2_scaling_law", "exp3_param_sensitivity", "exp4_2x2_n200", "exp5_topology_n200")) {
        $file = "${exp}_results.txt"
        if (Test-Path $file) {
            $lines = Get-Content $file -Tail 3
            $lineCount = (Get-Content $file | Measure-Object -Line).Lines
            Write-Host "--- $exp ($lineCount lines) ---" -ForegroundColor Green
            $lines | ForEach-Object { Write-Host "  $_" }
        } else {
            Write-Host "--- $exp ---" -ForegroundColor Red
            Write-Host "  [not started yet]"
        }
        Write-Host ""
    }

    Start-Sleep -Seconds 60
}
```

---

## What to Check After 15-20 Minutes

After the scripts have been running ~15 min, glance at the monitor or
the individual terminal tabs and verify:

1. **exp1** (ultralong): Should show at least 1 seed completing for
   N=500 gamma=1.5. If you see a seed line with timing, it's working.
   If the first seed takes >2 hours with no output, something's wrong.

2. **exp2** (scaling): Should have finished N=50 and be into N=100.
   Look for the per-seed lines printing. If it's stuck on N=50 seed=42
   for >5 min, kill it.

3. **exp3** (sensitivity): Should be printing combo lines like
   `0.05  0.01  1.02  ...`. These go fast (~30s each). If no output
   after 5 min, something's wrong.

4. **exp4** (2x2 N=200): LM variant should finish fast (no convergence,
   low expulsions). If LM is still running after 30 min, problem.

5. **exp5** (topology): watts_strogatz should produce output first.
   If no seed lines after 10 min, problem.

**The key heuristic**: every script should produce its first seed-level
output line within 5-15 minutes. If any terminal is silent after 20 min,
kill it and check for import errors by running the script directly.

---

## Parallelism Notes

These are CPU-bound (no GPU). On a modern 8-core machine, running all 5
simultaneously will slow each by ~40-60% vs running alone. Expected wall
clock with all 5 parallel:

| Script | Solo estimate | With 5 parallel |
|--------|-------------|-----------------|
| exp1   | 10-15 hrs   | 16-24 hrs       |
| exp2   | 8-12 hrs    | 13-19 hrs       |
| exp3   | 6-8 hrs     | 10-13 hrs       |
| exp4   | 4-6 hrs     | 7-10 hrs        |
| exp5   | 3-5 hrs     | 5-8 hrs         |

If your machine only has 4 cores, consider running exp3+exp4+exp5 first
(they'll finish faster), then exp1+exp2 overnight.
