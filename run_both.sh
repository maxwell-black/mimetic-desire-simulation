#!/bin/bash
cd "$(dirname "$0")"

echo "Launching gap_trend_analysis.py and self_exhaustion_interpolation.py..."
echo ""

PYTHONUNBUFFERED=1 python gap_trend_analysis.py 2>&1 | tee gap_trend.log &
PID1=$!

PYTHONUNBUFFERED=1 python self_exhaustion_interpolation.py 2>&1 | tee interpolation.log &
PID2=$!

echo "gap_trend_analysis.py        PID=$PID1  log: gap_trend.log"
echo "self_exhaustion_interpolation.py  PID=$PID2  log: interpolation.log"
echo ""
echo "Monitor with:"
echo "  tail -f gap_trend.log"
echo "  tail -f interpolation.log"
echo ""
echo "Kill with:"
echo "  kill $PID1 $PID2"

wait
echo ""
echo "Both processes finished."
