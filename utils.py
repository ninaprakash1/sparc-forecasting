import requests
from datetime import datetime, timedelta
from pytz import timezone
import json
import logging
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from deploy.backend.utils import get_last_n_days

colors = {'solar': '#E3D18A','wind':'#02475E', 'hydro': '#FFE9D6', 'renewable_other': '#A7D0CD', 'battery': '#222a2a', 'fossil_fuel': '#7B6079','other': '#DE8971'}

def plot_gauge(co2_perc):
    # fig = go.Figure()
    # fig.add_trace(go.Indicator(
    #     domain = {'x':[0,1], 'y':[0,1]},
    #     value = co2,
    #     mode = 'gauge',
    #     gauge = {
    #         'shape' : 'angular',
    #         'steps':[{'range':[0,33*5], 'color': '#95CD41'}, # '#37a706'
    #                 {'range':[33*5,67*5], 'color': '#FFF89A'}, # '#e1ed41'
    #                 {'range':[67*5,100*5], 'color': '#D9534F'}], # '#DD4A48'}], # '#D82E3F'
    #         'bar':{'color':'black', 'thickness':0.0},
    #         'threshold':{'line':{'width':8, 'color':'black'}
    #                     ,'thickness':0.8, 'value':co2},
    #         'axis':{'range':[None,500]}
    #     }
    
    # ))
    # return fig

    fig = go.Figure()
    fig.add_trace(go.Indicator(
        domain = {'x':[0,1], 'y':[0,1]},
        value = co2_perc,
        mode = 'gauge',
        gauge = {
            'shape' : 'angular',
            'steps':[{'range':[0,33], 'color': '#95CD41'},
                    {'range':[33,67], 'color': '#FFF89A'},
                    {'range':[67,100], 'color': '#D9534F'}],
            'bar':{'color':'black', 'thickness':0.0},
            'threshold':{'line':{'width':8, 'color':'black'}
                        ,'thickness':0.8, 'value':co2_perc},
            'axis':{'range':[None,100]}
        }
    
    ))
    return fig

def plot_hourly_barchart(results):
    time_idx = np.arange(1,len(results['solar'])+1).astype(int)

    results_perc, recommended_time = get_recommendation(results)

    fig = go.Figure()
    fig.add_bar(name='Solar', x= time_idx, y=results_perc['solar'], marker_color=colors['solar'])
    fig.add_bar(name='Wind', x= time_idx, y=results_perc['wind'], marker_color=colors['wind'])
    fig.add_bar(name='Hydro', x= time_idx, y=results_perc['hydro'], marker_color=colors['hydro'])
    fig.add_bar(name='Other Renewables', x= time_idx, y=results_perc['renewable_other'],
            marker_color = colors['renewable_other'])
    fig.add_bar(name='Battery', x= time_idx, y=results_perc['battery'], marker_color=colors['battery'])
    fig.add_bar(name  = 'Fossil Fuels', x = time_idx, y= results_perc['fossil_fuel'], marker_color = colors['fossil_fuel'])
    fig.add_bar(name  = 'Other', x = time_idx, y= results_perc['other'], marker_color = colors['other'])
    fig.update_layout(barmode='relative', plot_bgcolor='rgba(0,0,0,0)',bargap=0.01, legend=dict(
        orientation="h",yanchor="bottom",y=1.02,xanchor="center", x=0.5))
    fig.update_xaxes(title = 'Hour')
    fig.update_yaxes(range=[0,100], title = 'Percentage')

    return fig, recommended_time

def smooth_5min_data(data, kernel_size = 12):
    kernel = np.ones(kernel_size) / kernel_size
    return np.convolve(data, kernel, mode='same')

def get_recommendation(results):

    results = pd.DataFrame(results)

    # normalize results for graphing
    results_perc = results.drop(columns=['time','total']).div(results.drop(columns=['time','total']).sum(axis=1),axis=0).round(3) * 100

    # get time with smallest fossil fuel and other usage
    min_indx = results[['fossil_fuel','other']].sum(axis=1).idxmin()
    recommended_time = results.iloc[min_indx]['time']

    return results_perc, recommended_time

def generate_graph_historical_and_forecasted():

    fossil_fuel = ['Coal','Natural Gas']
    other = ['Imports', 'Other']
    hydro = ['Small hydro', 'Large Hydro']
    renewable_other = ['Geothermal', 'Biomass', 'Biogas', 'Nuclear']

    """
    Plotting most recent CAISO data, grouped
    """

    # Get most recent CAISO data, then filter for today only
    data2 = get_last_n_days(1)
    length_today_only = int(60/5 * datetime.now(timezone('US/Pacific')).hour) + 1
    data2 = data2.tail(length_today_only)

    # cut off the last few minutes to round to the nearest hour
    data2 = data2.head(len(data2) - int(datetime.now().minute / 5))

    # Add grouped columns
    data2['Fossil Fuels'] = data2[fossil_fuel].sum(axis=1)
    data2['Other'] = data2[other].sum(axis=1)
    data2['Hydro'] = data2[hydro].sum(axis=1)
    data2['Other Renewables'] = data2[renewable_other].sum(axis=1)

    labels = ['Fossil Fuels','Solar','Wind','Hydro','Other Renewables','Batteries','Other']

    # Add the forecasting results
    res = requests.get(f"https://sparc-cloud-run-hdyvu4kycq-uw.a.run.app/predict")
    if 'result' not in str(res.text) or type(json.loads(res.text)['result']['battery']) == int:
        logging.error("Nothing returned from endpoint")
        logging.info(res)
        logging.info(res.text)
        return None, None, None
    else:
        res = json.loads(res.text)['result']
    results = {grouped_source: list(res[grouped_source].values()) for grouped_source in res.keys()}
    hours_from_pred = []
    for i in range(1,25):
        hours_from_pred.append(data2.iloc[-1]['date_time_5min'] + timedelta(hours=i))
    results['time'] = hours_from_pred
    logging.info("Time", results)

    # Concatenate the historical and forecast results
    data2_temp = data2[labels+['date_time_5min']]
    results_temp = pd.DataFrame(results).drop(columns=['total'])
    data2_temp = data2_temp.rename(columns={'date_time_5min': 'time', 'Fossil Fuels':'fossil_fuel','Solar':'solar','Wind': 'wind','Hydro':'hydro','Other Renewables':'renewable_other','Batteries':'battery','Other':'other'})
    hist_and_future_concat = pd.concat([data2_temp, results_temp])

    print('max = ', hist_and_future_concat.drop(columns=['time']).values.max())

    fig = go.Figure(data = [
        go.Scatter(name='Solar', x= hist_and_future_concat['time'], y=hist_and_future_concat['solar'], marker_color=colors['solar'],mode = 'lines'),
        go.Scatter(name='Wind', x= hist_and_future_concat['time'], y=hist_and_future_concat['wind'], marker_color=colors['wind'],mode = 'lines'),
        go.Scatter(name='Hydro', x= hist_and_future_concat['time'], y=hist_and_future_concat['hydro'], marker_color=colors['hydro'],mode = 'lines'),
        go.Scatter(name='Other Renewables', x= hist_and_future_concat['time'], y=hist_and_future_concat['renewable_other'], marker_color = colors['renewable_other'],mode ='lines'),
        go.Scatter(name='Battery', x= hist_and_future_concat['time'], y=hist_and_future_concat['battery'], marker_color=colors['battery'],mode = 'lines'),
        go.Scatter(name  = 'Fossil Fuels', x = hist_and_future_concat['time'], y= hist_and_future_concat['fossil_fuel'], marker_color = colors['fossil_fuel'], mode = 'lines'),
        go.Scatter(name = 'Current Hour', x = [datetime.now(), datetime.now()], y = [0, hist_and_future_concat.drop(columns=['time']).values.max()] , marker_color = 'red', mode = 'lines', line = dict(dash='dash'))
    ])
    fig.update_xaxes(title = 'Hour')
    fig.update_yaxes(title = 'MW')
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)',bargap=0.01,hovermode="x",
                    legend=dict(
        orientation="h",yanchor="bottom",y=1.02,xanchor="center", x=0.5))

    return results, fig