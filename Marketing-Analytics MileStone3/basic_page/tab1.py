from lib2to3.pgen2.pgen import DFAState
import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.express as px
from regex import P
import utils
import pandas as pd
import dash
import numpy as np
from statsmodels.stats.power import TTestIndPower
import chart_studio.plotly as py
from dash.dependencies import Input, Output, State
from app import app
import plotly
import plotly.tools as tls
import plotly.figure_factory as ff




def playminutes(data):
  data['playminutes_integers'] = round(data['playminutes'])
  fig = px.bar(data, x='playminutes_integers', y='userid')
  return fig
var = pd.DataFrame()
#playminutes(var.df)

def layout1(data):
    global var
    if not data.empty:
       var = data.copy()
    items = [
    dbc.DropdownMenuItem("Time spent in Website",id = "playminutes_integers"),
    dbc.DropdownMenuItem("The distribution of the users", id = "dist_user"),
    dbc.DropdownMenuItem("Difference",id = "boot_mean"),
    dbc.DropdownMenuItem("7 Day Density of Effect",id = "dens_treat_effect_day7"),
    dbc.DropdownMenuItem("1st day Density of Effect",id = 'dens_treat_effect_day1'),
    dbc.DropdownMenuItem("1st Day Conversion Rate",id = 'conv_rate_day1'),
    dbc.DropdownMenuItem("Conversion Rate of 7 days",id = 'conv_rate_day7'),
    dbc.DropdownMenuItem("Cost by Groups",id = "cost_group")


    ]
    return  dbc.Row([
                    html.Div([
                        dbc.Row(id = 'hidden-div2',style = {'display':'none'}),
                        dbc.Col([
                            dbc.Label("Choose Visualisation from menu"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.DropdownMenu(items,
                                                        label = 'Menu',
                                                        color = '#034309', 
                                                        className = 'm-1'),
                                ],
                                style = {'width' : '70%', 'margin-top' : '10px', 'margin-bottom' : '10px'}),
                            ]),
                            
                                    # Block 4
                                    
                            dbc.Col([
                                html.Div([
                                    html.H3('Tab content 2'),
                                    dcc.Graph(
                                        id='graph-1-tabs-dcc',

                                    )
                                ])
                            ]),

                        ]),
                    ])
    ])

@app.callback(Output('graph-1-tabs-dcc','figure'),
			[Input('playminutes_integers','n_clicks'),
            Input('dist_user','n_clicks'),
            Input('boot_mean',"n_clicks"),
            Input('dens_treat_effect_day1','n_clicks'),
            Input('dens_treat_effect_day7','n_clicks'),
            Input('conv_rate_day1','n_clicks'),
            Input('conv_rate_day7','n_clicks'),
            Input('cost_group','n_clicks')


            ],
			)

def update_graph_gg(*args):
    global var
    if var.empty:
        return px.bar()
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = "all"
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    print(button_id)
    
    data = var.copy()
    if button_id == 'playminutes_integers':
        print("debug 1")
        print(data.head())
        data['playminutes_integers'] = round(data['playminutes'])
        fig = px.bar(data, x='playminutes_integers', y='userid',title = "minutes play", height = 400)
        return fig

    elif button_id == 'dist_user':
        print(data.head())
        data['playminutes_integers'] = round(data['playminutes'])
        plot_df = data.groupby('playminutes_integers')['userid'].count()
        ax = plot_df.head(n=50).plot(x="playminutes_integer", y="userid", kind="hist")
        return px.histogram(data, x ='playminutes_integers',nbins = 20,histnorm= 'probability density',title="Users distribution by playminutes" )
    elif button_id == 'boot_mean':
        
        boot_means = data.groupby('group')['playminutes'].mean()
        boot_means = pd.DataFrame(boot_means)
        return px.line(boot_means)
    elif button_id == 'dens_treat_effect_day7':
        boot_7d = []

        for i in range(100):
            boot_mean = data.sample(frac=1,replace=True).groupby('group')['day7'].mean() 
            boot_7d.append(boot_mean)
        boot_7d = pd.DataFrame(boot_7d)
        lst = []
        for each in boot_7d.columns:
            if each!='control':
                lst.append((boot_7d[each] - boot_7d['control'])/boot_7d['control'] *100)
        fig = ff.create_distplot(lst, group_labels = boot_7d.columns[1:],show_hist=False)
        fig.update_layout(title_text = "Density of 7 days active By treatment Groups")
        return fig
    elif button_id == 'dens_treat_effect_day1':
        boot_1d = []

        for i in range(100):
            boot_mean = data.sample(frac=1,replace=True).groupby('group')['day'].mean() 
            boot_1d.append(boot_mean)
        boot_1d = pd.DataFrame(boot_1d)
        lst = []
        for each in boot_1d.columns:
            if each!='control':
                lst.append((boot_1d[each] - boot_1d['control'])/boot_1d['control'] *100)
        fig = ff.create_distplot(lst, group_labels = boot_1d.columns[1:],show_hist=False)
        fig.update_layout(title_text = "Density of 1 day active By treatment Groups")
        return fig
    elif button_id == 'conv_rate_day1':
        fig = px.bar(x=data['group'],
             y=data['day'],
             color = data['group'],
             labels = {"group": "Group",
                       "day":"active"})
        fig.update_layout(title_text = "Congroup Rate 1 day")
        return fig
    elif button_id == 'conv_rate_day7':
        fig = px.bar(x=data['group'],
             y=data['day7'],
             color = data['group'],
             labels = {"group": "Group",
                       "day7":"active"})
        fig.update_layout(title_text = "Congroup Rate 7 days")
        return fig    
    elif button_id == 'cost_group':
       print( data.groupby('group')['cost'].max())
       return px.bar(x = data['group'].unique(), 
       y = data.groupby('group')['cost'].max(),
       color=data['group'].unique(),
       labels = {"x": "Group",
                       "y":"Cost"})
    else:
        data['playminutes_integers'] = round(data['playminutes'])
        fig = px.bar(data, x='playminutes_integers', y='userid',title = "minutes play", height = 400)
        
        return fig
    return px.bar()
