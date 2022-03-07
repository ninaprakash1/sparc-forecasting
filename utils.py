import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import requests
from datetime import datetime, timedelta
from pytz import timezone
import json
import logging

from deploy.backend.utils import get_last_n_days

def generate_graph_historical_and_forecasted():
    genmix_vars = ['Solar', 'Wind', 'Geothermal', 'Biomass', 'Biogas', 'Small hydro',
        'Coal', 'Nuclear', 'Batteries', 'Imports', 'Natural Gas',
        'Large Hydro']

    fossil_fuel = ['Coal','Natural Gas']
    other = ['Imports', 'Other']
    hydro = ['Small hydro', 'Large Hydro']
    renewable_other = ['Geothermal', 'Biomass', 'Biogas', 'Nuclear']
    # solar = ['Solar']
    # wind = ['Wind']
    # batteries = ['Batteries']

    colors_grouped = ['#2e91e5','#e15f99','#1ca71c', '#fb0d0d', '#da16ff', '#222a2a','#b68100']
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
    data2['other'] = data2[other].sum(axis=1)
    data2['hydro'] = data2[hydro].sum(axis=1)
    data2['renewable_other'] = data2[renewable_other].sum(axis=1)

    # Set up grouped plot (ax2)
    fig2, ax2 = plt.subplots(figsize=(16,8))
    for source_indx, source in enumerate(['fossil_fuel','Solar','Wind','hydro','renewable_other','Batteries','other']):
        ax2.plot(data2['date_time_5min'], data2[source], c=colors_grouped[source_indx])
    ax2.legend(['Fossil Fuels','Solar','Wind','Hydro','Other Renewables','Batteries','Other'])

    # Set up detailed plot (ax3)
    fig3, ax3 = plt.subplots(figsize=(16,8))
    for source_indx, source in enumerate(genmix_vars):
        ax3.plot(data2['date_time_5min'], data2[source], c=colors_detailed[source_indx])
    ax3.legend(genmix_vars,loc='right')

    # Add the forecasting results
    res = requests.get(f"https://sparc-cloud-run-hdyvu4kycq-uw.a.run.app/predict")
    print('\n\n\nresult of call: ', res.text, '\n\n\n')
    if 'result' not in str(res.text):
        logging.error("Nothing returned from endpoint")
        logging.info(res)
        logging.info(res.text)
        return None, None, None
    else:
        res = json.loads(res.text)['result']
    results = {grouped_source: list(res[grouped_source].values()) for grouped_source in res.keys()}
    
    hours_from_pred = []
    for i in range(24):
        hours_from_pred.append(data2.iloc[-1]['date_time_5min'] + timedelta(hours=i))
    results['time'] = hours_from_pred

    for source_type in ['fossil_fuel','solar','wind','hydro','renewable_other','battery','other']:
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