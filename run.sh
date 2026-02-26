#! /bin/bash

TEST_RUNS=10
RESULTS_FOLDER="experiment_resuts"
CSV_HEADER="threads,hash bits,ms"

mkdir "$RESULTS_FOLDER"
mkdir "$RESULTS_FOLDER/concurrent"
mkdir "$RESULTS_FOLDER/countThenMove"
for thread in 1 2 4 8 16 32
do
    FILE_NAME="$RESULTS_FOLDER/concurrent/concurrent_${thread}t_timings.csv"
    touch "$FILE_NAME"
    echo "$CSV_HEADER" > "$FILE_NAME"
    for hash_bit in {1..18}
    do
        sum=0
        echo "Running tests for $thread threads and $hash_bit hash bits"
        for test_run in {0..9}
        do
            result=$(./out/main $thread $hash_bit 1 0 | grep -oE '[0-9]+')
            sum=$(($sum + $result))
            echo -e "\tTest $((test_run + 1)): $result ms"
        done
        mean=$(($sum / 10))
        echo -e "\tMean: $mean"
        echo "$thread,$hash_bit,$mean" >> "$FILE_NAME"
    done
done