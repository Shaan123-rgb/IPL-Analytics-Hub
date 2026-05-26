# IPL Data Analytics Hub

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B)
![Scikit-Learn](https://img.shields.io/badge/Machine%20Learning-Scikit--Learn-F7931E)
![Pandas](https://img.shields.io/badge/Data-Pandas-150458)

A comprehensive, interactive, and beautifully designed web dashboard built with **Streamlit** to analyze the complete historical data of the Indian Premier League (IPL). This project features deep analytical insights, granular ball-by-ball player matchups, and a Machine Learning predictor for match outcomes.

---

## Key Features

The dashboard is divided into several highly focused modules:

- **Home**: A premium dark-themed landing page summarizing the tournament's overall scale and massive aggregate statistics.
- **Dataset Explorer**: Search, filter, sort, and download the raw historical IPL match data.
- **Tournament Overview**: High-level strategic KPIs, match phase efficiencies (Powerplay vs Death Overs), umpire audits, and venue statistics.
- **Analytics Dashboard**: Deep dive into seasonal trends, toss decision impacts, victory types (runs vs wickets), and par scores across different stadiums.
- **Advanced Analytics**: Beautiful interactive visualizations utilizing Plotly Treemaps, Heatmaps, Sankey Diagrams, and Violin plots for granular insights.
- **Team Comparison**: Head-to-head legacy statistics and direct matchup win records between any two IPL franchises.
- **Player Matchups (Ball-by-Ball)**: Powered by a massive ~260,000+ row dataset, this tool pits specific batsmen against specific bowlers to show exact runs scored, strike rates, dot ball percentages, and wickets taken.
- **Match Predictor**: An embedded **Random Forest Classifier** that takes inputs like Venue, Toss Winner, and Teams to instantly predict the win probability using tuned, regularized historical data.
- **Data Assistant**: A built-in natural language querying tool allowing users to ask simple questions (e.g., "highest score", "CSK vs MI") and get instant statistical answers.

---

## Technology Stack

- **Frontend & UI**: Streamlit, Custom CSS (IPL Dark Theme)
- **Data Manipulation**: Pandas, NumPy
- **Data Visualization**: Plotly Express, Plotly Graph Objects
- **Machine Learning**: Scikit-Learn (`RandomForestClassifier`, `LabelEncoder`)

---

## Project Structure

```text
ipl_data/
│
├── ipl.py                        # Main router and entry point for the Streamlit app
├── data_loader.py                # Data ingestion, cleaning, and caching logic
├── style.css                     # Custom CSS for the premium IPL dark theme
├── requirements.txt              # Project dependencies
├── IPL.csv                       # Core dataset (Match-level summaries)
├── deliveries.csv                # Granular dataset (~260k rows of ball-by-ball data)
│
├── .streamlit/
│   └── config.toml               # Native Streamlit dark mode configuration
│
└── views/                        # Modular UI components
    ├── home.py
    ├── dataset.py
    ├── overview.py
    ├── analytics_dashboard.py
    ├── advanced_analytics.py
    ├── team_comparison.py
    ├── player_matchups.py
    ├── predictor.py
    └── data_assistant.py
```

---

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/ipl-analytics-hub.git
   cd ipl-analytics-hub
   ```

2. **Create a virtual environment (Recommended):**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application:**
   ```bash
   streamlit run ipl.py
   ```

---

## Machine Learning Details
The **Match Predictor** utilizes a `RandomForestClassifier` trained on historical match conditions (Venue, Toss Decision, Toss Winner, Team 1, Team 2). 
To prevent the model from overfitting (simply memorizing past unique matchups), the tree is heavily regularized (`max_depth=3`, `min_samples_leaf=20`), forcing it to learn general winning trends rather than outputting biased 100% probabilities.

---

*Note: Ensure both `IPL.csv` and `deliveries.csv` are placed in the root directory before running the application.*
