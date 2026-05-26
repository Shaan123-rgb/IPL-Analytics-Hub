import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

def show_advanced_analytics(df):
    # shows the deep dive charts
    st.title("Advanced Analytics & Deep Insights")

    # setup filters
    st.markdown("### Deep Dive Filters")
    all_teams = sorted(list(set(df["Team1"].dropna().unique()) | set(df["Team2"].dropna().unique())))
    all_venues = sorted(list(df["Venue"].dropna().unique()))

    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        selected_team = st.selectbox("Focus on Team", ["All"] + all_teams, key="adv_team")
    with filter_col2:
        selected_venue = st.selectbox("Focus on Venue", ["All"] + all_venues, key="adv_venue")

    # filter the data
    adv_df = df.copy()
    if selected_team != "All":
        adv_df = adv_df[(adv_df["Team1"] == selected_team) | (adv_df["Team2"] == selected_team)]
    if selected_venue != "All":
        adv_df = adv_df[adv_df["Venue"] == selected_venue]

    if adv_df.empty:
        st.warning("No data available for the selected filters. Please adjust your criteria.")
        return
        
    st.divider()

    # player of match treemap
    st.subheader("Player of the Match Dominance (Treemap)")
    treemap_data = adv_df.groupby(['Match_Winner', 'Player_of_Match']).size().reset_index(name='Awards')

    top_teams = adv_df['Match_Winner'].value_counts().nlargest(8).index
    treemap_data = treemap_data[treemap_data['Match_Winner'].isin(top_teams)]
    treemap_data = treemap_data[treemap_data['Awards'] > 1]

    if not treemap_data.empty:
        fig_tree = px.treemap(
            treemap_data,
            path=[px.Constant("All Teams"), 'Match_Winner', 'Player_of_Match'],
            values='Awards',
            color='Match_Winner',
            color_discrete_sequence=px.colors.qualitative.Prism 
        )
        fig_tree.update_traces(root_color="lightgrey")
        fig_tree.update_layout(height=600, margin=dict(t=30, l=10, r=10, b=10))
        st.plotly_chart(fig_tree, use_container_width=True)
    else:
        st.info("Not enough player award data to generate a Treemap for this filter.")

    st.divider()

    # team venue heatmap
    st.subheader("Stadium Strengths and Weakness (Team vs Venue Heatmap)")
    heatmap_data = adv_df.groupby(['Match_Winner', 'Venue']).size().reset_index(name='Wins')

    if not heatmap_data.empty:
        pivot_df = heatmap_data.pivot(index='Match_Winner', columns='Venue', values='Wins').fillna(0)

        if pivot_df.shape[1] > 12:
            top_12_venues = pivot_df.sum(axis=0).nlargest(12).index
            pivot_df = pivot_df[top_12_venues]

        fig_heat = px.imshow(
            pivot_df,
            text_auto=True,
            aspect="auto",
            color_continuous_scale="YlOrRd", 
            labels=dict(x="Venue", y="Winning Team", color="Total Wins")
        )
        fig_heat.update_layout(height=600, xaxis={'tickangle': 35})
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.info("No venue dominance data available.")

    st.divider()

    # sankey for toss decisions
    st.subheader("The Toss Advantage Flow (Sankey Diagram)")
    st.markdown("Traces the flow of what happens after the coin toss. Does deciding to bat or bowl actually lead to victory?")

    bat_win = len(adv_df[(adv_df['Toss_Decision'].astype(str).str.lower() == 'bat') & (adv_df['Toss_Winner'] == adv_df['Match_Winner'])])
    bat_loss = len(adv_df[(adv_df['Toss_Decision'].astype(str).str.lower() == 'bat') & (adv_df['Toss_Winner'] != adv_df['Match_Winner'])])
    bowl_win = len(adv_df[(adv_df['Toss_Decision'].astype(str).str.lower() == 'bowl') & (adv_df['Toss_Winner'] == adv_df['Match_Winner'])])
    bowl_loss = len(adv_df[(adv_df['Toss_Decision'].astype(str).str.lower() == 'bowl') & (adv_df['Toss_Winner'] != adv_df['Match_Winner'])])

    if (bat_win + bat_loss + bowl_win + bowl_loss) > 0:
        fig_sankey = go.Figure(data=[go.Sankey(
            node=dict(
                pad=30,
                thickness=30,
                line=dict(color="black", width=1),
                label=["Decided to Bat", "Decided to Bowl", "Toss Winner Won Match", "Toss Winner Lost Match"],
                color=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
            ),
            link=dict(
                source=[0, 0, 1, 1],
                target=[2, 3, 2, 3],
                value=[bat_win, bat_loss, bowl_win, bowl_loss],
                color=["rgba(44, 160, 44, 0.4)", "rgba(214, 39, 40, 0.4)", "rgba(44, 160, 44, 0.4)", "rgba(214, 39, 40, 0.4)"]
            )
        )])
        fig_sankey.update_layout(height=500, font=dict(size=14))
        st.plotly_chart(fig_sankey, use_container_width=True)
    else:
        st.info("Not enough toss data to generate a Sankey flow.")

    st.divider()

    # violin plot for scoring distribution
    st.subheader("Team Scoring Densities (Violin Plot)")
    top_teams_violin = adv_df['Team1'].value_counts().nlargest(8).index
    violin_df = adv_df[(adv_df['Team1'].isin(top_teams_violin)) & (adv_df['First_Innings_Score'] > 0)]

    if not violin_df.empty:
        fig_violin = px.violin(
            violin_df,
            x="Team1",
            y="First_Innings_Score",
            color="Team1",
            box=True,
            points="all",
            labels={"Team1": "Batting Team", "First_Innings_Score": "1st Innings Total"}
        )
        fig_violin.update_layout(height=600, showlegend=False, xaxis={'tickangle': 25})
        st.plotly_chart(fig_violin, use_container_width=True)
    else:
        st.info("Not enough score data for this selection.")

    st.divider()
    
    # sunburst for win methods
    st.subheader("Team Victory Chart (Sunburst Chart)")

    sunburst_df = adv_df.dropna(subset=['Match_Winner', 'Win_Type', 'Toss_Winner']).copy()
    if not sunburst_df.empty:
        sunburst_df['Win_Method'] = sunburst_df['Win_Type'].astype(str).str.lower().map({
            'runs': 'Defended Target',
            'wickets': 'Chased Target',
            'tie': 'Super Over / Tie'
        }).fillna('Other')

        won_toss = sunburst_df['Toss_Winner'] == sunburst_df['Match_Winner']
        defended = sunburst_df['Win_Method'] == 'Defended Target'
        chased = sunburst_df['Win_Method'] == 'Chased Target'

        conditions = [
            defended & won_toss,
            defended & ~won_toss,
            chased & won_toss,
            chased & ~won_toss
        ]
        outcomes = [
            'Won Toss (Chose Bat)',
            'Lost Toss (Forced to Bat)',
            'Won Toss (Chose Bowl)',
            'Lost Toss (Forced to Bowl)'
        ]

        sunburst_df['Toss_Impact'] = np.select(conditions, outcomes, default='Unknown / Tie')

        if selected_team == "All":
            top_teams = sunburst_df['Match_Winner'].value_counts().nlargest(6).index
            sunburst_df = sunburst_df[sunburst_df['Match_Winner'].isin(top_teams)]

        sun_data = sunburst_df.groupby(['Match_Winner', 'Win_Method', 'Toss_Impact']).size().reset_index(name='Wins')

        fig_sun = px.sunburst(
            sun_data,
            path=['Match_Winner', 'Win_Method', 'Toss_Impact'],
            values='Wins',
            color='Match_Winner',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_sun.update_traces(textinfo="label+percent parent", insidetextorientation='radial')
        fig_sun.update_layout(height=650, margin=dict(t=20, l=10, r=10, b=10))
        st.plotly_chart(fig_sun, use_container_width=True)
    else:
        st.info("No victory blueprint data available.")
