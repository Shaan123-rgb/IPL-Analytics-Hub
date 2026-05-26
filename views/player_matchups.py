import streamlit as st
import pandas as pd

def show_player_matchups(del_df):
    st.title("Player Matchups")
    st.markdown("Dive into the ball-by-ball history to see exactly how specific batsmen fare against specific bowlers.")
    st.divider()

    # if data didn't load, stop here
    if del_df.empty:
        st.error("Could not load deliveries data. Please make sure deliveries.csv is in the folder.")
        return

    # get all unique players
    all_batters = sorted(del_df["batter"].unique().tolist())
    all_bowlers = sorted(del_df["bowler"].unique().tolist())

    col1, col2 = st.columns(2)
    with col1:
        selected_batter = st.selectbox("Select Batsman", all_batters, index=all_batters.index("V Kohli") if "V Kohli" in all_batters else 0)
    with col2:
        selected_bowler = st.selectbox("Select Bowler", all_bowlers, index=all_bowlers.index("JJ Bumrah") if "JJ Bumrah" in all_bowlers else 0)

    st.divider()

    # filter the data for this exact matchup
    matchup_data = del_df[(del_df["batter"] == selected_batter) & (del_df["bowler"] == selected_bowler)]

    if matchup_data.empty:
        st.info(f"{selected_batter} has never faced {selected_bowler} in the IPL (or data is missing).")
        return

    # calculate exact stats
    total_runs = matchup_data["batsman_runs"].sum()
    balls_faced = len(matchup_data)
    strike_rate = (total_runs / balls_faced) * 100 if balls_faced > 0 else 0
    
    # count wickets (ignoring run outs where the bowler isn't credited)
    bowler_wickets = matchup_data[(matchup_data["is_wicket"] == 1) & (matchup_data["dismissal_kind"] != "run out")]
    times_dismissed = len(bowler_wickets)

    # display the stats in nice boxes
    st.markdown(f"### {selected_batter} vs {selected_bowler}")
    
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Runs Scored", total_runs)
    k2.metric("Balls Faced", balls_faced)
    k3.metric("Strike Rate", f"{strike_rate:.1f}")
    k4.metric("Times Dismissed", times_dismissed, delta="Wickets" if times_dismissed > 0 else None, delta_color="inverse")

    st.divider()

    # show how the runs were scored (boundaries, singles, etc)
    st.subheader("Scoring Breakdown")
    scoring = matchup_data["batsman_runs"].value_counts().sort_index().to_frame(name="Count")
    
    # rename index for better reading
    scoring.index = scoring.index.map({
        0: "Dot Balls (0)",
        1: "Singles (1)",
        2: "Doubles (2)",
        3: "Threes (3)",
        4: "Fours (4)",
        5: "Fives (5)",
        6: "Sixes (6)"
    })
    
    st.bar_chart(scoring["Count"], color="#D4AF37")
