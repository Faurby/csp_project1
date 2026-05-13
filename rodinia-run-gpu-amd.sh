#!/bin/bash

RODINIA_PATH="$HOME/ITU/msc2/csprf/project2/gpu-rodinia"
BFS_PATH="$RODINIA_PATH/opencl/bfs"
OUTPUT_PATH="$HOME/ITU/msc2/csprf/project2"
DATA_PATH="$RODINIA_PATH/rodinia-data/bfs/benchmark"
RUNS=10
OUTPUT_FILE="$OUTPUT_PATH/results.csv"

# Sampling interval for rocm-smi polling (seconds)
SAMPLE_INTERVAL=0.1

cd "$BFS_PATH" || exit 1

echo ""
echo ""
echo "############# Starting AMD ROCm Experiment #############"

# Same CSV header as NVIDIA version
echo "graph_size,avg_htod_ms,avg_exec_ms,avg_dtoh_ms,avg_pwr,avg_gtemp,avg_sm,avg_mem,avg_mclk,avg_pclk" > "$OUTPUT_FILE"

# Poll rocm-smi metrics continuously
poll_gpu_metrics() {
    local outfile=$1

    while true; do
        rocm-smi \
            --showpower \
            --showtemp \
            --showuse \
            --showmemuse \
            --showmclk \
            --showclkfrq 2>/dev/null |
        awk -F': ' '
        /Average Graphics Package Power/ {
            pwr=$NF
            sub(/ .*/, "", pwr)
        }

        /Temperature \(Sensor edge\)/ {
            temp=$NF
        }

        /GPU use \(%\)/ {
            sm=$NF
        }

        /GPU Memory Read\/Write Activity \(%\)/ {
            mem=$NF
        }

        /Supported mclk frequencies/ { inmclk=1; next }
        /Supported sclk frequencies/ { insclk=1; next }

        inmclk && /\*/ {
            match($0, /[0-9]+Mhz/)
            mclk=substr($0, RSTART, RLENGTH)
            sub(/Mhz/, "", mclk)
            inmclk=0
        }

        insclk && /\*/ {
            match($0, /[0-9]+Mhz/)
            pclk=substr($0, RSTART, RLENGTH)
            sub(/Mhz/, "", pclk)
            insclk=0
        }

        END {
            if (pwr != "" && temp != "" && sm != "" && mem != "" && mclk != "" && pclk != "")
                print pwr","temp","sm","mem","mclk","pclk
        }' >> "$outfile"

        sleep "$SAMPLE_INTERVAL"
    done
}

avg_col() {
    awk '{ sum += $1; count++ } END { if (count > 0) printf "%.4f", sum/count }' "$1"
}

for datafile in "$DATA_PATH"/*
do
    BASENAME=$(basename "$datafile")
    EXEC_TMP=$(mktemp)
    HTOD_TMP=$(mktemp)
    DTOH_TMP=$(mktemp)
    GPU_TMP=$(mktemp)

    GRAPH_SIZE=$(echo "$BASENAME" | sed 's/graph\(.*\)\.txt/\1/')

    echo "-------------------------"
    echo "Warmup run for $BASENAME (size: $GRAPH_SIZE)..."
    ./bfs.out "$datafile" > /dev/null

    for ((test_run=1; test_run<=RUNS; test_run++))
    do
        echo "Run $test_run/$RUNS on $BASENAME ..."

        # Start polling GPU metrics
        poll_gpu_metrics "$GPU_TMP" &
        POLL_PID=$!

        # Run under rocprofv3
        BFS_OUTPUT=$(rocprofv3 -- ./bfs.out "$datafile" 2>/dev/null)

        # Stop polling
        kill $POLL_PID 2>/dev/null
        wait $POLL_PID 2>/dev/null

        # Extract benchmark timings
        echo "$BFS_OUTPUT" | awk '/^HtoD:/ { print $2 }' >> "$HTOD_TMP"
        echo "$BFS_OUTPUT" | awk '/^Exec:/ { print $2 }' >> "$EXEC_TMP"
        echo "$BFS_OUTPUT" | awk '/^DtoH:/ { print $2 }' >> "$DTOH_TMP"
    done

    echo "Finished $RUNS runs for $BASENAME"

    AVG_HTOD=$(avg_col "$HTOD_TMP")
    AVG_EXEC=$(avg_col "$EXEC_TMP")
    AVG_DTOH=$(avg_col "$DTOH_TMP")

    AVG_GPU=$(awk -F',' '
    {
        for (i=1; i<=NF; i++) sum[i] += $i
        count++
    }
    END {
        if (count > 0) {
            for (i=1; i<=NF; i++) {
                printf "%.4f", sum[i]/count
                if (i < NF) printf ","
            }
        }
    }' "$GPU_TMP")

    echo "${GRAPH_SIZE},${AVG_HTOD},${AVG_EXEC},${AVG_DTOH},${AVG_GPU}" >> "$OUTPUT_FILE"

    rm "$HTOD_TMP" "$EXEC_TMP" "$DTOH_TMP" "$GPU_TMP"
done

echo "-------------------------"
echo "############# Finished all runs. #############"
echo "Results written to $OUTPUT_FILE"
