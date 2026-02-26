#!/bin/bash

# =============================================================================
# Benchmark script for ./out/main
# Sweeps hashbits 1-16 and threads 1/2/4/8/16/32 for both algorithms.
# Each config is run 10 times; mean and stddev are written to per-algo CSVs.
# =============================================================================

BINARY="./out/main"
CORE_AFFINITY=0
RUNS=10

ALGO_NAMES=("Concurrent" "CountThenMove")
CSV_HEADER="threads,hashbits,mean_ms,stddev_ms"

# --- Compute mean and stddev from a space-separated list of numbers ----------
mean_std() {
    echo "$@" | tr ' ' '\n' | awk '
        { sum += $1; sumsq += $1^2; n++ }
        END {
            mean = sum / n
            std  = sqrt(sumsq/n - mean^2)
            printf "%.2f,%.2f", mean, std
        }'
}

# =============================================================================

for algo in 1 2; do
    algo_name="${ALGO_NAMES[$algo-1]}"
    csv_file="results_${algo_name,,}.csv"   # lowercase filename
    echo "$CSV_HEADER" > "$csv_file"

    echo ""
    echo "============================="
    echo " Algorithm: $algo_name"
    echo "============================="

    for threads in 1 2 4 8 16 32; do
        for hashbits in $(seq 1 16); do
            echo "  threads=${threads} hashbits=${hashbits} ..."

            times=()
            for run in $(seq 1 "$RUNS"); do
                PROG_OUTPUT=$(perf stat \
                    "$BINARY" "$threads" "$hashbits" "$algo" "$CORE_AFFINITY" \
                    2>/dev/null)

                TIME_MS=$(echo "$PROG_OUTPUT" | grep -oP '\d+(?= ms)')
                times+=("$TIME_MS")
            done

            echo "${threads},${hashbits},$(mean_std "${times[@]}")" >> "$csv_file"
        done
    done

    echo "  Saved to $csv_file"
done

echo ""
echo "Done!"
