import streamlit as st
import pandas as pd
import plotly.express as px

def show_team_comparison(df):
    # shows head to head stats between two teams
    st.title("Head-to-Head Team Comparison")

    # setup filters
    st.markdown("### Select Teams to Compare")
    all_teams = sorted(list(set(df["Team1"].dropna().unique()) | set(df["Team2"].dropna().unique())))

    col1, col2 = st.columns(2)
    with col1:
        team_a = st.selectbox("Select Team A", all_teams, index=0)
    with col2:
        default_idx = 1 if len(all_teams) > 1 else 0
        team_b = st.selectbox("Select Team B", all_teams, index=default_idx)

    if team_a == team_b:
        st.warning("Please select two different teams to see the comparison.")
        return

    st.divider()
    stats = {}

    # calc stats for each team
    for t in [team_a, team_b]:
        stats[t] = {}

        matches = df[(df['Team1'] == t) | (df['Team2'] == t)]
        played = len(matches)

        stats[t]['wins'] = len(df[df['Match_Winner'] == t])
        stats[t]['win_rate'] = (stats[t]['wins'] / played * 100) if played > 0 else 0
        stats[t]['toss_rate'] = (len(df[df['Toss_Winner'] == t]) / played * 100) if played > 0 else 0

        stats[t]['max_run_win'] = df[(df['Match_Winner'] == t) & (df['Win_Type'].astype(str).str.lower() == 'runs')]['Win_Margin'].max()
        stats[t]['max_wic_win'] = df[(df['Match_Winner'] == t) & (df['Win_Type'].astype(str).str.lower() == 'wickets')]['Win_Margin'].max()

        poms = df[df['Match_Winner'] == t]['Player_of_Match'].value_counts()
        stats[t]['top_pom'] = poms.index[0] if not poms.empty else "N/A"
        stats[t]['pom_count'] = poms.iloc[0] if not poms.empty else 0

        won_toss = matches['Toss_Winner'] == t
        chose_bat = matches['Toss_Decision'].astype(str).str.lower() == 'bat'
        chose_bowl = matches['Toss_Decision'].astype(str).str.lower().isin(['bowl', 'field'])

        bat_first = matches[(won_toss & chose_bat) | (~won_toss & chose_bowl)]
        bat_second = matches[(won_toss & chose_bowl) | (~won_toss & chose_bat)]

        h1 = bat_first['First_Innings_Score'].max()
        h2 = bat_second['Second_Innings_Score'].max()
        stats[t]['highest_score'] = int(max(h1 if pd.notna(h1) else 0, h2 if pd.notna(h2) else 0))

        pp1 = [f'innings_1_over_{i}' for i in range(1, 7) if f'innings_1_over_{i}' in bat_first.columns]
        mid1 = [f'innings_1_over_{i}' for i in range(7, 16) if f'innings_1_over_{i}' in bat_first.columns]
        death1 = [f'innings_1_over_{i}' for i in range(16, 21) if f'innings_1_over_{i}' in bat_first.columns]

        pp2 = [f'innings_2_over_{i}' for i in range(1, 7) if f'innings_2_over_{i}' in bat_second.columns]
        mid2 = [f'innings_2_over_{i}' for i in range(7, 16) if f'innings_2_over_{i}' in bat_second.columns]
        death2 = [f'innings_2_over_{i}' for i in range(16, 21) if f'innings_2_over_{i}' in bat_second.columns]

        pp_runs = bat_first[pp1].sum(axis=1).sum() + bat_second[pp2].sum(axis=1).sum()
        mid_runs = bat_first[mid1].sum(axis=1).sum() + bat_second[mid2].sum(axis=1).sum()
        death_runs = bat_first[death1].sum(axis=1).sum() + bat_second[death2].sum(axis=1).sum()
        total_runs = bat_first['First_Innings_Score'].sum() + bat_second['Second_Innings_Score'].sum()

        innings_count = len(bat_first) + len(bat_second)
        stats[t]['avg_pp'] = pp_runs / innings_count if innings_count > 0 else 0
        stats[t]['avg_mid'] = mid_runs / innings_count if innings_count > 0 else 0
        stats[t]['avg_death'] = death_runs / innings_count if innings_count > 0 else 0
        stats[t]['avg_total'] = total_runs / innings_count if innings_count > 0 else 0

    # show overall franchise legacy
    st.subheader("Franchise Legacy & Historic Milestones")
    st.markdown("Comparing their overall performance against all teams across the tournament's history.")

    leg_col1, leg_col2 = st.columns(2)

    with leg_col1:
        st.info(f"**🛡️ {team_a}**")
        c1, c2 = st.columns(2)
        c1.metric("Overall Tournament Wins", stats[team_a]['wins'])
        c2.metric("Toss Win Rate", f"{stats[team_a]['toss_rate']:.1f}%")
        c3, c4 = st.columns(2)
        c3.metric("Highest Historic Score", f"{stats[team_a]['highest_score']} Runs")
        c4.metric("Biggest Win Margin", f"{stats[team_a]['max_run_win']} Runs / {stats[team_a]['max_wic_win']} Wkts")
        st.metric("Top Player of the Match", f"{stats[team_a]['top_pom']}", f"{stats[team_a]['pom_count']} Awards", delta_color="off")

    with leg_col2:
        st.success(f"**⚔️ {team_b}**")
        c5, c6 = st.columns(2)
        c5.metric("Overall Tournament Wins", stats[team_b]['wins'])
        c6.metric("Toss Win Rate", f"{stats[team_b]['toss_rate']:.1f}%")
        c7, c8 = st.columns(2)
        c7.metric("Highest Historic Score", f"{stats[team_b]['highest_score']} Runs")
        c8.metric("Biggest Win Margin", f"{stats[team_b]['max_run_win']} Runs / {stats[team_b]['max_wic_win']} Wkts")
        st.metric("Top Player of the Match", f"{stats[team_b]['top_pom']}", f"{stats[team_b]['pom_count']} Awards", delta_color="off")

    st.divider()

    # head to head matchup stats
    st.subheader(f"Direct Rivalry: {team_a} vs {team_b}")
    h2h_df = df[((df['Team1'] == team_a) & (df['Team2'] == team_b)) | ((df['Team1'] == team_b) & (df['Team2'] == team_a))]

    if not h2h_df.empty:
        total_matches = len(h2h_df)
        team_a_h2h_wins = len(h2h_df[h2h_df['Match_Winner'] == team_a])
        team_b_h2h_wins = len(h2h_df[h2h_df['Match_Winner'] == team_b])
        ties_no_result = total_matches - (team_a_h2h_wins + team_b_h2h_wins)

        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Total H2H Matches", total_matches)
        kpi2.metric(f"{team_a} Direct Wins", team_a_h2h_wins)
        kpi3.metric(f"{team_b} Direct Wins", team_b_h2h_wins)

        h2h_wins = pd.DataFrame({'Team': [team_a, team_b, 'Tie/No Result'], 'Wins': [team_a_h2h_wins, team_b_h2h_wins, ties_no_result]})
        h2h_wins = h2h_wins[h2h_wins['Wins'] > 0]

        fig_h2h = px.pie(h2h_wins, names='Team', values='Wins', hole=0.4, color='Team',
                         color_discrete_map={team_a: '#1f77b4', team_b: '#2ca02c', 'Tie/No Result': 'grey'})
        fig_h2h.update_layout(height=400, showlegend=True, margin=dict(t=10, b=10))
        fig_h2h.update_traces(textposition='inside', textinfo='label+percent')
    else:
        st.info(f"Historical Data Check: {team_a} and {team_b} have not played against each other in this dataset.")
        fig_h2h = None

    st.divider()

    # team dna radar chart
    st.subheader("Overall Team DNA (Radar Chart)")
    st.markdown("Shows the structural strengths of both teams against a 'Perfect T20 Standard'.")

    radar_data = []
    for t in [team_a, team_b]:
        radar_data.append({
            'Team': t,
            'Win Rate (%)': stats[t]['win_rate'],
            'Powerplay Aggression': min((stats[t]['avg_pp'] / 70) * 100, 100),
            'Middle Overs Anchor': min((stats[t]['avg_mid'] / 110) * 100, 100),
            'Death Overs Finisher': min((stats[t]['avg_death'] / 65) * 100, 100),
            'Total Scoring Power': min((stats[t]['avg_total'] / 230) * 100, 100)
        })

    radar_df = pd.DataFrame(radar_data)
    radar_melted = radar_df.melt(id_vars=['Team'], var_name='Metric', value_name='Score (out of 100)')

    r1, r2 = st.columns([1.5, 1])
    with r1:
        fig_radar = px.line_polar(
            radar_melted, r='Score (out of 100)', theta='Metric', color='Team',
            line_close=True, markers=True, range_r=[0, 100],
            color_discrete_map={team_a: '#1f77b4', team_b: '#2ca02c'}
        )
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, showticklabels=False, range=[0, 100])),
                                height=450, margin=dict(t=30, b=30, l=40, r=40),
                                legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5))
        fig_radar.update_traces(fill='toself', fillcolor='rgba(0,0,0,0.1)')
        st.plotly_chart(fig_radar, use_container_width=True)

    with r2:
        if fig_h2h:
            st.markdown(f"**Direct Matchups Share**")
            st.plotly_chart(fig_h2h, use_container_width=True)
        else:
            st.empty()

    st.divider()

    # raw scoring bar chart and box plot
    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Raw Scoring by Phase")
        st.markdown("A direct comparison of the actual average runs scored by each team during specific match phases.")
        
        raw_scores_df = pd.DataFrame([
            {'Team': team_a, 'Powerplay (1-6)': stats[team_a]['avg_pp'],
             'Middle Overs (7-15)': stats[team_a]['avg_mid'], 'Death Overs (16-20)': stats[team_a]['avg_death']},
            {'Team': team_b, 'Powerplay (1-6)': stats[team_b]['avg_pp'],
             'Middle Overs (7-15)': stats[team_b]['avg_mid'], 'Death Overs (16-20)': stats[team_b]['avg_death']}
        ]).melt(id_vars=['Team'], var_name='Match Phase', value_name='Average Runs')

        fig_bar = px.bar(
            raw_scores_df, x='Match Phase', y='Average Runs', color='Team', barmode='group',
            text_auto='.1f', color_discrete_map={team_a: '#1f77b4', team_b: '#2ca02c'}
        )
        fig_bar.update_layout(height=450, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_bar, use_container_width=True)

    with c4:
        st.subheader("Dominance Spread (Win Margins)")
        st.markdown("When these teams win, how hard do they crush the opposition? Shows the spread of victory margins.")

        margins_df = df[df['Match_Winner'].isin([team_a, team_b])].dropna(subset=['Win_Margin', 'Win_Type'])
        if not margins_df.empty:
            fig_box = px.box(
                margins_df, x="Win_Type", y="Win_Margin", color="Match_Winner", points="outliers",
                color_discrete_map={team_a: '#1f77b4', team_b: '#2ca02c'},
                labels={'Win_Type': 'Victory Method', 'Win_Margin': 'Margin of Victory', 'Match_Winner': 'Winning Team'}
            )
            fig_box.update_layout(height=450, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig_box, use_container_width=True)
        else:
            st.info("No victory margin data available for these teams.")
