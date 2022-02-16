import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import requests
from datetime import datetime, timedelta
from pytz import timezone
import json


def generate_graph_forecasted():
    results = predict()
    fig3, ax3 = plt.subplots(figsize=(16,8))
    for source_type in results:
        lst = results[source_type].tolist()
        ax3.plot(range(len(lst)), lst)
    ax3.set_title('Forecasted Generation Mix for Next 24 hours')
    ax3.set_xlabel('Hours from Now')
    ax3.set_ylabel('MWh')
    ax3.legend(results.keys())

    return results, fig3

def generate_graph_historical_and_forecasted():
    genmix_vars = ['Solar', 'Wind', 'Geothermal', 'Biomass', 'Biogas', 'Small hydro',
        'Coal', 'Nuclear', 'Batteries', 'Imports', 'Natural Gas',
        'Large Hydro']

    renewable = ['Solar', 'Wind', 'Geothermal', 'Biomass', 'Biogas','Small hydro', 'Large Hydro', 'Nuclear']
    fossil_fuel = ['Coal', 'Natural Gas']   
    other = ['Batteries', 'Imports', 'Other']

    colors_grouped = ['#1f77b4','#ff7f0e','#2ca02c']
    colors_detailed = ['green','gray','brown','purple','orange','red','yellow','black','blue','pink','teal','lawngreen','indigo']

    """
    Plotting most recent CAISO data, grouped
    """

    # Get most recent CAISO data, then filter for today only
    data2 = get_last_n_days(1)
    length_today_only = int(60/5 * datetime.now(timezone('US/Pacific')).hour)
    data2 = data2.tail(length_today_only)

    # Add grouped columns
    data2['fossil_fuel'] = data2[fossil_fuel].sum(axis=1)
    data2['renewable'] = data2[renewable].sum(axis=1)
    data2['other'] = data2[other].sum(axis=1)

    # Set up grouped plot (ax2)
    fig2, ax2 = plt.subplots(figsize=(16,8))
    for source_indx, source in enumerate(['fossil_fuel','renewable','other']):
        ax2.plot(data2['date_time_5min'], data2[source], c=colors_grouped[source_indx])
    ax2.legend(['fossil_fuel','renewable','other'])

    # Set up detailed plot (ax3)
    fig3, ax3 = plt.subplots(figsize=(16,8))
    for source_indx, source in enumerate(genmix_vars):
        ax3.plot(data2['date_time_5min'], data2[source], c=colors_detailed[source_indx])
    ax3.legend(genmix_vars,loc='right')

    # Add the forecasting results
    # results = predict() # local call

    res = requests.get(f"https://sparc-cloud-run-hdyvu4kycq-uw.a.run.app/predict")
    print('\n\n\nresult of call: ', res.text, '\n\n\n')
    res = json.loads(res.text)['result']
    results = {grouped_source: list(res[grouped_source].values()) for grouped_source in res.keys()}
    
    hours_from_pred = []
    for i in range(24):
        hours_from_pred.append(data2.iloc[-1]['date_time_5min'] + timedelta(hours=i))
    results['time'] = hours_from_pred

    for source_type in ['fossil_fuel','renewable','other']:
        # lst = results[source_type].tolist() # need if calling locally
        lst = results[source_type]
        ax2.plot(results['time'], lst)
        ax3.plot(results['time'], lst)

        # Add a vertical line
    for ax in ([ax2, ax3]):
        ax.vlines(x=data2.iloc[-1]['date_time_5min'], ymin=0,ymax=20000,colors='red',linestyles='dotted')
        ax.set_xlabel('Time')
        ax.set_ylabel('MWh')
        ax.set_xticklabels(ax.get_xticks(), rotation = 45)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%h-%d %I:%M%p'))

    return results, fig2, fig3