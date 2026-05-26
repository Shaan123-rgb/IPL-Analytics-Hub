import streamlit as st
from streamlit_option_menu import option_menu

from data_loader import load_and_clean_data, load_deliveries
from views.dataset import show_dataset
from views.overview import show_overview
from views.analytics_dashboard import show_analytics_dashboard
from views.advanced_analytics import show_advanced_analytics
from views.team_comparison import show_team_comparison
from views.player_matchups import show_player_matchups
from views.data_assistant import show_data_assistant
from views.predictor import show_predictor
from views.home import show_home

# config
st.set_page_config(page_title="IPL Data Analytics", layout="wide")

# load custom css
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# load up the data
df = load_and_clean_data()
del_df = load_deliveries()

# sidebar menu
with st.sidebar:
    
    selected = option_menu(
        "Main Menu",
        ["Home", "Dataset", "Overview", "Analytics Dashboard", "Advanced Analytics", "Team Comparision", "Player Matchups", "Match Predictor", "Data Assistant"],
        icons=["house", "table", "bar-chart", "cast", "graph-up", "person", "controller", "cpu", "robot"],
        menu_icon="trophy-fill", 
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#D4AF37", "font-size": "18px"}, 
            "nav-link": {"font-size": "15px", "text-align": "left", "margin":"0px", "--hover-color": "#1F2937"},
            "nav-link-selected": {"background-color": "#D4AF37", "color": "#0A0E17", "font-weight": "bold"},
        }
    )

# route to the right page based on selection
if selected == "Home":
    show_home(df)

elif selected == "Dataset":
    show_dataset(df)
    
elif selected == "Overview":
    show_overview(df)
    
elif selected == "Analytics Dashboard":
    show_analytics_dashboard(df)
    
elif selected == "Advanced Analytics":
    show_advanced_analytics(df)
    
elif selected == "Team Comparision":
    show_team_comparison(df)

elif selected == "Player Matchups":
    show_player_matchups(del_df)

elif selected == "Match Predictor":
    show_predictor(df)
    
elif selected == "Data Assistant":
    show_data_assistant(df)
