import pandas as pd
import streamlit as st

@st.cache_data
def load_and_clean_data():
    # just loads the ipl dataset and cleans up some basic stuff
    try:
        # grab the csv
        df = pd.read_csv("IPL.csv")
    except FileNotFoundError:
        st.error("Error: 'IPL.csv' not found. Please ensure the dataset is in the project root directory.")
        st.stop()
        
    # make toss decisions lowercase and standardized
    if "Toss_Decision" in df.columns:
        df["Toss_Decision"] = df["Toss_Decision"].str.strip().str.lower().replace({
            "bat": "Bat",
            "bowl": "Bowl",
            "field": "Bowl"
        })

    # combine all the different names for the same stadiums
    venue_mapping = {
        "M Chinnaswamy Stadium": "M Chinnaswamy Stadium, Bengaluru",
        "M.Chinnaswamy Stadium": "M Chinnaswamy Stadium, Bengaluru",
        "M.Chinnaswamy Stadium, Bengaluru": "M Chinnaswamy Stadium, Bengaluru",

        "Wankhede Stadium": "Wankhede Stadium, Mumbai",
        "vankhede stadium": "Wankhede Stadium, Mumbai",

        "Feroz Shah Kotla": "Arun Jaitley Stadium, Delhi",
        "Arun Jaitley Stadium": "Arun Jaitley Stadium, Delhi",

        "Eden Gardens": "Eden Gardens, Kolkata",

        "MA Chidambaram Stadium": "MA Chidambaram Stadium, Chennai",
        "MA Chidambaram Stadium, Chepauk": "MA Chidambaram Stadium, Chennai",
        "MA Chidambaram Stadium, Chepauk, Chennai": "MA Chidambaram Stadium, Chennai",

        "Punjab Cricket Association Stadium, Mohali": "Punjab Cricket Association IS Bindra Stadium, Mohali",
        "Punjab Cricket Association IS Bindra Stadium": "Punjab Cricket Association IS Bindra Stadium, Mohali",
        "Punjab Cricket Association IS Bindra Stadium, Mohali, Chandigarh": "Punjab Cricket Association IS Bindra Stadium, Mohali",

        "Rajiv Gandhi International Stadium": "Rajiv Gandhi International Stadium, Hyderabad",
        "Rajiv Gandhi International Stadium, Uppal": "Rajiv Gandhi International Stadium, Hyderabad",
        "Rajiv Gandhi International Stadium, Uppal, Hyderabad": "Rajiv Gandhi International Stadium, Hyderabad",

        "Sawai Mansingh Stadium": "Sawai Mansingh Stadium, Jaipur",

        "Sardar Patel Stadium, Motera": "Narendra Modi Stadium, Ahmedabad",

        "Dr DY Patil Sports Academy": "Dr DY Patil Sports Academy, Mumbai",
        "Brabourne Stadium": "Brabourne Stadium, Mumbai",

        "Maharashtra Cricket Association Stadium": "Maharashtra Cricket Association Stadium, Pune",
        "Subrata Roy Sahara Stadium": "Maharashtra Cricket Association Stadium, Pune",

        "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium": "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium, Visakhapatnam",

        "Himachal Pradesh Cricket Association Stadium": "Himachal Pradesh Cricket Association Stadium, Dharamsala",

        "Maharaja Yadavindra Singh International Cricket Stadium, Mullanpur": "Maharaja Yadavindra Singh International Cricket Stadium, Mullanpur, Chandigarh",

        "Sheikh Zayed Stadium": "Zayed Cricket Stadium, Abu Dhabi"
    }
    
    if "Venue" in df.columns:
        df["Venue"] = df["Venue"].replace(venue_mapping)
        
    return df

@st.cache_data
def load_deliveries():
    # read the big ball by ball file
    try:
        del_df = pd.read_csv("deliveries.csv")
    except:
        return pd.DataFrame()
        
    # fill empty spots with sensible defaults so nothing breaks
    del_df["extras_type"] = del_df["extras_type"].fillna("none")
    del_df["player_dismissed"] = del_df["player_dismissed"].fillna("no_wicket")
    del_df["dismissal_kind"] = del_df["dismissal_kind"].fillna("none")
    del_df["fielder"] = del_df["fielder"].fillna("none")
    
    return del_df
