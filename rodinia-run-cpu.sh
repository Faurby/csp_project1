#!/bin/bash
RODINIA_PATH="$HOME/csprf/gpu-rodinia"
BFS_PATH="$RODINIA_PATH/opencl/bfs"
OUTPUT_PATH="$HOME/csprf"
DATA_PATH="$HOME/csprf/gpu-rodinia/rodinia-data/bfs/benchmark"
RUNS=10
OUTPUT_FILE="$OUTPUT_PATH/results_cpu.csv"

cd "$BFS_PATH" || exit 1

echo ""
echo ""
echo "############# Starting CPU Experiment #############"

# Write header once
echo "graph_size,avg_exec_ms" > "$OUTPUT_FILE"

for datafile in "$DATA_PATH"/*
do
        BASENAME=$(basename "$datafile")
        EXEC_TMP=$(mktemp)

        # Extract graph size from filename e.g. graph8M.txt -> 8M
        GRAPH_SIZE=$(echo "$BASENAME" | sed 's/graph\(.*\)\.txt/\1/')

        # Warmup run (output discarded)
        echo "-------------------------"
        echo "Warmup run for $BASENAME (size: $GRAPH_SIZE) ..."
        ./bfs.out -p 1 "$datafile" > /dev/null

        for ((test_run=1; test_run<=RUNS; test_run++))
        do
                echo "Run $test_run/$RUNS on $BASENAME ..."

                BFS_OUTPUT=$(./bfs.out -p 1 "$datafile")
                echo "$BFS_OUTPUT" | awk '/^Exec:/  { print $2 }' >> "$EXEC_TMP"
        done

        echo "Finished $RUNS runs for $BASENAME"

        avg_col() { awk '{ sum += $1; count++ } END { if (count > 0) printf "%.4f", sum/count }' "$1"; }

        AVG_EXEC=$(avg_col "$EXEC_TMP")

        echo "${GRAPH_SIZE},${AVG_EXEC}" >> "$OUTPUT_FILE"

        rm "$EXEC_TMP"
done

echo "-------------------------"
echo "############# Finished all runs. #############"
echo "Results written to $OUTPUT_FILE"