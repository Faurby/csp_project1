import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os

GPU_CSV_PATH = "results-rx9070xt.csv"
CPU_CSV_PATH = "cpu_results.csv"
OUTPUT_DIR = "comparison_results"

TIMING_METRICS = ["avg_htod_ms", "avg_exec_ms", "avg_dtoh_ms"]


def parse_graph_size(s):
    s = str(s).strip()
    if s.endswith('M'):
        return int(s[:-1]) * 1_000_000
    return int(s)


def load_and_accumulate(csv_path):
    df = pd.read_csv(csv_path)
    df["graph_size"] = df["graph_size"].apply(parse_graph_size)
    df = df.sort_values("graph_size").reset_index(drop=True)

    timing_cols = [m for m in TIMING_METRICS if m in df.columns]
    df["accumulated"] = df[timing_cols].sum(axis=1)

    return df[["graph_size", "accumulated"]].dropna()


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    gpu_df = load_and_accumulate(GPU_CSV_PATH)
    cpu_df = load_and_accumulate(CPU_CSV_PATH)

    merged = pd.merge(gpu_df, cpu_df, on="graph_size", suffixes=("_gpu", "_cpu"))
    merged = merged.sort_values("graph_size").reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(
        gpu_df["graph_size"] / 1_000_000,
        gpu_df["accumulated"],
        marker="o",
        color="darkorange",
        label="GPU Accumulated Total",
    )

    ax.plot(
        cpu_df["graph_size"] / 1_000_000,
        cpu_df["accumulated"],
        marker="o",
        color="steelblue",
        label="CPU Accumulated Total",
    )

    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:g}M"))
    ax.xaxis.set_minor_formatter(ticker.NullFormatter())
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: f"{int(y)}ms"))
    ax.yaxis.set_minor_formatter(ticker.NullFormatter())

    ax.set_xlabel("Graph Size [millions of nodes]")
    ax.set_ylabel("Time [ms]")
    ax.set_title("GPU vs CPU Accumulated Total Time")
    ax.set_ylim(bottom=0)
    ax.legend()
    ax.grid(True, linestyle="--", linewidth=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "gpu_vs_cpu_accumulated.png"))
    plt.close()

    print("\nAccumulated totals (ms):")
    print(f"{'Graph Size':<15} {'GPU':>10} {'CPU':>10} {'Faster':>10}")
    print("-" * 47)
    for _, row in merged.iterrows():
        faster = "GPU" if row["accumulated_gpu"] < row["accumulated_cpu"] else "CPU"
        print(f"{int(row['graph_size'] / 1_000_000):>8}M       {row['accumulated_gpu']:>10.2f} {row['accumulated_cpu']:>10.2f} {faster:>10}")

    print("\nComparison graph generated successfully.")


if __name__ == "__main__":
    main()
