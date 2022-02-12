import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
from utils import generate_graph_historical, generate_graph_forecasted
import requests

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

# res = requests.get(f"https://sparc-cloud-run-hdyvu4kycq-uw.a.run.app/echo/something")
# st.title(res.text)

st.title('SPARC')
st.header('{ Save Power and Reduce Carbon }')
st.sidebar.markdown("## About SPARC California")
st.sidebar.markdown("Welcome to SPARC California! This app allows you to see the carbon emissions of common daily activities for the next few days.")

# User Input
# day = st.selectbox("Select a day", ["Today","Tomorrow", "Day After Tomorrow"])
hour = st.selectbox("Select a time in the next 24 hours",
                    ['12:00am'] + [str(h) + ':00am' for h in range(1,12)] + ['12:00pm'] + [str(h) + ':00pm' for h in range(1,12)],
                    index=13)
activity = st.selectbox("Select an activity", ["Charge an EV", "Run a load of laundry","Take a hot shower"])

clicked_generate = st.button('Generate Forecast')

if (clicked_generate):
    # Make call to model

    with st.empty():
        for seconds in range(2):
            st.write(f"Gathering prediction...")
            time.sleep(.05)
        st.write("✔️ Complete!")

    # Write output
    st.subheader('To {} at {}, you will produce: '.format(activity[0].lower() + activity[1:], hour))

    st.subheader('__ g CO2',anchor='prediction')

    pred_alignment = """
    <style>
    #prediction {
    text-align: center
    }
    </style>
    """
    st.markdown(pred_alignment, unsafe_allow_html=True)

    fig2 = generate_graph_historical()
    fig3 = generate_graph_forecasted()

    with st.expander("Click to see the forecast results"):
        st.subheader('Generation mix for last 24 hours')
        st.pyplot(fig2)

        st.subheader('Forecasted generation mix for next 24 hours')
        st.pyplot(fig3)

clicked_generate = False