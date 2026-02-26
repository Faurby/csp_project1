#! /bin/bash

# Over all constants 
TEST_RUNS=4
ALGORITHMS=(1 2)
ALGORITHMS_NAME=("concurrent" "countThenMove")
RESULTS_FOLDER="experiment_resuts"

CSV_HEADER="threads,hash bits,mean[ms]"


mkdir "$RESULTS_FOLDER"
for algo in 0 1
do
    mkdir "$RESULTS_FOLDER/${ALGORITHMS_NAME[$algo]}"
    for thread in 1 2 4 8 16 32
    do
        # Create csv file for a given number of threads
        FILE_NAME="$RESULTS_FOLDER/${ALGORITHMS_NAME[$algo]}/${ALGORITHMS_NAME[$algo]}_${thread}t_timings.csv"
        touch "$FILE_NAME"

        # Set the header
        echo -n "$CSV_HEADER" > "$FILE_NAME"
        for i in $(seq 1 $TEST_RUNS)
        do
            echo -n ",run$i[ms]" >> "$FILE_NAME"
        done
        echo "" >> "$FILE_NAME"


        for hash_bit in {1..18}
        do
            # Run TEST_RUNS number of run for pr params and save results 
            runs={1..$TEST_RUNS}
            echo "==== Running tests for ${ALGORITHMS_NAME[$algo]} at $thread threads and $hash_bit hash bits ===="
            for test_run in $(seq 1 $TEST_RUNS)
            do
                result=$(./out/main $thread $hash_bit $ALGORITHMS[algo] 0 | grep -oE '[0-9]+')
                runs[$(($test_run - 1))]=$result
                echo -e "\tTest $test_run: $result ms"
            done

            # Calculate mean of runs
            sum=0
            for run_time in ${runs[@]}
            do
                sum=$(($sum + $run_time))
            done
            mean=$(($sum / $TEST_RUNS))

            # Write results to file
            echo -e "\tMean: $mean"
            echo -n "$thread,$hash_bit,$mean" >> "$FILE_NAME"
            for run_time in ${runs[@]}
            do
                echo -n ",$run_time" >> "$FILE_NAME"
            done
            echo "" >> "$FILE_NAME"
        done
    done
done