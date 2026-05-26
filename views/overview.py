import streamlit as st
import pandas as pd

def show_overview(df):
    # shows the main tournament overview with kpis
    st.title("IPL Tournament Overview")
    st.markdown("---")

    # top level kpis
    total_matches = len(df)
    total_runs = df["First_Innings_Score"].sum() + df["Second_Innings_Score"].sum()
    avg_first_innings = df["First_Innings_Score"].mean()
    toss_win_match_win = df[df["Toss_Winner"] == df["Match_Winner"]]
    toss_advantage_rate = (len(toss_win_match_win) / total_matches) * 100 if total_matches > 0 else 0
    highest_score = max(df["First_Innings_Score"].max(), df["Second_Innings_Score"].max())

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Gross Tournament Runs", f"{total_runs:,.0f}", "Cumulative Scoring")
    kpi2.metric("Toss Advantage Rate", f"{toss_advantage_rate:.1f}%", "+ Impact of Toss", "normal")
    kpi3.metric("Avg 1st Innings Score", f"{avg_first_innings:.1f} Runs")
    kpi4.metric("Highest Single Innings", f"{highest_score} Runs", "Tournament Record")

    st.divider()

    # secondary kpis
    avg_run_margin = df[df["Win_Type"] == "runs"]["Win_Margin"].dropna().mean()
    avg_wicket_margin = df[df["Win_Type"] == "wickets"]["Win_Margin"].dropna().mean()
    unique_poms = df["Player_of_Match"].nunique()
    tie_matches = len(df[df["Win_Type"].astype(str).str.lower() == "draw"]) if "Win_Type" in df.columns else 0

    kpi5, kpi6, kpi7, kpi8 = st.columns(4)
    kpi5.metric("Avg Run Win Margin", f"{avg_run_margin:.1f} Runs", "When Defending")
    kpi6.metric("Avg Wicket Win Margin", f"{avg_wicket_margin:.1f} Wickets", "When Chasing")
    kpi7.metric("Unique Match Winners", f"{unique_poms} Players", "Award Diversity")
    kpi8.metric("Super Overs / Ties", f"{tie_matches}", "Nail-biting finishes")

    st.divider()

    # team performance table
    st.subheader("Team Performance Overview")
    teams_played = pd.concat([df['Team1'], df['Team2']]).value_counts().to_frame(name="Total_Matches")
    team_wins = df['Match_Winner'].value_counts().to_frame(name="Total_Wins")

    team_metrics = teams_played.merge(team_wins, left_index=True, right_index=True, how='left').fillna(0)
    team_metrics["Win Rate %"] = (team_metrics["Total_Wins"] / team_metrics["Total_Matches"]) * 100
    team_metrics["Total_Wins"] = team_metrics["Total_Wins"].astype(int)

    avg_scores = df.groupby('Team1')["First_Innings_Score"].mean().to_frame(name="Avg_1st_Innings_Score")
    team_metrics = team_metrics.merge(avg_scores, left_index=True, right_index=True, how='left')

    st.dataframe(
        team_metrics.style.format({
            "Avg_1st_Innings_Score": "{:.1f}",
            "Win Rate %": "{:.1f}%"
        }).background_gradient(subset=["Total_Wins", "Win Rate %"], cmap="YlGnBu"),
        use_container_width=True
    )
    st.divider()

    # defending vs chasing stats
    st.subheader("Tactical Success: Defending vs Chasing")
    defend_wins = df[df['Win_Type'] == 'runs']['Match_Winner'].value_counts().to_frame("Defend_Wins (Runs)")
    chase_wins = df[df['Win_Type'] == 'wickets']['Match_Winner'].value_counts().to_frame("Chase_Wins (Wickets)")

    tactical_df = defend_wins.merge(chase_wins, left_index=True, right_index=True, how='outer').fillna(0)
    tactical_df['Total_Wins'] = tactical_df['Defend_Wins (Runs)'] + tactical_df['Chase_Wins (Wickets)']
    tactical_df['Defend Win %'] = (tactical_df['Defend_Wins (Runs)'] / tactical_df['Total_Wins']) * 100
    tactical_df['Chase Win %'] = (tactical_df['Chase_Wins (Wickets)'] / tactical_df['Total_Wins']) * 100

    st.dataframe(
        tactical_df.style.format({
            "Defend Win %": "{:.1f}%",
            "Chase Win %": "{:.1f}%",
            "Defend_Wins (Runs)": "{:.0f}",
            "Chase_Wins (Wickets)": "{:.0f}",
            "Total_Wins": "{:.0f}"
        }).background_gradient(subset=["Defend Win %", "Chase Win %"], cmap="Purples"),
        use_container_width=True
    )
    st.divider()

    # match phase stats and win types
    col_1, col_2 = st.columns(2)

    with col_1:
        st.subheader("Match Phase Efficiency")
        phase_df = df.groupby("Match_Winner")[
            ["Powerplay_Scores", "Middle_Overs_Scores", "Death_Overs_Scores"]].mean().head(10)
        st.write("Average Runs Scored by Phase (Top 10 Teams)")
        st.dataframe(
            phase_df.style.highlight_max(axis=0, color="#d9f2d9").highlight_min(axis=0, color="#ffd9d9"),
            use_container_width=True
        )

    with col_2:
        st.subheader("Victory Method Audit")
        status_count = df["Win_Type"].value_counts().to_frame(name="Count")
        status_count["Share %"] = (status_count["Count"] / total_matches * 100)
        st.write("Distribution of Match Outcomes")
        st.dataframe(
            status_count.style.format({"Share %": "{:.2f}%"}),
            use_container_width=True
        )
    st.divider()

    # close matches
    st.subheader("Nail-Biting Encounters (Close Margins)")
    st.write("Matches won by 5 runs or less, 3 wickets or less, or tied.")
    close_matches = df[
        ((df['Win_Type'] == 'runs') & (df['Win_Margin'] <= 5) & (df['Win_Margin'] > 0)) |
        ((df['Win_Type'] == 'wickets') & (df['Win_Margin'] <= 3) & (df['Win_Margin'] > 0)) |
        (df['Win_Type'].astype(str).str.lower() == 'draw')
    ]
    close_display = close_matches[
        ['Date', 'Team1', 'Team2', 'Match_Winner', 'Win_Type', 'Win_Margin', 'Venue']
    ].sort_values(by=['Win_Type', 'Win_Margin'])
    st.dataframe(close_display.head(10), use_container_width=True)
    st.divider()

    # venue and toss stats
    st.subheader("Strategic Deep Dive")
    toss_col, venue_col = st.columns([4, 6])

    with toss_col:
        st.markdown("**Toss Decision Preference**")
        toss_summary = (df["Toss_Decision"].value_counts(normalize=True) * 100)
        st.dataframe(toss_summary.rename("Decision %").to_frame().style.format("{:.1f}%"), use_container_width=True)

    with venue_col:
        st.markdown("**Top Venues by Runs Scored**")
        venue_runs = df.groupby("Venue")[["First_Innings_Score", "Second_Innings_Score"]].mean()
        venue_runs["Total Avg Match Runs"] = venue_runs["First_Innings_Score"] + venue_runs["Second_Innings_Score"]
        st.dataframe(
            venue_runs.sort_values(by="Total Avg Match Runs", ascending=False).head(5).style.format("{:.1f}"),
            use_container_width=True
        )
    st.divider()

    # umpire stats
    st.subheader("Umpire Officiating Audit")
    ump_col1, ump_col2 = st.columns(2)

    with ump_col1:
        st.write("**Top Main Umpires**")
        umpire_counts = df['Umpire'].value_counts().head(10).to_frame("Matches Officiated")
        st.dataframe(umpire_counts.style.bar(color='#ffaa00'), use_container_width=True)

    with ump_col2:
        st.write("**Top TV/Third Umpires**")
        umpire2_counts = df['Umpire2'].value_counts().head(10).to_frame("Matches Officiated")
        st.dataframe(umpire2_counts.style.bar(color='#00bfff'), use_container_width=True)

    st.divider()

    # data quality check
    with st.expander("Data Quality & Audit Logs"):
        audit1, audit2 = st.columns(2)
        audit1.write(f"**Duplicate Records**: **{df.duplicated().sum()}**")
        audit2.write(f"**Missing Player of Match Values**: **{df['Player_of_Match'].isna().sum()}**")
        st.info("Missing values in match winner/player of match are expected for abandoned matches or 'No Result'.")
        st.success("Overview Generated From Historical IPL Dataset successfully.")
