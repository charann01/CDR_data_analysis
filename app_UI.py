# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 13:26:21 2020

@author: Charann A
"""
# Importing the required librarires
import pandas as pd
import webbrowser
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px
import dash_bootstrap_components as dbc
import dash_table as dt
import re

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

project_name = None 

# Loading the dataset and creating the required variables
def load_data():
    print("Start of the load_data function")

    call_dataset_name = "Call_data.csv" 
    service_dataset_name = "Service_data.csv"
    device_dataset_name = "Device_data.csv"
 
    global call_data, service_data, device_data
    
    call_data = pd.read_csv(call_dataset_name)
    service_data = pd.read_csv(service_dataset_name)
    device_data = pd.read_csv(device_dataset_name)
    
    global start_date_list
    temp_list = sorted (  call_data["date"].dropna().unique().tolist()  )
    start_date_list = [ { "label":str(i)    , "value":str(i)  }    for i in temp_list   ]
    
    global end_date_list
    temp_list = sorted (  call_data["date"].dropna().unique().tolist()  )
    end_date_list = [ { "label":str(i)    , "value":str(i)  }    for i in temp_list   ]
    
    global report_type
    temp_list = [ "Hourly", "Daywise", "Weekly"  ]
    report_type = [ { "label":str(i)    , "value":str(i)  }  for i in temp_list ]
    
    print("End of the load_data function")

# Opening the website
def open_browser():
    webbrowser.open_new("http://127.0.0.1:8050/")

# Creating the app's User Interface
def create_app_ui():
    main_layout = html.Div([
    
    html.H1('CDR Analysis with Insights', id='Main_title', style={ 'color': 'white', 'backgroundColor':'black', 'textAlign': 'center'}),
    
    # Creating the three tabs
    dcc.Tabs(id="Tabs", value="tab-1",children=[
    
    # Tab for the "Call Data Analysis"
    dcc.Tab(label="Call Data Analysis" ,id="Call Analytics tool",value="tab-1", children = [
    html.Br(),
    html.Br(),
    
    dcc.Dropdown(
          id='start-date-dropdown', 
          options=start_date_list,
          placeholder = "Select Starting Date here",
          value = "2019-06-20",
          
    ),
            
    dcc.Dropdown(
           id='end-date-dropdown', 
                  options=end_date_list,
                  placeholder = "Select Ending Date here",
                  value = "2019-06-25"
    ),
            
            
    dcc.Dropdown(
                  id='group-dropdown', 
                  placeholder = "Select group here",
                  multi = True
    ),
            
            
    dcc.Dropdown(
                  id='Report-type-dropdown', 
                  options=report_type,
                  placeholder = "Select Report Type",
                  value = "Hourly"
    )]),
  
    # Tab for the "Device Data Analysis"
    dcc.Tab(label = "Device Data Analysis", id="Device Analytics tool", value="tab-2", children = [            
    html.Br(),
    dcc.Dropdown(
      id='device-date-dropdown', 
      options=start_date_list,
      placeholder = "Select Date here",
      multi = True
        ), 
    html.Br()]),
  
    # Tab for the "Service Data Analysis"
    dcc.Tab(label = "Service Data Analysis", id="Service Analytics tool", value="tab-3", children = [            
    html.Br(),
    dcc.Dropdown(
      id='service-date-dropdown', 
      options=start_date_list,
      placeholder = "Select Date here",
      multi = True
        ), 
    html.Br()])
    ]),
    html.Br(),
    dcc.Loading(html.Div(id='visualization-object',children='Graph,Card, Table')),
    
    ])


    return main_layout

# Creating the cards 
def create_card(title, content, color):
    card = dbc.Card(
        dbc.CardBody(
            [
                html.H4(title), 
                html.Br(),
                html.Br(),
                html.H2(content), 
                html.Br(),
                ]
        ),
        color=color, inverse=True,
    )
    return(card)

# Counting the devices for pie chart
def device_count(data):
    
    device_dict = {"Polycom" :0, "Windows" : 0, "iphone" : 0, "Android" : 0, "Mac" : 0, "Yealink" : 0, "Aastra" : 0, "Others" : 0}
    
    reformed_data = data["UserDeviceType"].dropna().reset_index()
    for var in reformed_data["UserDeviceType"]:
        if re.search("Aastra", var):
            device_dict["Aastra"]+=1  
        elif re.search("Polycom", var) :
            device_dict["Polycom"]+=1   
        elif re.search("Windows", var):
            device_dict["Windows"]+=1
        elif re.search("Mac", var):
            device_dict["Mac"]+=1
        elif re.search("Yealink", var):
            device_dict["Yealink"]+=1
        elif re.search("Android", var):
            device_dict["Android"]+=1
        elif re.search("iPhone|iOS", var):
            device_dict["iphone"]+=1
        else:
            device_dict["Others"]+=1
    final_data = pd.DataFrame()
    final_data["Device"] = device_dict.keys()
    final_data["Count"] = device_dict.values()
    return final_data

@app.callback(
    Output('visualization-object', 'children'),
    [
    Input("Tabs", "value"),
    Input('start-date-dropdown', 'value'),
    Input('end-date-dropdown', 'value'),
    Input("group-dropdown", 'value'),
    Input('Report-type-dropdown', 'value'),
    Input('device-date-dropdown', 'value'),
    Input('service-date-dropdown', 'value')
    ]
    )

def update_app_ui(Tabs, start_date, end_date, group, report_type,device_date,service_date):
    
    print("Data Type of start_date value = " , str(type(start_date)))
    print("Data of start_date value = " , str(start_date))
    print("Data Type of end_date value = " , str(type(end_date)))
    print("Data of end_date value = " , str(end_date))
    print("Data Type of group value = " , str(type(group)))
    print("Data of group value = " , str(group))
    print("Data Type of report_type value = " , str(type(report_type)))
    print("Data of report_type value = " , str(report_type))
    print("Data Type of device_date value = " , str(type(device_date)))
    print("Data of device_date value = " , str(device_date))
    print("Data Type of service_date value = " , str(type(service_date)))
    print("Data of service_date value = " , str(service_date))

    # Tab - 1 "Call Data Analysis"
    if Tabs == "tab-1":
        call_analytics_data = call_data[ (call_data["date"]>=start_date) & (call_data["date"]<=end_date) ]   
        if group  == [] or group is None:
           pass
        else:
           call_analytics_data = call_analytics_data[call_analytics_data["Group"].isin(group)]

        graph_data = call_analytics_data    
        if report_type == "Hourly":
            graph_data = graph_data.groupby("hourly_range")["Call_Direction"].value_counts().reset_index(name = "count")
            x = "hourly_range"
            content = call_analytics_data["hourly_range"].value_counts().idxmax()
            title =  "Busiest Hour"
        elif report_type == "Daywise":
            graph_data = graph_data.groupby("date")["Call_Direction"].value_counts().reset_index(name = "count")
            x = "date"
            content = call_analytics_data["date"].value_counts().idxmax()
            title =  "Busiest Day"
        else:
            graph_data = graph_data.groupby("weekly_range")["Call_Direction"].value_counts().reset_index(name = "count")
            x = "weekly_range"
            content = call_analytics_data["weekly_range"].value_counts().idxmax()
            title =  "Busiest WeekDay"
            
        # Area graph for call data analysis 
        figure = px.area(graph_data, 
                         x = x, 
                         y = "count",
                         color = "Call_Direction",
                         hover_data=[ "Call_Direction", "count"], 
                         template = "plotly_dark"
                         )
        figure.update_traces(mode = "lines+markers")
      
        # Cards for insights about call data analysis
        total_calls = call_analytics_data["Call_Direction"].count()
        card_1 = create_card("Total Calls",total_calls, "primary")
        incoming_calls = call_analytics_data["Call_Direction"][call_analytics_data["Call_Direction"]=="Incoming"].count()
        card_2 = create_card("Incoming Calls", incoming_calls, "success")
        outgoing_calls = call_analytics_data["Call_Direction"][call_analytics_data["Call_Direction"]=="Outgoing"].count()
        card_3 = create_card("Outgoing Calls", outgoing_calls, "danger")
        missed_calls = call_analytics_data["Missed Calls"][call_analytics_data["Missed Calls"] == 3].count()
        card_4 = create_card("Missed Calls", missed_calls, "warning")
        max_duration = call_analytics_data["duration"].max()
        card_5 = create_card("Max Duration", f'{max_duration} min', "info")
        card_6 = create_card(title, content, "dark")
             
        graphRow0 = dbc.Row([dbc.Col(id='card1', children=[card_1], md=4, width={"offset": 2}), dbc.Col(id='card2', children=[card_2], md=4)])
        graphRow1 = dbc.Row([dbc.Col(id='card3', children=[card_3], md=4, width={"offset": 2}), dbc.Col(id='card4', children=[card_4], md=4)])
        graphRow2 = dbc.Row([dbc.Col(id='card5', children=[card_5], md=4, width={"offset": 2}), dbc.Col(id='card6', children=[card_6], md=4)])
     
        cardDiv = html.Div([graphRow0,html.Br(), graphRow1,html.Br(), graphRow2], style={})
        
        # Datatable for the call data analysis
        datatable_data = call_analytics_data.groupby(["Group", "UserID", "UserDeviceType"])["Call_Direction"].value_counts().unstack(fill_value = 0).reset_index()
        if call_analytics_data["Missed Calls"][call_analytics_data["Missed Calls"]==19].count()!=0:
            datatable_data["Missed Calls"] = call_analytics_data.groupby(["Group", "UserID", "UserDeviceType"])["Missed Calls"].value_counts().unstack()[3]
        else:
            datatable_data["Missed Calls"] = 0
        datatable_data["Total_call_duration"] = call_analytics_data.groupby(["Group", "UserID", "UserDeviceType"])["duration"].sum().tolist()
        
        datatable = dt.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in datatable_data.columns],
        data=datatable_data.to_dict('records'),
        page_current=0,
        page_size=5,
        page_action='native',
        style_header={'backgroundColor': 'rgb(30, 30, 30)'},
        style_cell={
            'backgroundColor': 'rgb(50, 50, 50)',
            'color': 'white'
        }
        )
        
        return [
                dcc.Graph(figure = figure), 
                html.Br() ,
                cardDiv, 
                html.Br(),
                datatable
               ]
    
    # Tab - 2 "Device data analysis"
    elif Tabs == "tab-2":
        if device_date is None or device_date == []: 
            device_analytics_data = device_count(device_data)
        else:
            device_analytics_data = device_count(device_data[device_data["DeviceEventDate"].isin(device_date)])
          
        fig = px.pie(device_analytics_data, names = "Device", values = "Count", color = "Device", hole = .3)
        fig.update_layout(autosize=True,
                          margin=dict(l=0, r=0, t=25, b=20),
                          )
        return dcc.Graph(figure = fig)
    
    # Tab - 3 "Service data analysis"
    elif Tabs == "tab-3":
        if service_date is None or service_date == []:
            service_analytics_data = service_data["FeatureName"].value_counts().reset_index(name = "Count")
        else:
            service_analytics_data = service_data["FeatureName"][service_data["FeatureEventDate"].isin(service_date)].value_counts().reset_index(name = "Count")
        fig = px.pie(service_analytics_data, names = "index", values = "Count",color = "index")
        
        fig.update_layout(autosize=True,
                          margin=dict(l=0, r=0, t=25, b=20),
                          )
        return dcc.Graph(figure = fig)
    else:
        return None

 

@app.callback(
    Output('group-dropdown', 'options'),
    [
    Input('start-date-dropdown', 'value'),
    Input('end-date-dropdown',  'value')
    ]
    )

# Updating the group 
def update_groups(start_date, end_date ):
    
    print("data type = ",  str(type(start_date)))
    print("data value = ", str(start_date))
    print("data type = ",  str(type(end_date)))
    print("data value = ", str(end_date))
    
    temp_data = call_data [ (  call_data["date"] >= start_date)  & ( call_data["date"]<= end_date)]
    group_list = temp_data["Group"].unique().tolist()
    group_list = [ {"label":m, "value":m }      for m in group_list] 

    return group_list

# Main function
def main():
    print("Start of the main function")

    global project_name
    project_name = "CDR Data Analytics "
    load_data()
    open_browser()
    
    global app
    app.title = project_name
    app.layout = create_app_ui()
    app.run_server()
    

    print("End of the main function")
    app = None
    project_name = None
    
    global call_data, service_data, device_data, start_date_list,end_date_list,report_type
    call_data = None
    service_data = None
    device_data = None
    start_date_list = None
    end_date_list = None
    report_type = None


    print("End of the main function")

 
if (__name__ == '__main__'):
    main()
