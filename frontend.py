import json
import requests
import streamlit as st
from utils import generate_graph_historical_and_forecasted
from deploy.backend.utils import compute_co2, ACTIVITY_USAGE_KWH

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
st.header('{ Save Power and Reduce Carbon }')
st.sidebar.markdown("## About SPARC California")
st.sidebar.markdown("Welcome to SPARC California! This app allows you to see the forecasted carbon emissions of common daily activities.")
st.sidebar.markdown("At any moment, the electricity that we use from the grid comes from a mix of many sources, from natural gas to solar to nuclear depending on resource availability, weather, time, day, and season. The more nonrenewable resources are used to provide energy to the grid, the more CO2 emissions are produced.")
st.sidebar.markdown("If we can predict how much CO2 we are producing at a given time, we can adjust our behavior to reduce emissions!")
st.sidebar.markdown("")
st.sidebar.markdown("*Kun Guo, Nina Prakash, Griffin Schillinger Tarpenning | Stanford University | CS 329s*")

# User Input

activity = st.selectbox("Select an activity", ["Charge an EV (Level 1)", "Charge an EV (Level 2)",
                                               "Charge an EV (Level 3)", "Run the washing machine",
                                               "Run the dryer", "Take a hot shower",
                                               "Run central AC", "Run a space heater",
                                               "Run hot water heater", "Run the dishwasher",
                                               "Watch TV"])

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
    energy_cons = st.text_input("Energy consumption of {} (kW):".format(activity_present_tense[activity]), ACTIVITY_USAGE_KWH[activity], max_chars=3)
    try:
        energy_cons = int(energy_cons)
    except:
        st.error("Please enter a number")

clicked_generate = st.button('Generate Forecast')

if (clicked_generate):
    # Make call to model

    with st.empty():
        st.write(f"Gathering prediction...")
        results, fig2, fig3 = generate_graph_historical_and_forecasted()
        co2 = compute_co2(results, activity, hour, duration)
        st.success('Model run complete')

    # Write output
    st.subheader('To {} at {} for {}, you will produce: '.format(activity[0].lower() + activity[1:], hour, duration))

    st.header('%.1f lb CO2' %(co2),anchor='prediction')

    pred_alignment = """
    <style>
    #prediction {
    text-align: center
    }
    #prediction {
    color: green
    }
    </style>
    """
    st.markdown(pred_alignment, unsafe_allow_html=True)

    with st.expander("Click to see the forecast results"):
        st.subheader('Historical and Predicted Generation Mix')
        st.pyplot(fig2)

        st.subheader('Historical (Detailed) and Predicted Generation Mix')
        st.pyplot(fig3)

clicked_generate = False

retrain = st.button('Retrain model')
if (retrain):
    with st.empty():
        st.write(f"Retraining...")

        res = requests.get(f"https://sparc-cloud-run-hdyvu4kycq-uw.a.run.app/train/days=5")
        train_result = json.loads(res.text)['result']
        st.success(train_result)