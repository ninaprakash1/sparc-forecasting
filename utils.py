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

    colors_grouped = ['#E3D18A','#02475E','#FFE9D6', '#A7D0CD', '#222a2a', '#7B6079','#DE8971']
    colors_detailed = ['green','gray','brown','purple','orange','red','yellow','black','blue','pink','teal','lawngreen','indigo']

    """
    Plotting most recent CAISO data, grouped
    """

    # Get most recent CAISO data, then filter for today only
    data2 = get_last_n_days(1)
    length_today_only = int(60/5 * datetime.now(timezone('US/Pacific')).hour) + 1
    data2 = data2.tail(length_today_only)

    # Add grouped columns
    data2['Fossil Fuels'] = data2[fossil_fuel].sum(axis=1)
    data2['Other'] = data2[other].sum(axis=1)
    data2['Hydro'] = data2[hydro].sum(axis=1)
    data2['Other Renewables'] = data2[renewable_other].sum(axis=1)

    labels = ['Fossil Fuels','Solar','Wind','Hydro','Other Renewables','Batteries','Other']

    # Set up grouped plot (ax2)
    fig2, ax2 = plt.subplots(figsize=(16,8))
    for source_indx, source in enumerate(labels):
        ax2.plot(data2['date_time_5min'], data2[source], c=colors_grouped[source_indx])
    ax2.legend(labels)

    # Set up detailed plot (ax3)
    fig3, ax3 = plt.subplots(figsize=(16,8))
    for source_indx, source in enumerate(genmix_vars):
        ax3.plot(data2['date_time_5min'], data2[source], c=colors_detailed[source_indx])
    ax3.legend(genmix_vars,loc='right')

    # Add the forecasting results
    res = requests.get(f"https://sparc-cloud-run-hdyvu4kycq-uw.a.run.app/predict")
    logging.info('\n\n\nresult of call: ', res.text, '\n\n\n')

    if 'result' not in str(res.text) or type(json.loads(res.text)['result']['battery']) == int:
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
    logging.info("Time", results)

    for i, source_type in enumerate(['fossil_fuel','solar','wind','hydro','renewable_other','battery','other']):
        lst = results[source_type]
        ax2.plot(results['time'], lst, c=colors_grouped[i])
        ax3.plot(results['time'], lst, c=colors_detailed[i])

        # Add a vertical line
    for ax in ([ax2, ax3]):
        ax.vlines(x=data2.iloc[-1]['date_time_5min'], ymin=0,ymax=20000,colors='red',linestyles='dotted')
        ax.set_xlabel('Time')
        ax.set_ylabel('MWh')
        ax.set_xticklabels(ax.get_xticks(), rotation = 45)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%h-%d %I:%M%p'))

    return results, fig2, fig3