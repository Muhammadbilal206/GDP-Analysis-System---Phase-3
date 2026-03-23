import dash
from dash import dcc, html
from dash.dependencies import Output, Input
import plotly.graph_objs as go
import queue

class DashboardApp:
    def __init__(self, telemetry, proc_q, proc_count):
        self.telemetry = telemetry
        self.proc_q = proc_q
        self.proc_count = proc_count
        self.app = dash.Dash(__name__)
        self.x_data, self.y_raw, self.y_avg = [], [], []
        self.setup_layout()

    def setup_layout(self):
        self.app.layout = html.Div([
            html.H1("Real-Time Pipeline Telemetry"),
            html.Div([
                html.Div(id='raw-indicator'),
                html.Div(id='proc-indicator')
            ]),
            dcc.Graph(id='live-graph'),
            dcc.Interval(id='interval-component', interval=500, n_intervals=0)
        ])

        @self.app.callback(
            [Output('raw-indicator', 'children'), Output('raw-indicator', 'style'),
             Output('proc-indicator', 'children'), Output('proc-indicator', 'style'),
             Output('live-graph', 'figure')],
            [Input('interval-component', 'n_intervals')]
        )
        def update(n):
            stats = self.telemetry.get_status()
            
            try:
                while not self.proc_q.empty():
                    d = self.proc_q.get_nowait()
                    if d is None: continue
                    with self.proc_count.get_lock():
                        if self.proc_count.value > 0: self.proc_count.value -= 1
                    
                    self.x_data.append(len(self.x_data))
                    self.y_raw.append(d['metric_value'])
                    self.y_avg.append(d['computed_metric'])
                    if len(self.x_data) > 50:
                        self.x_data.pop(0); self.y_raw.pop(0); self.y_avg.pop(0)
            except queue.Empty:
                pass

            def get_color(val, mx):
                if val / mx > 0.8: return '#ff6666'
                if val / mx > 0.5: return '#ffff66'
                return '#99ff99'

            raw_style = {'padding': '20px', 'display': 'inline-block', 'margin': '10px', 'backgroundColor': get_color(stats['raw'], stats['limit']), 'borderRadius': '5px'}
            proc_style = {'padding': '20px', 'display': 'inline-block', 'margin': '10px', 'backgroundColor': get_color(stats['proc'], stats['limit']), 'borderRadius': '5px'}

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=self.x_data, y=self.y_raw, mode='lines', name='Verified Raw'))
            fig.add_trace(go.Scatter(x=self.x_data, y=self.y_avg, mode='lines', name='Running Average'))

            return (
                f"Raw Stream (Input -> Core): {stats['raw']}/{stats['limit']}", raw_style,
                f"Processed Stream (Core -> Output): {stats['proc']}/{stats['limit']}", proc_style,
                fig
            )

    def run(self):
        self.app.run(debug=False, port=8050, use_reloader=False)
