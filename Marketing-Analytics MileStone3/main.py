from importlib import import_module
from urllib import parse

import dash
import flask_jwt_extended
from dash import dcc, html

import authentication

# Import homepage and authentication package
import index
from app import app, config
from basic_page.layout import layout as main_layout

# Main layout
params = {}
app.layout = main_layout(params)



if __name__ == "__main__":
    app.run_server(debug=False, host='0.0.0.0', port = 8080)

