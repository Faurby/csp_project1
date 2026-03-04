import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
from math import log2
"""
This is like 90% chatGPT code btw
"""

BASE_DIR = "experiment_results"
GRAPH_SHAPES = [".", "o", "v", "s", "*", "p"]

def calculateThroughput(time): 
    """
    Calculate the throughput based on the total number of tuples and the execution time.

    Args:
        time (int): The execution time in ms.

    Returns:
        throughput (float): Million Touples pr secound
    """
    
    data_amount = 2**24
    return (data_amount/(time/1000)/1_000_000)
    
def createThoughputColumn(dataframe):
    dataframe["throughput"] = calculateThroughput(dataframe["mean[ms]"])

def load_experiment_data(experiment_path):
    """
    Loads all CSV files for one experiment.
    Returns a dictionary:
    {
        thread_count: DataFrame(sorted by hash bits)
    }
    """
    data = {}
    csv_files = glob.glob(os.path.join(experiment_path, "*.csv"))

    for file in csv_files:
        df = pd.read_csv(file)

        # Extract thread value (same for entire file)
        thread_value = df["threads"].iloc[0]

        # Sort by hash bits to ensure proper lines
        df = df.sort_values("hash bits")

        data[thread_value] = df

    return data


def plot_experiment(experiment_name, data):
    """Graph 1: Lines per thread for a single experiment"""
    plt.figure()

    for thread, df in sorted(data.items()):
        createThoughputColumn(df)
        plt.plot(
            df["hash bits"],
            df["throughput"],
            marker=GRAPH_SHAPES[int(log2(thread))-1],
            label=f"{thread} threads"
        )

    plt.xlabel("Hash Bits")
    plt.ylabel("Throughput [mil tuples/s]")
    plt.title(f"Throughput vs Hash Bits - {experiment_name}")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{experiment_name}_plot.png")
    plt.close()


def plot_combined(all_experiments):
    """
    Graph 2: Combined comparison.
    Each line = experiment + thread
    """
    plt.figure()

    for experiment_name, data in all_experiments.items():
        for thread, df in data.items():
            plt.plot(
                df["hash bits"],
                calculateThroughput(df["mean[ms]"]),
                marker=GRAPH_SHAPES[int(log2(thread))-1],
                label=f"{experiment_name} - {thread}t"
            )

    plt.xlabel("Hash Bits")
    plt.ylabel("Throughput [mil tuples/s]")
    plt.title("Throughput vs Hash Bits (All Experiments)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("combined_plot.png")
    plt.close()


def main():
    experiment_dirs = [
        d for d in os.listdir(BASE_DIR)
        if os.path.isdir(os.path.join(BASE_DIR, d))
    ]

    all_experiments = {}

    for exp in experiment_dirs:
        exp_path = os.path.join(BASE_DIR, exp)
        data = load_experiment_data(exp_path)

        if data:
            all_experiments[exp] = data
            plot_experiment(exp, data)

    if all_experiments:
        plot_combined(all_experiments)

    print("Graphs generated successfully.")


if __name__ == "__main__":
    main()