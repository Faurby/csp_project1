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
    return (data_amount / (time / 1000) / 1_000_000)


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
    csv_files = glob.glob(os.path.join(experiment_path, "*_" + affinity + "_timings.csv"))

    for file in csv_files:
        df = pd.read_csv(file)

        # Extract thread value (same for entire file)
        thread_value = df["threads"].iloc[0]

        # Sort by hash bits to ensure proper lines
        df = df.sort_values("hash_bits")

        data[thread_value] = df

    return data


def compute_global_axis_limits(all_experiments_data, x_col, y_col):
    """Compute global x and y limits across all experiments."""
    all_x, all_y = [], []
    for data in all_experiments_data:
        for df in data.values():
            all_x.extend(df[x_col].dropna().tolist())
            all_y.extend(df[y_col].dropna().tolist())
    return (min(all_x), max(all_x)), (0, max(all_y))


def plot_experiment(experiment_info, data, data_scaler=None):
    plt.figure()

    for thread, df in sorted(data.items()):
        if data_scaler:
            df[data_scaler["label"]] = df[data_scaler["label"]] / data_scaler["factor"]

        plt.plot(
            df[experiment_info["x-axis"]],
            df[experiment_info["y-axis"]],
            marker=GRAPH_SHAPES[int(log2(thread))-1],
            label=f"{thread} threads"
        )

    if "xlim" in experiment_info:
        plt.xlim(experiment_info["xlim"])
    if "ylim" in experiment_info:
        plt.ylim(experiment_info["ylim"])

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

    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)

    for category in OUTPUT_CATEGORIES:
        if not os.path.exists(os.path.join(OUTPUT_DIR, category)):
            os.mkdir(os.path.join(OUTPUT_DIR, category))

    # First pass: load all data
    loaded = {}  # (exp, aff) -> data
    for exp in experiment_dirs:
        exp_path = os.path.join(BASE_DIR, exp)
        for aff in AFFINITIES:
            data = load_experiment_data(exp_path, aff)
            if data:
                loaded[(exp, aff)] = data

    # Group data by experiment name (ignoring affinity)
    exp_groups = {}  # exp -> list of data dicts
    for (exp, aff), data in loaded.items():
        exp_groups.setdefault(exp, []).append(data)

    # Compute per-experiment limits across all affinities
    exp_limits = {}
    for exp, data_list in exp_groups.items():
        throughput_xlim, throughput_ylim = compute_global_axis_limits(data_list, "hash_bits", "mean_tuples_per_sec_millions")
        tlb_xlim, tlb_ylim             = compute_global_axis_limits(data_list, "hash_bits", "mean_dtlb_misses")
        cache_xlim, cache_ylim         = compute_global_axis_limits(data_list, "hash_bits", "mean_cache_misses")

        exp_limits[exp] = {
            "throughput": (throughput_xlim, throughput_ylim),
            "tlb":        (tlb_xlim,        (0, tlb_ylim[1]   / 1_000_000)),
            "cache":      (cache_xlim,      (0, cache_ylim[1] / 1_000_000)),
        }

    # Second pass: plot using per-experiment limits
    for (exp, aff), data in loaded.items():
        lims = exp_limits[exp]

        plot_experiment(
            {
                "x-axis": "hash_bits",
                "y-axis": "mean_tuples_per_sec_millions",
                "x-label": "Hash Bits",
                "y-label": "Throughput [mil tuples/s]",
                "xlim": lims["throughput"][0],
                "ylim": lims["throughput"][1],
                "graph-title": f"Throughput vs Hash Bits|{exp}:{aff}",
                "output-path": os.path.join(OUTPUT_DIR, "throughput", exp + ":" + aff + ".png")
            },
            data
        )

        plot_experiment(
            {
                "x-axis": "hash_bits",
                "y-axis": "mean_dtlb_misses",
                "x-label": "Hash Bits",
                "y-label": "TLB Misses [mil misses]",
                "xlim": lims["tlb"][0],
                "ylim": lims["tlb"][1],
                "graph-title": f"TLB Misses vs Hash Bits|{exp}:{aff}",
                "output-path": os.path.join(OUTPUT_DIR, "tlb", exp + ":" + aff + ".png")
            },
            data,
            {"label": "mean_dtlb_misses", "factor": 1_000_000}
        )

        plot_experiment(
            {
                "x-axis": "hash_bits",
                "y-axis": "mean_cache_misses",
                "x-label": "Hash Bits",
                "y-label": "Cache Misses [mil misses]",
                "xlim": lims["cache"][0],
                "ylim": lims["cache"][1],
                "graph-title": f"Cache Misses vs Hash Bits|{exp}:{aff}",
                "output-path": os.path.join(OUTPUT_DIR, "cache", exp + ":" + aff + ".png")
            },
            data,
            {"label": "mean_cache_misses", "factor": 1_000_000}
        )

    # if loaded:
    #     plot_combined(loaded)

    print("Graphs generated successfully.")


if __name__ == "__main__":
    main()
