#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ "${1:-}" == "--refresh-sources" ]]; then
    "${PYTHON:-python3}" "$PROJECT_ROOT/scripts/build_latex_report.py"
fi
cd "$PROJECT_ROOT/docs/report/latex"
latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=build main.tex
cp build/main.pdf "$PROJECT_ROOT/docs/report/latex/BTL2_L09_Nhom09_P1_P2.pdf"
cp build/main.pdf "$PROJECT_ROOT/docs/report/latex/main.pdf"
