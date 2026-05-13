import pandas as pd
import matplotlib.pyplot as plt
import os

CSV_PATH = "results.csv"
OUTPUT_DIR = "GPU_results"

METRIC_LABELS = {
    "avg_htod_ms":  ("Avg Host-to-Device Transfer Time", "Time [ms]"),
    "avg_exec_ms":  ("Avg Execution Time",               "Time [ms]"),
    "avg_dtoh_ms":  ("Avg Device-to-Host Transfer Time", "Time [ms]"),
    "avg_pwr":      ("Avg Power",                        "Power [W]"),
    "avg_gtemp":    ("Avg GPU Temperature",              "Temperature [°C]"),
    "avg_sm":       ("Avg SM Utilization",               "Utilization [%]"),
    "avg_mem":      ("Avg Memory Utilization",           "Utilization [%]"),
    "avg_mclk":     ("Avg Memory Clock",                 "Clock [MHz]"),
    "avg_pclk":     ("Avg Processor Clock",              "Clock [MHz]"),
}

TIMING_METRICS = ["avg_htod_ms", "avg_exec_ms", "avg_dtoh_ms"]

TIMING_COLORS = {
    "avg_htod_ms": "steelblue",
    "avg_exec_ms": "darkorange",
    "avg_dtoh_ms": "seagreen",
    "accumulated": "crimson",
}

TIMING_DISPLAY = {
    "avg_htod_ms": "Host-to-Device",
    "avg_exec_ms": "Execution",
    "avg_dtoh_ms": "Device-to-Host",
    "accumulated": "Accumulated Total",
}


def parse_graph_size(s):
    s = str(s).strip()
    if s.endswith('M'):
        return int(s[:-1]) * 1_000_000
    return int(s)


def plot_standalone_timings(df, output_dir):
    """Plot each timing metric as its own figure."""
    for metric in TIMING_METRICS:
        if metric not in df.columns:
            continue
        subset = df[["graph_size", metric]].dropna().copy()
        if subset.empty:
            continue

        title, ylabel = METRIC_LABELS[metric]
        fig, ax = plt.subplots()
        ax.plot(
            subset["graph_size"] / 1_000_000,
            subset[metric],
            marker="o",
            color=TIMING_COLORS[metric],
            label=TIMING_DISPLAY[metric],
        )
        ax.set_xlabel("Graph Size [millions of nodes]")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.set_ylim(bottom=0)
        ax.legend()
        ax.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"{metric}.png"))
        plt.close()


def plot_combined_timings(df, output_dir):
    """Plot all three timing metrics + accumulated total on one figure."""
    timing_cols = [m for m in TIMING_METRICS if m in df.columns]
    subset = df[["graph_size"] + timing_cols].dropna().copy()
    if subset.empty:
        return

    subset["accumulated"] = subset[timing_cols].sum(axis=1)

    fig, ax = plt.subplots()
    for metric in timing_cols:
        ax.plot(
            subset["graph_size"] / 1_000_000,
            subset[metric],
            marker="o",
            color=TIMING_COLORS[metric],
            label=TIMING_DISPLAY[metric],
        )

    ax.plot(
        subset["graph_size"] / 1_000_000,
        subset["accumulated"],
        marker="o",
        color=TIMING_COLORS["accumulated"],
        linestyle="--",
        linewidth=2,
        label=TIMING_DISPLAY["accumulated"],
    )

    ax.set_xlabel("Graph Size [millions of nodes]")
    ax.set_ylabel("Time [ms]")
    ax.set_title("GPU Timing Breakdown")
    ax.set_ylim(bottom=0)
    ax.legend()
    ax.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "timing_combined.png"))
    plt.close()


def plot_other_metrics(df, output_dir):
    """Plot all non-timing metrics as standalone figures."""
    other_metrics = [c for c in df.columns if c not in TIMING_METRICS and c != "graph_size"]
    for metric in other_metrics:
        subset = df[["graph_size", metric]].dropna().copy()
        if subset.empty:
            continue

        title, ylabel = METRIC_LABELS.get(metric, (metric, metric))
        fig, ax = plt.subplots()
        ax.plot(subset["graph_size"] / 1_000_000, subset[metric], marker="o")
        ax.set_xlabel("Graph Size [millions of nodes]")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.set_ylim(bottom=0)
        ax.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"{metric}.png"))
        plt.close()


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    df = pd.read_csv(CSV_PATH)
    df["graph_size"] = df["graph_size"].apply(parse_graph_size)
    df = df.sort_values("graph_size").reset_index(drop=True)

    plot_standalone_timings(df, OUTPUT_DIR)
    plot_combined_timings(df, OUTPUT_DIR)
    plot_other_metrics(df, OUTPUT_DIR)

    print("Graphs generated successfully.")


if __name__ == "__main__":
    main()
