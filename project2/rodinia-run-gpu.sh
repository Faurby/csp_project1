#!/bin/bash
RODINIA_PATH="$HOME/csprf/gpu-rodinia"
BFS_PATH="$RODINIA_PATH/opencl/bfs"
OUTPUT_PATH="$HOME/csprf"
DATA_PATH="$HOME/csprf/gpu-rodinia/rodinia-data/bfs/benchmark"
RUNS=10
OUTPUT_FILE="$OUTPUT_PATH/results.csv"

cd "$BFS_PATH" || exit 1

echo ""
echo ""
echo "############# Starting Experiment #############"

# Write header once
echo "graph_size,avg_htod_ms,avg_exec_ms,avg_dtoh_ms,avg_pwr,avg_gtemp,avg_sm,avg_mem,avg_mclk,avg_pclk" > "$OUTPUT_FILE"

for datafile in "$DATA_PATH"/*
do
        BASENAME=$(basename "$datafile")
        EXEC_TMP=$(mktemp)
        HTOD_TMP=$(mktemp)
        DTOH_TMP=$(mktemp)
        GPU_TMP=$(mktemp)

        # Extract graph size from filename e.g. graph8M.txt -> 8M
        GRAPH_SIZE=$(echo "$BASENAME" | sed 's/graph\(.*\)\.txt/\1/')

        # Warmup run (no monitoring, output discarded)
        echo "-------------------------"
        echo "Warmup run for $BASENAME (size: $GRAPH_SIZE) ..."
        ./bfs.out "$datafile" > /dev/null

        for ((test_run=1; test_run<=RUNS; test_run++))
        do
                echo "Run $test_run/$RUNS on $BASENAME ..."

                DMON_TMP_FILE=$(mktemp)
                nvidia-smi dmon -s puc > "$DMON_TMP_FILE" &
                DMON_PID=$!

                BFS_OUTPUT=$(./bfs.out "$datafile")
                echo "$BFS_OUTPUT" | awk '/^HtoD:/  { print $2 }' >> "$HTOD_TMP"
                echo "$BFS_OUTPUT" | awk '/^Exec:/  { print $2 }' >> "$EXEC_TMP"
                echo "$BFS_OUTPUT" | awk '/^DtoH:/  { print $2 }' >> "$DTOH_TMP"

                kill $DMON_PID
                wait $DMON_PID 2>/dev/null

                # Append per-run gpu metrics (skip 3-line dmon header)
                awk 'NR>3 && $6 > 5 { print $2","$3","$5","$6","$11","$12 }' "$DMON_TMP_FILE" >> "$GPU_TMP"
                rm "$DMON_TMP_FILE"
        done

        echo "Finished $RUNS runs for $BASENAME"

        avg_col() { awk '{ sum += $1; count++ } END { if (count > 0) printf "%.4f", sum/count }' "$1"; }

        AVG_HTOD=$(avg_col "$HTOD_TMP")
        AVG_EXEC=$(avg_col "$EXEC_TMP")
        AVG_DTOH=$(avg_col "$DTOH_TMP")

        # Average of each GPU metric column (pwr, gtemp, sm, mem, mclk, pclk)
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
