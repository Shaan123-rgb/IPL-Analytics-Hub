import streamlit as st
import pandas as pd
import plotly.express as px

def show_analytics_dashboard(df):
    # shows the main analytics dashboard with filters
    st.title("IPL Analytics Dashboard")
    st.markdown("### Dashboard Filters")

    # set up filters
    all_teams = sorted(list(set(df["Team1"].dropna().unique()) | set(df["Team2"].dropna().unique())))
    all_venues = sorted(list(df["Venue"].dropna().unique()))

    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        selected_team = st.selectbox("Filter by Team", ["All"] + all_teams)
    with filter_col2:
        selected_venue = st.selectbox("Filter by Venue", ["All"] + all_venues)

    # apply the filters to the dataframe
    dashboard_df = df.copy()
    if selected_team != "All":
        dashboard_df = dashboard_df[(dashboard_df["Team1"] == selected_team) | (dashboard_df["Team2"] == selected_team)]
    if selected_venue != "All":
        dashboard_df = dashboard_df[dashboard_df["Venue"] == selected_venue]

    if dashboard_df.empty:
        st.warning("No data available for the selected filters. Please adjust your filter selections.")
        return

    st.divider()

    # get the big numbers for the top
    highest_chase = dashboard_df[dashboard_df["Win_Type"] == "wickets"]["Second_Innings_Score"].max()
    avg_1st_score = dashboard_df["First_Innings_Score"].mean()
    avg_pp_score = dashboard_df["Powerplay_Scores"].mean()
    avg_death_score = dashboard_df["Death_Overs_Scores"].mean()

    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    # fix na values if the filter is too strict
    highest_chase_str = f"{highest_chase:.0f} Runs" if pd.notna(highest_chase) else "N/A"
    avg_1st_score_str = f"{avg_1st_score:.0f} Runs" if pd.notna(avg_1st_score) else "N/A"
    avg_pp_score_str = f"{avg_pp_score:.1f} Runs" if pd.notna(avg_pp_score) else "N/A"
    avg_death_score_str = f"{avg_death_score:.1f} Runs" if pd.notna(avg_death_score) else "N/A"

    kpi_col1.metric("Highest Successful Chase", highest_chase_str)
    kpi_col2.metric("Average 1st Innings Score", avg_1st_score_str)
    kpi_col3.metric("Avg Powerplay Score", avg_pp_score_str)
    kpi_col4.metric("Avg Death Overs Score", avg_death_score_str)

    st.divider()

    # charts for wins and toss decisions
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Most Successful Teams (By Wins)")
        team_wins = dashboard_df["Match_Winner"].value_counts().head(17)
        if not team_wins.empty:
            fig_bar = px.bar(
                x=team_wins.index, 
                y=team_wins.values,
                color=team_wins.index,
                labels={"x": "Team", "y": "Wins"}
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No Win data available for this filter")

    with c2:
        st.subheader("Toss Decision Distribution")
        if selected_team != "All":
            toss_df = dashboard_df[dashboard_df["Toss_Winner"] == selected_team]
            st.caption(f"Showing decisions for **{selected_team}** when they won the toss")
        else:
            toss_df = dashboard_df
            st.caption("Showing decision for **All Teams**.")
            
        decision_counts = toss_df["Toss_Decision"].value_counts()
        if not decision_counts.empty:
            fig_toss = px.pie(
                decision_counts, 
                names=decision_counts.index, 
                values=decision_counts.values, 
                hole=0.4
            )
            st.plotly_chart(fig_toss, use_container_width=True)
        else:
            st.info("No Toss Data available for this filter")
            
    st.divider()

    # charts for win types and top players
    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Match Win Type Distribution")
        win_types = dashboard_df["Win_Type"].value_counts()
        if not win_types.empty:
            fig_win_type = px.pie(
                win_types, 
                names=win_types.index, 
                values=win_types.values,
                hole=0.4, 
                color_discrete_sequence=px.colors.sequential.Teal
            )
            st.plotly_chart(fig_win_type, use_container_width=True)
        else:
            st.info("No win type data available")

    with c4:
        st.subheader("Top 10 Players of the Match")
        top_players = dashboard_df["Player_of_Match"].value_counts().head(10)
        if not top_players.empty:
            fig_players = px.bar(
                x=top_players.values, 
                y=top_players.index,
                orientation="h", 
                labels={"x": "Number of POM Awards", "y": "Player"},
                color=top_players.values,
                color_continuous_scale="Viridis",
                text_auto=True
            )
            fig_players.update_layout(yaxis={"categoryorder":"total ascending"}, showlegend=False)
            st.plotly_chart(fig_players, use_container_width=True)
        else:
            st.info("No player award data available")

    st.divider()
    
    # timeline of wins over the years
    st.subheader("Year-over-Year Team Wins")
    st.markdown("Tracks the total number of wins per season. *Tip: Click on a team in the legend to isolate their trend!*")

    timeline_df = dashboard_df.copy()
    timeline_df['Year'] = pd.to_datetime(timeline_df['Date'], errors='coerce').dt.year
    timeline_df = timeline_df.dropna(subset=['Year'])
    timeline_df['Year'] = timeline_df['Year'].astype(int)

    if not timeline_df.empty:
        yearly_wins = timeline_df.groupby(['Year', 'Match_Winner']).size().reset_index(name='Wins')
        fig_line = px.line(
            yearly_wins, 
            x="Year", 
            y="Wins", 
            color="Match_Winner",
            markers=True, 
            labels={"Wins": "Total Match Wins", "Year": "Season(Year)", "Match_Winner": "Team"},
            color_discrete_sequence=px.colors.qualitative.Set1
        )
        fig_line.update_layout(
            xaxis=dict(dtick=1),
            hovermode="x unified",
            height=550,
            margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(title=None, orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("No valid chronological data available to plot year over year trends")

    st.divider()

    # box plot for stadium scores
    st.subheader("Venue Par Scores & Consistency")
    st.markdown("Box plot showing the spread of 1st Innings scores to determine typical pitch behavior.")

    if not dashboard_df["First_Innings_Score"].dropna().empty:
        if 'Year' not in dashboard_df.columns:
            dashboard_df['Year'] = pd.to_datetime(dashboard_df['Date'], errors='coerce').dt.year
            dashboard_df['Year'] = dashboard_df['Year'].fillna(0).astype(int)

        if selected_venue == "All":
            top_venues = dashboard_df['Venue'].value_counts().nlargest(6).index
            box_df = dashboard_df[dashboard_df['Venue'].isin(top_venues)]
            st.caption("Showing Top 6 Venues by matches played.")
        else:
            box_df = dashboard_df
            st.caption(f"Showing distribution for {selected_venue}")

        fig_box = px.box(
            box_df, 
            x="Venue", 
            y="First_Innings_Score", 
            color="Venue",
            points="outliers",  
            labels={'Venue': 'Stadium', 'First_Innings_Score': '1st Innings Total', 'Year': 'Season'},
            hover_data=["Team1", "Team2", "Year"]
        )
        fig_box.update_layout(showlegend=False, xaxis={'tickangle': 45})
        fig_box.update_yaxes(rangemode="tozero")
        
        st.plotly_chart(fig_box, use_container_width=True)
    else:
        st.info("No innings score data available.")
