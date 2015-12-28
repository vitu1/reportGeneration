#!/bin/bash

set -x
set -e

if [ $# -ne 1 ]; then
    echo "Usage: $0 WORK_DIR"
    exit 1
fi

WORK_DIR="$1"
SCRIPT_DIR="${HOME}/.virtualenvs/shotgun-pipeline/bin"

# make preprocess summary
"${SCRIPT_DIR}/preprocess_report.py" \
    --illqc-dir "${WORK_DIR}/summary" \
    --decontam-dir "${WORK_DIR}/summary" \
    --decontam-prefix summary-decontam_human_ \
    --output-fp "${WORK_DIR}/preprocess_summary.tsv"

# make fastqc reports
"${SCRIPT_DIR}/fastqc_report.py" \
    --input-dir "${WORK_DIR}/illqc_reports" \
    --output-dir "${WORK_DIR}"

# make taxonomic assignment table
"${SCRIPT_DIR}/build_results_table.py" \
    --input-dir "${WORK_DIR}/phyloprofiler_results" \
    --input-suffix _R1.txt \
    --output-fp "${WORK_DIR}/taxonomic_assignments.tsv"

# make gene content table
"${SCRIPT_DIR}/build_results_table.py" \
    --input-dir "${WORK_DIR}/pathfinder_results" \
    --input-suffix .ko \
    --output-fp "${WORK_DIR}/ko_assignments.tsv"