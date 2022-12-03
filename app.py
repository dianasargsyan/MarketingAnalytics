import base64
import os
from urllib.parse import quote as urlquote

from flask import Flask, send_from_directory
import dash
import pandas as pd
from turtle import width
import dash_bootstrap_components as dbc
from dash import dcc, html

from dash import html, dcc, Dash, dash_table
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objs as go
from statsmodels.stats.proportion import proportions_ztest, proportion_confint


# external CSS stylesheets
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app=Dash(__name__,
	external_stylesheets = external_stylesheets, suppress_callback_exceptions=True)
server=app.server

data = pd.read_csv("test1.csv")

# Barplot for visualizations
data['playminutes_integers'] = round(data['playminutes'])
barplot = px.bar(data, x='playminutes_integers', y='userid',title = "minutes play", height = 400)

# Histogram for visualizations
data['playminutes_integers'] = round(data['playminutes'])
plot_df = data.groupby('playminutes_integers')['userid'].count()
ax = plot_df.head(n=50).plot(x="playminutes_integer", y="userid", kind="hist")
histogram = px.histogram(data, x ='playminutes_integers',nbins = 20,histnorm= 'probability density',title="Users distribution by playminutes" )

#  Conversion Rate (1) for visualizations
conversionRate1 = px.bar(x=data['group'],
y=data['day'],
color = data['group'],
labels = {"group": "Group",
"day":"active"})

#Conversion Rate (7) for visualizations
conversionRate7 = px.bar(x=data['group'],
             y=data['day7'],
             color = data['group'],
             labels = {"group": "Group",
                       "day7":"active"})


#Gain for crosstable
d1 = pd.crosstab(data['group'],data['gain'])
d1.to_csv("a.csv")
d1 = pd.read_csv("a.csv")
columns = [{'name': col, 'id': col} for col in d1.columns.names]

gain = go.Figure(data=[go.Table(
	header=dict(values=list(d1.columns),
				fill_color='grey',
				align='left'),
	cells=dict(values=d1.transpose().values.tolist(),
			fill_color='lavender',
			align='left'))
])

#Day (1) for crosstable
d2 = pd.crosstab(data['group'],data['day'])
d2.to_csv("a.csv")
d2 = pd.read_csv("a.csv")
columns = [{'name': col, 'id': col} for col in d2.columns.names]

day1 = go.Figure(data=[go.Table(
	header=dict(values=list(d2.columns),
				fill_color='grey',
				align='left'),
	cells=dict(values=d2.transpose().values.tolist(),
			fill_color='lavender',
			align='left'))
])

#Day (7) for crosstable
d3 = pd.crosstab(data['group'],data['day7'])
d3.to_csv("a.csv")
d3 = pd.read_csv("a.csv")
columns = [{'name': col, 'id': col} for col in d3.columns.names]

day7 = go.Figure(data=[go.Table(
	header=dict(values=list(d3.columns),
				fill_color='grey',
				align='left'),
	cells=dict(values=d2.transpose().values.tolist(),
			fill_color='lavender',
			align='left'))
])

#Cost for crosstable
d4 = pd.crosstab(data['group'],data['cost'])
d4.to_csv("a.csv")
d4 = pd.read_csv("a.csv")
columns = [{'name': col, 'id': col} for col in d4.columns.names]

cost = go.Figure(data=[go.Table(
	header=dict(values=list(d4.columns),
				fill_color='grey',
				align='left'),
	cells=dict(values=d4.transpose().values.tolist(),
			fill_color='lavender',
			align='left'))
])


#Statitics Table python

list1 = []
for i in range(len(data['group'].unique())-1):
	control_results = data[data['group'] == 'control']['day']
	treatment1_results = data[data['group'] == f'treatment_{i+1}']['day']
	n_con = control_results.count()
	n_treat1 = treatment1_results.count()
	successes = [control_results.sum(), treatment1_results.sum()]
	nobs = [n_con, n_treat1]
	z_stat, pval = proportions_ztest(successes, nobs=nobs)

	list1.append(pval)
list2 = []
for i in range(len(data['group'].unique())-1):
	control_results = data[data['group'] == 'control']['day7']
	treatment1_results = data[data['group'] == f'treatment_{i+1}']['day7']
	n_con = control_results.count()
	n_treat1 = treatment1_results.count()
	successes = [control_results.sum(), treatment1_results.sum()]
	nobs = [n_con, n_treat1]
	z_stat, pval = proportions_ztest(successes, nobs=nobs)
	list2.append(pval)

list3 = []
for i in range(len(data['group'].unique())-1):
	treatment = f'Treatment group ' + str(i+1)
	list3.append(treatment)

dx = pd.DataFrame()
dx = pd.DataFrame(zip(list3, list1, list2))
dx.columns = ['group','day','day7']
dx.index = data['group'].unique()[1:]

app.layout=html.Div([
	html.Div([
		html.Div([
			html.H1('AB Testing Platform')
		], id = 'title')
	], className='twelve columns', id='titleFrame'),
	html.Div([
		dcc.Tabs(id='tabs', value='tab-1', children=[
			dcc.Tab(label='Visualization', value='vis-tab'),
			dcc.Tab(label='Statistics', value='statistics-tab'),
			dcc.Tab(label='Cross Table', value='cross-table-tab'),
    	]),
		html.Div(id='tabs-content-1')
	]),	 
], className='twelve columns', id='pageWrapper')
    
@app.callback(
    Output('tabs-content-1', 'children'),
    Input('tabs', 'value')
)

def render_content(tab):
    if tab == 'vis-tab':
        return  html.Div([
            html.Div([
				html.H4('Choose Visualization from menu'),
			], className = 'choose'),
			html.Div([
				dcc.Dropdown(['Time spent in Website', 'The distribution of the users', '1st Day Conversion Rate', '7th Day Conversion Rate'], 'Time spent in Website', id='vis-dropdown'),
				html.Div(id='dd-output-container'),
			], id='vis-tab-dropdown'),
        ], id='vis-tab')
    elif tab == 'statistics-tab':
        return html.Div([
			html.Div([
				 html.H4('Statistics of the treatment groups'),
			], className = 'choose'),
			dash_table.DataTable(
				id='stat_table',
				columns = [{
					'name': i ,
					'id' : i,
					'deletable': True,
						'renamable': True
				} for i,j in zip(dx.columns,dx.index)],
				
				data = [{
					i: dx[i][j] for i in dx.columns} 
				for j in range(dx.shape[0])],
				editable=True
            ),
        ], id='statistics-tab')
    elif tab == 'cross-table-tab':
        return html.Div([
			html.Div([
				 html.H4('Choose Cross table from menu'),
			], className = 'choose'),
            html.Div([
				dcc.Dropdown(['Gain', '1st Day Activity', '7 Day Activity', 'Cost'], 'Gain', id='cross-table-dropdown'),
				html.Div(id='dd-output-container2'),
			], id='cross-table-tab-dropdown'),
        ], id='cross-table-tab')
	
@app.callback(
    Output('dd-output-container', 'children'),
    Input('vis-dropdown', 'value'),
)
@app.callback(
    Output('dd-output-container2', 'children'),
    Input('cross-table-dropdown', 'value')
)

def update_output(value):
	if(value == 'Time spent in Website'):
		return html.Div([
			dcc.Graph(
            	figure= barplot
        	),
		], id='barplot', className='vis-graph')
	elif(value == 'The distribution of the users'):
		return html.Div([
			dcc.Graph(
            	figure= histogram
        	),
		], id='histogram', className='vis-graph')
	elif(value == '1st Day Conversion Rate'):
		return html.Div([
			dcc.Graph(
            	figure= conversionRate1
        	),
		], id='conversionRate1', className='vis-graph')
	elif(value == '7th Day Conversion Rate'):
		return html.Div([
			dcc.Graph(
            	figure= conversionRate7
        	),
		], id='conversionRate7', className='vis-graph')
	elif(value == 'Gain'):
		return html.Div([
			dcc.Graph(
            	figure= gain
        	),
		], id='gain', className='cross-graph')
	elif(value == '1st Day Activity'):
		return html.Div([
			dcc.Graph(
            	figure= day1
        	),
		], id='day1', className='cross-graph')
	elif(value == '7 Day Activity'):
		return html.Div([
			dcc.Graph(
            	figure= day7
        	),
		], id='day7', className='cross-graph')
	elif(value == 'Cost'):
		return html.Div([
			dcc.Graph(
            	figure= cost
        	),
		], id='cost', className='cross-graph')

if __name__=='__main__':
	app.run_server(debug=True)

