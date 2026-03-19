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
AFFINITIES = ["none", "scatter", "compact"]
OUTPUT_DIR = "graphs"
OUTPUT_CATEGORIES = ["throughput", "tlb", "cache"]

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

def load_experiment_data(experiment_path, affinity):
    """
    Loads all CSV files for one experiment.
    Returns a dictionary:
    {
        thread_count: DataFrame(sorted by hash bits)
    }
    """
    data = {}
    csv_files = glob.glob(os.path.join(experiment_path, "*_"+affinity+"_timings.csv"))

    for file in csv_files:
        df = pd.read_csv(file)

        # Extract thread value (same for entire file)
        thread_value = df["threads"].iloc[0]

        # Sort by hash bits to ensure proper lines
        df = df.sort_values("hash_bits")

        data[thread_value] = df

    return data


def plot_experiment_troughput(experiment_name, data):
    """Graph 1: Lines per thread for a single experiment"""
    plt.figure()

    for thread, df in sorted(data.items()):
        # createThoughputColumn(df)
        plt.plot(
            df["hash_bits"],
            df["mean_tuples_per_sec_millions"],
            marker=GRAPH_SHAPES[int(log2(thread))-1],
            label=f"{thread} threads"
        )

    plt.xlabel("Hash Bits")
    plt.ylabel("Throughput [mil tuples/s]")
    plt.title(f"Throughput vs Hash Bits - {experiment_name}")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "troughput", f"{experiment_name}_plot.png"))
    plt.close()

def plot_experiment_dtlb_misses(experiemnt_name, data):
    plt.figure()

    for thread, df in sorted(data.items()):
        plt.plot(
            df["hash_bits"],
            df["mean_dtlb_misses"],
            marker=GRAPH_SHAPES[int(log2(thread))-1],
            label=f"{thread} threads"
        )

    plt.xlabel("Hash Bits")
    plt.ylabel("TLB Misses")
    plt.title(f"TLB Misses vs Hash Bits - {experiemnt_name}")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "tlb", f"{experiemnt_name}_plot.png"))
    plt.close()

def plot_experiment(experiment_info, data):
    plt.figure()

    for thread, df in sorted(data.items()):
        plt.plot(
            df[experiment_info["x-axis"]],
            df[experiment_info["y-axis"]],
            marker=GRAPH_SHAPES[int(log2(thread))-1],
            label=f"{thread} threads"
        )

    plt.xlabel(experiment_info["x-label"])
    plt.ylabel(experiment_info["y-label"])
    plt.title(experiment_info["graph-title"])
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(experiment_info["output-path"])
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
                df["hash_bits"],
                df["mean_tuples_per_sec_millions"],
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
    
    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)
    
    for catagori in OUTPUT_CATEGORIES:
        if not os.path.exists(os.path.join(OUTPUT_DIR, catagori)):
            os.mkdir(os.path.join(OUTPUT_DIR, catagori))

    for exp in experiment_dirs:
        exp_path = os.path.join(BASE_DIR, exp)
        for aff in AFFINITIES:
            data = load_experiment_data(exp_path, aff)

            if data:
                all_experiments[exp + aff] = data
                
                # ==== Througput graph ====
                plot_experiment(
                    {
                        "x-axis": "hash_bits",
                        "y-axis": "mean_tuples_per_sec_millions",
                        "x-label": "Hash Bits",
                        "y-label": "Throughput [mil tuples/s]",
                        "graph-title": f"Throughput vs Hash Bits|{exp}:{aff}",
                        "output-path": os.path.join(OUTPUT_DIR, "throughput", exp+":"+aff+".png")
                    },  
                    data
                )

                plot_experiment(
                    {
                        "x-axis": "hash_bits",
                        "y-axis": "mean_dtlb_misses",
                        "x-label": "Hash Bits",
                        "y-label": "TLB Misses",
                        "graph-title": f"TLB Misses vs Hash Bits|{exp}:{aff}",
                        "output-path": os.path.join(OUTPUT_DIR, "tlb", exp+":"+aff+".png")
                    },
                    data
                )
                
                plot_experiment(
                    {
                        "x-axis": "hash_bits",
                        "y-axis": "mean_cache_misses",
                        "x-label": "Hash Bits",
                        "y-label": "Cache Misses",
                        "graph-title": f"Cache vs Hash Bits|{exp}:{aff}",
                        "output-path": os.path.join(OUTPUT_DIR, "cache", exp+":"+aff+".png")
                    },
                    data
                )

    # if all_experiments:
    #     plot_combined(all_experiments)

    print("Graphs generated successfully.")


if __name__ == "__main__":
    main()