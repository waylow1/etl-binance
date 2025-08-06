from dash import Dash, html, dcc
from callbacks import register_callbacks
from layout import layout

app = Dash(__name__)
app.layout = layout

register_callbacks(app)

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
