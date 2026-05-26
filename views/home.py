import streamlit as st

def show_home(df):
    # a welcoming landing page
    
    st.markdown("<h1 style='text-align: center; color: #1E2D62; font-size: 3.5rem; margin-bottom: 0;'>IPL Data Analytics</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #D4AF37; margin-top: 0;'>The Ultimate Cricket Dashboard</h3>", unsafe_allow_html=True)
    
    st.divider()
    
    col1, col2, col3 = st.columns([1, 10, 1])
    with col2:
        st.markdown(
            """
            ### Welcome to the IPL Analytics Hub!
            
            This dashboard dives deep into the historical data of the Indian Premier League, uncovering the strategies, player dominance, and team DNA that define the tournament.
            
            **What you'll find inside:**
            - 📊 **Dataset Explorer:** View, filter, and download the raw historical data.
            - 📈 **Tournament Overview:** High-level metrics, score averages, and umpire audits.
            - 🎯 **Analytics Dashboard:** Year-over-year trends, win type distributions, and venue par scores.
            - 🔍 **Advanced Analytics:** Deep dives using Treemaps, Heatmaps, Sankey Diagrams, and more.
            - ⚔️ **Team Comparison:** Head-to-Head matchups and Team DNA radar charts.
            - 🤖 **Match Predictor:** An AI-powered tool to predict match outcomes based on historical conditions.
            - 💬 **Data Assistant:** Ask simple questions about the data and get quick answers!
            
            ---
            *Use the sidebar on the left to navigate through the different modules.*
            """
        )
    
    # some fun random stats at the bottom
    st.divider()
    st.markdown("#### Quick Facts")
    
    f1, f2, f3 = st.columns(3)
    total_matches = len(df)
    total_runs = df["First_Innings_Score"].sum() + df["Second_Innings_Score"].sum()
    super_overs = len(df[df["Win_Type"].astype(str).str.lower() == "draw"])
    
    f1.metric("Total Matches Recorded", total_matches)
    f2.metric("Total Runs Scored", f"{total_runs:,.0f}")
    f3.metric("Nail-Biting Finishes (Ties/Draws)", super_overs)
