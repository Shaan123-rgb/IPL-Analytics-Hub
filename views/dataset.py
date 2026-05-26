import streamlit as st

def show_dataset(df):
    # shows the dataset explorer page
    st.title("Dataset Explorer")
    st.divider()

    # top kpis
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Rows:", df.shape[0])
    col2.metric("Total Columns:", df.shape[1])
    col3.metric("Missing Value", df.isna().sum().sum())
    
    st.divider()

    # column selection
    st.subheader("Select Columns")
    selected_columns = st.multiselect(
        "Choose columns to Display",
        df.columns, 
        default=df.columns
    )
    filtered_df = df[selected_columns]

    # search bar
    st.subheader("Search in Dataset")
    search_value = st.text_input("Search any value")
    if search_value:
        filtered_df = filtered_df[filtered_df.astype(str).apply(
            lambda row: row.str.contains(search_value, case=False).any(), axis=1
        )]

    # filter by specific column
    st.subheader("Column Filter")
    col1, col2 = st.columns(2)
    with col1:
        filter_column = st.selectbox("Select Column", filtered_df.columns)
    with col2:
        # Dropna to avoid passing NaN values to the dropdown
        filter_value = st.selectbox("Select Value", filtered_df[filter_column].dropna().unique())

    if st.button("Apply Filter"):
        filtered_df = filtered_df[filtered_df[filter_column] == filter_value]
        
    st.divider()

    # data table
    st.subheader("Row Display")
    row = st.slider("Number of rows to display", 10, len(filtered_df), 100)
    st.divider()

    st.subheader("Dataset Table")
    st.dataframe(filtered_df.head(row), use_container_width=True)

    if st.checkbox("Show full Dataset"):
        st.dataframe(filtered_df, use_container_width=True)
        
    st.divider()

    # stats for numeric columns
    st.subheader("Column Statistics")
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns

    if len(numeric_cols) > 0:
        selected_col = st.selectbox("Select Numeric Column", numeric_cols)
        st.write(filtered_df[selected_col].describe())
        
    st.divider()

    # download button
    st.subheader("Download Data")
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Filtered Dataset", 
        data=csv, 
        file_name="filtered_ipl_dataset.csv", 
        mime="text/csv"
    )
