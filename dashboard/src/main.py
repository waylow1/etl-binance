from dash import Dash, html, dcc, Output, Input, State
from dash_extensions import WebSocket
import plotly.graph_objs as go
import json
from collections import deque

app = Dash(__name__)

max_len = 50
times = deque(maxlen=max_len)
prices = deque(maxlen=max_len)

app.layout = html.Div([
    html.H1("Cours BTC/USDT en temps réel"),
    WebSocket(id="ws", url="ws://localhost:8000/ws/kafka"),
    dcc.Graph(id="live-graph"),
    dcc.Interval(id="interval", interval=1000, n_intervals=0)  
])

@app.callback(
    Output("live-graph", "figure"),
    Input("ws", "message"),
    State("live-graph", "figure")
)
def update_graph(message, existing_fig):
    if message is None:
        fig = go.Figure(data=[go.Scatter(x=[], y=[], mode='lines+markers')])
        fig.update_layout(title="Cours BTC/USDT")
        return fig
    
    data = json.loads(message["data"])
    price = float(data["price"])
    timestamp = int(data["timestamp"])

    from datetime import datetime
    time_str = datetime.fromtimestamp(timestamp / 1000).strftime("%H:%M:%S")

    times.append(time_str)
    prices.append(price)

    fig = go.Figure(
        data=[go.Scatter(x=list(times), y=list(prices), mode="lines+markers")],
        layout=go.Layout(title="Cours BTC/USDT en temps réel",
                         xaxis_title="Heure",
                         yaxis_title="Prix (USDT)",
                         yaxis=dict(range=[min(prices)*0.99, max(prices)*1.01]))
    )
    return fig

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
