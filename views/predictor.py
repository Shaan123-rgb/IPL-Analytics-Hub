import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

@st.cache_resource
def train_model(df):
    # filter out matches with no result or ties for simpler prediction
    valid_data = df[~df['Match_Winner'].isna()].copy()
    valid_data = valid_data[valid_data['Win_Type'].str.lower() != 'draw']

    # we just need basic info to predict
    features = ['Team1', 'Team2', 'Venue', 'Toss_Winner', 'Toss_Decision']
    X = valid_data[features].copy()
    y = valid_data['Match_Winner'].copy()

    # encode strings to numbers so the model can read them
    encoders = {}
    for col in features:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col])
        encoders[col] = le
        
    # encode the target too
    target_encoder = LabelEncoder()
    y = target_encoder.fit_transform(y)

    # use random forest classifier because it handles categorical data really well
    # heavily constrained to force realistic, balanced probabilities (e.g. 55 vs 45 instead of 95 vs 5)
    model = RandomForestClassifier(
        n_estimators=200, 
        max_depth=3, 
        min_samples_split=20, 
        min_samples_leaf=20,
        random_state=42
    )
    model.fit(X, y)

    return model, encoders, target_encoder

def show_predictor(df):
    st.title("Match Predictor")
    st.write("Predict the outcome of a match based on past data.")
    
    # get the trained model and encoders
    model, encoders, target_encoder = train_model(df)
    
    # get unique lists for dropdowns
    all_teams = sorted(list(set(df["Team1"].dropna().unique()) | set(df["Team2"].dropna().unique())))
    all_venues = sorted(list(df["Venue"].dropna().unique()))
    
    st.markdown("### Match Setup")
    
    col1, col2 = st.columns(2)
    with col1:
        team1 = st.selectbox("Team 1", all_teams, index=0)
    with col2:
        team2 = st.selectbox("Team 2", all_teams, index=1 if len(all_teams)>1 else 0)
        
    if team1 == team2:
        st.warning("select two different teams")
        return
        
    venue = st.selectbox("Venue", all_venues)
    
    c3, c4 = st.columns(2)
    with c3:
        toss_winner = st.selectbox("Toss Winner", [team1, team2])
    with c4:
        toss_decision = st.selectbox("Toss Decision", ["bat", "bowl"])
        
    st.divider()
    
    if st.button("Predict Match Winner", type="primary", use_container_width=True):
        try:
            # prepare the input data
            input_df = pd.DataFrame({
                'Team1': [team1],
                'Team2': [team2],
                'Venue': [venue],
                'Toss_Winner': [toss_winner],
                'Toss_Decision': [toss_decision]
            })
            
            # encode input
            for col in input_df.columns:
                le = encoders[col]
                # handle unseen labels just in case
                if input_df[col].iloc[0] not in le.classes_:
                    input_df[col] = le.transform([le.classes_[0]])
                else:
                    input_df[col] = le.transform(input_df[col])
                    
            # get probabilities
            probs = model.predict_proba(input_df)[0]
            
            # get the actual class names
            classes = target_encoder.classes_
            
            # find index of team1 and team2 in the classes
            if team1 in classes and team2 in classes:
                idx1 = list(classes).index(team1)
                idx2 = list(classes).index(team2)
                
                prob1 = probs[idx1] * 100
                prob2 = probs[idx2] * 100
                
                # normalize so they add up to 100 exactly (ignoring other teams)
                total = prob1 + prob2
                if total > 0:
                    prob1 = (prob1 / total) * 100
                    prob2 = (prob2 / total) * 100
                
                st.subheader("Prediction Results")
                
                res1, res2 = st.columns(2)
                with res1:
                    st.metric(team1, f"{prob1:.1f}%")
                with res2:
                    st.metric(team2, f"{prob2:.1f}%")
                    
                # show progress bar
                st.progress(int(prob1))
                
                if prob1 > prob2:
                    st.success(f"{team1} is favored to win!")
                elif prob2 > prob1:
                    st.success(f"{team2} is favored to win!")
                else:
                    st.info("It's too close to call!")
            else:
                st.error("Not enough historical data for these specific teams.")
                
        except Exception as e:
            st.error(f"Something went wrong with prediction: {e}")
