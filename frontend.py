import streamlit as st
from utils import generate_graph_historical_and_forecasted, plot_hourly_barchart, plot_gauge
from deploy.backend.utils import compute_co2

###
# Main app components
###

energy_img = "https://www.pinclipart.com/picdir/big/105-1057895_green-my-life-app-eliminates-the-carbon-footprint.png"
earth_img = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSx-MftU146rqnu3qXiH1-PvbhqkBtqxln3nA&usqp=CAU"

# Set page title and favicon.
st.set_page_config(
    page_title="SPARC", page_icon=earth_img,
)

st.image(energy_img)

st.title('SPARC')
st.header('{ Schedule Power and Reduce Carbon }')
st.sidebar.markdown("## About SPARC California")
st.sidebar.markdown("Welcome to SPARC California! This app allows you to see the forecasted carbon emissions of common daily activities.")
st.sidebar.markdown("At any moment, the electricity that we use from the grid comes from a mix of many sources, from natural gas to solar to nuclear depending on resource availability, weather, time, day, and season. The more nonrenewable resources are used to provide energy to the grid, the more CO2 emissions are produced.")
st.sidebar.markdown("If we can predict how much CO2 we are producing at a given time, we can adjust our behavior to reduce emissions!")
st.sidebar.markdown("")
st.sidebar.markdown("*Kun Guo, Nina Prakash, Griffin Schillinger Tarpenning | Stanford University | CS 329s*")

# User Input

ACTIVITY_USAGE_KWH = { # these are all kW x 1
    "Charge an EV (Level 1)": 1, # https://rmi.org/electric-vehicle-charging-for-dummies/#:~:text=If%20you%20just%20plug%20an,7%20kW%20and%2019%20kW.
    "Charge an EV (Level 2)": 13,
    "Charge an EV (Level 3)": 50,
    "Run the washing machine": 5, # https://blog.arcadia.com/electricity-costs-10-key-household-products/#:~:text=An%20average%20cycle%20for%20a,to%20run%20for%2030%20minutes.
    "Run the dryer": 4, # https://majorenergy.com/how-much-electricity-does-a-dryer-use/#:~:text=Dryers%20are%20typically%20somewhere%20in,and%206%20kilowatts%20an%20hour.
    "Take a hot shower": 8.2, # https://greengeekblog.com/tools/shower-cost-calculator/#:~:text=An%20average%208.2%20minute%20shower,energy%20to%20heat%20our%20water.,
    "Run central AC": 3.5, # https://energyusecalculator.com/electricity_centralac.htm
    "Run a space heater": 1.5, # https://experthomereport.com/do-space-heaters-use-a-lot-of-electricity/#:~:text=Although%20amounts%20vary%20per%20space,but%20in%20hours%20of%20kilowatt.
    "Run hot water heater": 4, # https://www.directenergy.com/learning-center/how-much-energy-water-heater-use#:~:text=Typically%2C%20a%20hot%20water%20heater,month%2C%20or%20%24438%20per%20year.
    "Run the dishwasher": 1.8, # https://www.inspirecleanenergy.com/blog/sustainable-living/cost-to-run-dishwasher#:~:text=Most%20dishwashers%20use%20an%20average,hours%20(kWh)%20of%20electricity.
    "Watch TV": 0.1 # https://letsavelectricity.com/how-much-power-does-a-tv-use-in-an-hour/
}

activity = st.selectbox("Select an activity", ACTIVITY_USAGE_KWH.keys())

activity_present_tense = {
    "Charge an EV (Level 1)": "charging an EV (Level 1)",
    "Charge an EV (Level 2)": "charging an EV (Level 2)",
    "Charge an EV (Level 3)": "charging an EV (Level 3)",
    "Run the washing machine": "running the washing machine",
    "Run the dryer": "running the dryer",
    "Take a hot shower": "taking a hot shower",
    "Run central AC": "running central AC",
    "Run a space heater": "running a space heater",
    "Run hot water heater": "running hot water heater",
    "Run the dishwasher": "running the dishwasher",
    "Watch TV": "watching TV"
}

hour = st.selectbox("Select a time in the next 24 hours",
                    ['12:00am'] + [str(h) + ':00am' for h in range(1,12)] + ['12:00pm'] + [str(h) + ':00pm' for h in range(1,12)],
                    index=13)

duration = st.selectbox("Select a duration", ["1 hour"] + [str(i) + " hours" for i in range(2,25)])

choice = st.radio("Pick one",["Use default energy consumption of {}: {} kWh".format(activity_present_tense[activity],
                                                                             ACTIVITY_USAGE_KWH[activity]), "Enter my own"])

if (choice == "Enter my own"):
    energy_cons = st.text_input(f"Energy consumption of {activity_present_tense[activity]} (kW):", ACTIVITY_USAGE_KWH[activity])
    try:
        energy_cons = float(energy_cons)
    except:
        st.error("Please enter a number")
else:
    energy_cons = ACTIVITY_USAGE_KWH[activity]

clicked_generate = st.button('Generate Forecast')

if (clicked_generate):
    # Make call to model
    co2 = None

    with st.empty():
        st.write(f"Gathering prediction...")
        results, fig2 = generate_graph_historical_and_forecasted()
        fig3 = plot_hourly_barchart(results)
        if results and fig2 and fig3:
            co2, co2_perc, recommended_time = compute_co2(results, energy_cons, hour, duration)
            st.success('Model run complete')
        else:
            st.error("No results from model...")

    # Write output
    st.subheader(f'To {activity[0].lower() + activity[1:]} at {hour} for {duration}, you will produce: ')
    
    st.header('%0.1f lb CO2' %(co2) ,anchor='prediction')

    fig = plot_gauge(co2_perc)

    st.plotly_chart(fig)

    pred_alignment = """
        <style>
        #prediction {
        text-align: center
        }
        #prediction {
        color: black
        }
        </style>
        """
    if not co2_perc:
        pass
    elif (co2_perc < 33):
        pred_alignment = """
        <style>
        #prediction {
        text-align: center
        }
        #prediction {
        color: #37a706
        }
        </style>
        """
    elif (co2_perc < 67):
        pred_alignment = """
        <style>
        #prediction {
        text-align: center
        }
        #prediction {
        color: #e1ed41
        }
        </style>
        """
    else:
        pred_alignment = """
        <style>
        #prediction {
        text-align: center
        }
        #prediction {
        color: #D82E3F
        }
        </style>
        """

    if fig2 and fig3:
        st.markdown(pred_alignment, unsafe_allow_html=True)

        with st.expander("Click to see the forecast results"):
            st.subheader('Historical and Predicted Generation Mix')
            st.plotly_chart(fig2)

            st.subheader('Forecasted Generation Mix 24 hours from now')
            st.plotly_chart(fig3)

        with st.expander("Click to see recommendation"):
            st.subheader(f'Based on the forecast results, it is recommended that you begin {activity_present_tense[activity]} at {recommended_time.strftime("%I:00%p")} on {recommended_time.strftime("%b %d")}')

clicked_generate = False