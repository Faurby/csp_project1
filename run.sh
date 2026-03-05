#! /bin/bash

# Force C locale so awk/printf always use . as decimal separator
export LC_ALL=C
export LC_NUMERIC=C

TEST_RUNS=10
ALGORITHMS=(1 2)
ALGORITHMS_NAME=("concurrent" "countThenMove")
AFFINITIES=("none" "scatter" "compact")
RESULTS_FOLDER="experiment_results"
INPUT_TUPLES=$((1 << 24))

# dTLB-load-misses is the most relevant metric for partitioning since
# we care about output writes causing TLB misses, not instruction fetches
PERF_EVENTS="dTLB-load-misses,cache-misses"

CSV_HEADER="threads,hash_bits,affinity,mean_ms,mean_tuples_per_sec_millions,mean_dtlb_misses,mean_dtlb_misses_per_tuple,mean_cache_misses,mean_cache_misses_per_tuple"

compute_mean() {
    local arr=("$@")
    echo "${arr[@]}" | tr ' ' '\n' | awk '{s+=$1} END {if (NR>0) printf "%.2f", s/NR; else print 0}'
}

parse_perf_event() {
    local perf_output="$1"
    local event_name="$2"
    echo "$perf_output" \
        | grep -E "^\s+[0-9,].*${event_name}" \
        | head -1 \
        | grep -oE '^[[:space:]]*[0-9,]+' \
        | tr -d ' ,'
}

for algo in 0 1
do
    mkdir -p "$RESULTS_FOLDER/${ALGORITHMS_NAME[$algo]}"

    for thread in 1 2 4 8 16 32
    do
        for affinity_index in 0 1 2
        do
            affinity=${AFFINITIES[$affinity_index]}
            FILE_NAME="$RESULTS_FOLDER/${ALGORITHMS_NAME[$algo]}/${ALGORITHMS_NAME[$algo]}_${thread}t_${affinity}_timings.csv"

            header="$CSV_HEADER"
            for i in $(seq 1 $TEST_RUNS)
            do
                header+=",run${i}_ms,run${i}_dtlb_misses,run${i}_cache_misses"
            done
            echo "$header" > "$FILE_NAME"

            for hash_bit in $(seq 1 18)
            do
                echo "==== ${ALGORITHMS_NAME[$algo]} | threads=$thread | hash_bits=$hash_bit | affinity=$affinity ===="

                # Warm-up run
                ./out/main $thread $hash_bit ${ALGORITHMS[$algo]} $affinity > /dev/null 2>&1

                run_ms=()
                run_dtlb=()
                run_cache=()

                for test_run in $(seq 1 $TEST_RUNS)
                do
                    perf_output=$(perf stat \
                        -e "$PERF_EVENTS" \
                        ./out/main $thread $hash_bit ${ALGORITHMS[$algo]} $affinity \
                        2>&1 1>/dev/null)

                    timing_ms=$(./out/main $thread $hash_bit ${ALGORITHMS[$algo]} $affinity \
                        2>/dev/null | grep -oE '[0-9]+(\.[0-9]+)?' | head -1)

                    dtlb=$(parse_perf_event  "$perf_output" "dTLB-load-misses"); dtlb=${dtlb:-0}
                    cache=$(parse_perf_event "$perf_output" "cache-misses");     cache=${cache:-0}
                    timing_ms=${timing_ms:-0}

                    run_ms+=($timing_ms)
                    run_dtlb+=($dtlb)
                    run_cache+=($cache)

                    echo -e "\tRun $test_run: ${timing_ms}ms | dTLB-misses=${dtlb} | cache-misses=${cache}"
                done

                mean_ms=$(compute_mean    "${run_ms[@]}")
                mean_dtlb=$(compute_mean  "${run_dtlb[@]}")
                mean_cache=$(compute_mean "${run_cache[@]}")

                mean_dtlb_per_tuple=$( awk "BEGIN {printf \"%.6f\", $mean_dtlb  / $INPUT_TUPLES}")
                mean_cache_per_tuple=$(awk "BEGIN {printf \"%.6f\", $mean_cache / $INPUT_TUPLES}")

                mean_tups_per_sec=$(awk "BEGIN {
                    if ($mean_ms > 0) printf \"%.4f\", ($INPUT_TUPLES / $mean_ms) * 1000 / 1000000
                    else print 0
                }")

                echo -e "\tMean: ${mean_ms}ms | ${mean_tups_per_sec}M tuples/sec"
                echo -e "\tdTLB misses/tuple:  ${mean_dtlb_per_tuple}"
                echo -e "\tCache misses/tuple: ${mean_cache_per_tuple}"

                row="$thread,$hash_bit,$affinity,$mean_ms,$mean_tups_per_sec"
                row+=",${mean_dtlb},${mean_dtlb_per_tuple}"
                row+=",${mean_cache},${mean_cache_per_tuple}"

                for i in $(seq 0 $(($TEST_RUNS - 1)))
                do
                    row+=",${run_ms[$i]},${run_dtlb[$i]},${run_cache[$i]}"
                done

                echo "$row" >> "$FILE_NAME"
            done
        done
    done
done
