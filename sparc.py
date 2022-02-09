import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time

###
# Testing Data Plotting
###
data_url = "data/y_test_california_2020-2021.csv"

data = pd.read_csv(data_url)
most_recent_day = data.iloc[-1]

genmix_vars = ['Solar', 'Wind', 'Geothermal', 'Biomass', 'Biogas', 'Small hydro',
    'Coal', 'Nuclear', 'Batteries', 'Imports', 'Other', 'Natural Gas',
    'Large Hydro']

fig, ax = plt.subplots(figsize=(16,8))
for source_indx, source in enumerate(genmix_vars):
    # Plot the true values
    values = []
    for i in range(24):
        col_val = source + '_' + str(i)
        val = most_recent_day[col_val]
        values.append(val)
    ax.plot(range(24),values)
    
ax.legend(genmix_vars,loc='right')
ax.set_xlabel('Hour')
ax.set_ylabel('kWh')

###
# Testing fonts
###

# st.markdown(
#         """
#         <style>
# @font-face {
#   font-family: 'Montserrat';
#   font-style: normal;
#   font-weight: 400;
#   src: url(https://fonts.gstatic.com/s/quicksand/v24/6xK-dSZaM9iE8KbpRA_LJ3z8mH9BOJvgkP8o58a-wg.woff2) format('woff2');
#   unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
# }

#     html, body, [class*="css"]  {
#     font-family: 'Montserrat';
#     font-size: 48px;
#     }
#     </style>

#     """,
#         unsafe_allow_html=True,
#     )

###
# Main app components
###

earth_img = "https://purepng.com/public/uploads/large/purepng.com-earthearthplanetglobethird-planet-from-the-sun-1411526987612f5l5p.png"
tree_img = "https://www.pinclipart.com/picdir/middle/0-1348_leaves-clipart-mango-tree-clipart-tree-png-transparent.png"
energy_img = "https://www.pinclipart.com/picdir/big/105-1057895_green-my-life-app-eliminates-the-carbon-footprint.png"

# Set page title and favicon.
st.set_page_config(
    page_title="SPARC", page_icon=earth_img,
)

st.image(energy_img)

st.title('SPARC')
st.header('{ Save Power and Reduce Carbon }')
st.sidebar.markdown("## About SPARC California")
st.sidebar.markdown("Welcome to SPARC California! This app allows you to see the carbon emissions of common daily activities for the next few days.")

# User Input
day = st.selectbox("Select a day", ["Today","Tomorrow", "Day After Tomorrow"])
hour = st.selectbox("Select a time",
                    ['12:00am'] + [str(h) + ':00am' for h in range(1,12)] + ['12:00pm'] + [str(h) + ':00pm' for h in range(1,12)],
                    index=13)
activity = st.selectbox("Select an activity", ["Charge an EV", "Run a load of laundry","Take a hot shower"])

clicked_generate = st.button('Generate Forecast')

if (clicked_generate):
    # Make call to model

    with st.empty():
        for seconds in range(2):
            st.write(f"Gathering prediction...⏳ {seconds} seconds have passed")
            time.sleep(1)
        st.write("✔️ Complete!")

    # Write output
    st.subheader('To {} at {} {}, you will produce: '.format(activity[0].lower() + activity[1:], hour, day.lower()))

    st.subheader('__ g CO2',anchor='prediction')

    pred_alignment = """
    <style>
    #prediction {
    text-align: center
    }
    </style>
    """
    st.markdown(pred_alignment, unsafe_allow_html=True)

    with st.expander("Click to see the forecast results"):
        st.subheader('The forecasted generation mix for {}'.format(day.lower()))
        st.pyplot(fig)

clicked_generate = False