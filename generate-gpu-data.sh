#!/bin/bash
RODINIA_PATH="$HOME/csprf/gpu-rodinia"
BFS_PATH="$RODINIA_PATH/opencl/bfs"
DATA_PATH="$RODINIA_PATH/rodinia-data/bfs/benchmark"
GRAPHGEN_DIR="$RODINIA_PATH/rodinia-data/bfs/inputGen"
GRAPHGEN="$GRAPHGEN_DIR/graphgen"

mkdir -p "$DATA_PATH"

cd "$GRAPHGEN_DIR" || exit 1

# 1M to 10M: 1M steps
for ((i=1; i<=10; i++)); do
    NODES=$((i * 1048576))
    LABEL="${i}M"
    echo "Generating graph${LABEL}.txt ($NODES nodes)..."
    "$GRAPHGEN" $NODES $LABEL
done

# 12M to 32M: 2M steps
for ((i=12; i<=32; i+=4)); do
    NODES=$((i * 1048576))
    LABEL="${i}M"
    echo "Generating graph${LABEL}.txt ($NODES nodes)..."
    "$GRAPHGEN" $NODES $LABEL
done

# 36M to 64M: 4M steps
for ((i=36; i<=64; i+=8)); do
    NODES=$((i * 1048576))
    LABEL="${i}M"
    echo "Generating graph${LABEL}.txt ($NODES nodes)..."
    "$GRAPHGEN" $NODES $LABEL
done

# Move all generated files to benchmark folder
echo "Moving generated files to $DATA_PATH ..."
mv "$GRAPHGEN_DIR"/graph*.txt "$DATA_PATH"/

echo "Done. $(ls "$DATA_PATH"/graph*.txt | wc -l) graph files in $DATA_PATH"
