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


def parse_graph_size(s):
    s = str(s).strip()
    if s.endswith('M'):
        return int(s[:-1]) * 1_000_000
    return int(s)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    df = pd.read_csv(CSV_PATH)
    df["graph_size"] = df["graph_size"].apply(parse_graph_size)
    df = df.sort_values("graph_size").reset_index(drop=True)

    metrics = [c for c in df.columns if c != "graph_size"]

    for metric in metrics:
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
        plt.savefig(os.path.join(OUTPUT_DIR, f"{metric}.png"))
        plt.close()

    print("Graphs generated successfully.")


if __name__ == "__main__":
    main()
