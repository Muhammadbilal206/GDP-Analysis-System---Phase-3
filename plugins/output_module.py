import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from queue import Empty

class LiveVisualizer:
    def __init__(self, config_data, q_in, monitor):
        self.settings = config_data
        self.q_in = q_in
        self.monitor = monitor
        self.monitor.register(self)

        self.times = []
        self.raw_vals = []
        self.avg_vals = []
        self.finished = False

        self.q_status = {"raw": 0, "verified": 0, "processed": 0}
        self.capacity = monitor.capacity

    def refresh_telemetry(self, status):
        self.q_status = status

    def launch(self):
        chart_cfg = self.settings["visualizations"]["data_charts"]
        tel_cfg = self.settings["visualizations"]["telemetry"]

        fig = plt.figure(figsize=(15, 9))
        fig.suptitle("Live Data Streams & System Health", fontsize=16, weight="heavy", color="darkblue")
        grid = fig.add_gridspec(2, 6, height_ratios=[1, 4], hspace=0.4, wspace=0.5)

        bars = []
        keys = []
        
        if tel_cfg.get("show_raw_stream"):
            bars.append((fig.add_subplot(grid[0, 0:2]), "Phase 1: Ingestion"))
            keys.append("raw")
        if tel_cfg.get("show_intermediate_stream"):
            bars.append((fig.add_subplot(grid[0, 2:4]), "Phase 2: Authentication"))
            keys.append("verified")
        if tel_cfg.get("show_processed_stream"):
            bars.append((fig.add_subplot(grid[0, 4:6]), "Phase 3: Aggregation"))
            keys.append("processed")

        plot_val = fig.add_subplot(grid[1, 0:3])
        plot_avg = fig.add_subplot(grid[1, 3:6])

        def refresh_frame(frame_idx):
            self.monitor.trigger_update()

            if not self.finished:
                for _ in range(3):
                    try:
                        item = self.q_in.get_nowait()
                    except Empty:
                        break

                    if item is None:
                        self.finished = True
                        break

                    self.times.append(item[chart_cfg[0]["x_axis"]])
                    self.raw_vals.append(item[chart_cfg[0]["y_axis"]])
                    self.avg_vals.append(item[chart_cfg[1]["y_axis"]])

            for idx, (ax, title) in enumerate(bars):
                self._render_bar(ax, title, self.q_status.get(keys[idx], 0))

            self._render_plot(plot_val, chart_cfg[0]["title"], self.times, self.raw_vals, "indigo")
            self._render_plot(plot_avg, chart_cfg[1]["title"], self.times, self.avg_vals, "teal")

        self.animation = FuncAnimation(fig, refresh_frame, interval=150, cache_frame_data=False)
        plt.show()

    def _render_bar(self, ax, title, count):
        ax.clear()
        fill_pct = count / self.capacity if self.capacity > 0 else 0

        bar_color = "teal" if fill_pct < 0.4 else "goldenrod" if fill_pct < 0.75 else "crimson"

        ax.barh([0], [1.0], color="whitesmoke", height=0.6)
        ax.barh([0], [fill_pct], color=bar_color, height=0.6)
        ax.set_xlim(0, 1)
        ax.set_title(title, fontsize=11, weight="bold", color="darkslategray")
        ax.axis("off")
        ax.text(0.5, 0, f"{count} / {self.capacity}", ha="center", va="center", fontsize=10, weight="bold")

    def _render_plot(self, ax, title, x_arr, y_arr, col):
        ax.clear()
        if x_arr and y_arr:
            ax.plot(x_arr, y_arr, lw=1.8, color=col)
        ax.set_title(title, fontsize=12, weight="bold")
        ax.set_xlabel("Time (Ticks)")
        ax.set_ylabel("Recorded Value")
        ax.grid(True, ls="--", alpha=0.5)
        ax.tick_params(axis="x", rotation=45, labelsize=9)
