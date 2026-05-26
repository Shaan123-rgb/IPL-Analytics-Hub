import streamlit as st

def show_data_assistant(df):
    # a simple bot to answer queries
    st.title("IPL Data Assistant")
    st.markdown("Type what you want to know! Try: *'highest score'*, *'most wins'*, *'CSK vs MI'*, or just *'RCB'*.")

    raw_query = st.text_input("Search", placeholder="Type your keywords here...").lower().strip()
    st.divider()

    if not raw_query:
        return

    # shortcuts for team names so users don't have to type full names
    shortcuts = {
        "csk": "chennai", "mi": "mumbai", "rcb": "challengers", "kkr": "kolkata",
        "srh": "hyderabad", "dc": "delhi", "rr": "rajasthan", "pbks": "punjab",
        "kxip": "punjab", "lsg": "lucknow", "gt": "titans"
    }

    words = [shortcuts.get(w, w) for w in raw_query.split()]
    query = " ".join(words)

    if "highest" in query or "record" in query:
        st.success("**Tournament Highest Score**")
        highest = max(df['First_Innings_Score'].max(), df['Second_Innings_Score'].max())
        st.metric("Highest Historic Score", f"{int(highest)} Runs")

    elif "most wins" in query or "successful" in query:
        st.success("**Most Successful Teams**")
        st.bar_chart(df['Match_Winner'].value_counts().head(5))

    elif "player" in query or "pom" in query:
        st.success("**Top Players of the Match**")
        st.dataframe(df['Player_of_Match'].value_counts().head(10).reset_index(name='Awards'), hide_index=True)

    elif "toss" in query:
        st.success("**The Toss Advantage**")
        toss_wins = len(df[df['Toss_Winner'] == df['Match_Winner']])
        total = len(df.dropna(subset=['Toss_Winner', 'Match_Winner']))
        st.metric("Toss Win ➔ Match Win Rate", f"{(toss_wins / total) * 100:.1f}%")

    elif "vs" in query:
        teams = query.split("vs")
        if len(teams) == 2:
            t1, t2 = teams[0].strip(), teams[1].strip()
            h2h = df[
                (df['Team1'].str.contains(t1, case=False) & df['Team2'].str.contains(t2, case=False)) |
                (df['Team1'].str.contains(t2, case=False) & df['Team2'].str.contains(t1, case=False))
            ]

            if not h2h.empty:
                st.success(f"**Head-to-Head Matchup**")
                c1, c2, c3 = st.columns(3)
                c1.metric("Total Matches", len(h2h))
                c2.metric("Team 1 Wins", len(h2h[h2h['Match_Winner'].str.contains(t1, case=False, na=False)]))
                c3.metric("Team 2 Wins", len(h2h[h2h['Match_Winner'].str.contains(t2, case=False, na=False)]))

                st.dataframe(h2h[["Date", "Match_Winner", "Win_Margin", "Player_of_Match"]].head(10), use_container_width=True)
            else:
                st.info("No matches found between these teams. Try typing their full names.")
        else:
            st.info("Please format your vs query like: 'team1 vs team2'.")

    else:
        # just look for the team name
        team_df = df[df["Team1"].str.contains(query, case=False) | df["Team2"].str.contains(query, case=False)]

        if not team_df.empty:
            # get the actual full name
            matches_team1 = team_df[team_df["Team1"].str.contains(query, case=False)]["Team1"]
            if not matches_team1.empty:
                real_name = matches_team1.iloc[0]
            else:
                real_name = team_df[team_df["Team2"].str.contains(query, case=False)]["Team2"].iloc[0]
                
            st.success(f"**Team Overview: {real_name}**")

            wins = len(team_df[team_df["Match_Winner"].str.contains(query, case=False, na=False)])

            c1, c2 = st.columns(2)
            c1.metric("Matches Played", len(team_df))
            c2.metric("Total Wins", wins)

            st.dataframe(team_df[["Date", "Team1", "Team2", "Match_Winner"]].head(10), use_container_width=True)
        else:
            st.warning("Keyword not recognizable. Try keywords like 'highest score' or a team's name.")
