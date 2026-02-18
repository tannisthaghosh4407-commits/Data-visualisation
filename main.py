import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="My Organized Dashboard")
st.title("My Organized Dashboard")

if "chart_type" not in st.session_state:
    st.session_state.chart_type = "Bar Chart"

with st.sidebar:
    file = st.file_uploader("Upload a csv or xlsx file", type=["csv", "xlsx"])

if file is not None:
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file, engine="openpyxl")
else:
    st.info("Please upload a file to proceed.")
    st.stop()


def all_features(feature: str, data_frame: pd.DataFrame) -> pd.DataFrame:
    temp_data = data_frame.copy()

    if feature == "Handling Missing Data":
        method = st.selectbox(
            "How do you want to handle?",
            ["Do nothing", "Drop that Row", "With Mean", "With Median",
             "With Standard Deviation", "With Mode",
             "Data From Previous Row", "Data From Next Row"],
            key="missing_method",
        )
        if method == "Do nothing":
            pass
        elif method == "Drop that Row":
            temp_data.dropna(inplace=True)
        elif method == "With Mean":
            temp_data.fillna(temp_data.mean(numeric_only=True), inplace=True)
        elif method == "With Median":
            temp_data.fillna(temp_data.median(numeric_only=True), inplace=True)
        elif method == "With Standard Deviation":
            temp_data.fillna(temp_data.std(numeric_only=True), inplace=True)
        elif method == "With Mode":
            mode_vals = temp_data.mode(numeric_only=True)
            if not mode_vals.empty:
                temp_data.fillna(mode_vals.iloc[0], inplace=True)
        elif method == "Data From Previous Row":
            temp_data.ffill(inplace=True)
        elif method == "Data From Next Row":
            temp_data.bfill(inplace=True)

    elif feature == "Groupwise Filter":
        group_filter = st.selectbox("Select a Column", temp_data.columns, key="group_col")
        unique_group = temp_data[group_filter].dropna().unique()
        select_a_group = st.selectbox("Select a group", unique_group, key="group_val")
        temp_data = temp_data[temp_data[group_filter] == select_a_group]

    elif feature == "Statistical Summary":
        temp_data = temp_data.describe()

    elif feature == "Rename Column":
        col_to_rename = st.selectbox("Select column to rename", temp_data.columns, key="rename_col")
        new_name = st.text_input("Enter new column name", value=col_to_rename, key="rename_val")
        if new_name and new_name != col_to_rename:
            temp_data.rename(columns={col_to_rename: new_name}, inplace=True)
            st.success(f'Renamed "{col_to_rename}" → "{new_name}"')

    return temp_data


col_left, col_right = st.columns([1, 5])

with col_left:
    features = st.selectbox(
        "Let's do something",
        ["Handling Missing Data", "Groupwise Filter", "Statistical Summary", "Rename Column"],
        key="feature_select",
    )
    new_df = all_features(features, df)

with col_right:
    st.dataframe(new_df, use_container_width=True)


st.markdown("---")
st.subheader("Data Visualisation")

numeric_cols = new_df.select_dtypes(include=np.number).columns.tolist()
categorical_cols = new_df.select_dtypes(exclude=np.number).columns.tolist()
all_cols = new_df.columns.tolist()

if len(all_cols) < 1:
    st.warning("Not enough columns to visualise.")
else:
    chart_type = st.selectbox(
        "Select Chart Type",
        ["Bar Chart", "Line Chart", "Scatter Plot", "Pie Chart"],
        key="chart_type",
    )

    v1, v2 = st.columns(2)

    if chart_type == "Bar Chart":
        with v1:
            x_col = st.selectbox("X-axis (Category)", all_cols, key="bar_x")
        with v2:
            y_col = st.selectbox("Y-axis (Value)", numeric_cols or all_cols, key="bar_y")
        color_col = st.selectbox("Color by (optional)", ["None"] + categorical_cols, key="bar_color")
        fig = px.bar(new_df, x=x_col, y=y_col,
                     color=None if color_col == "None" else color_col,
                     title=f"{y_col} by {x_col}", template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Line Chart":
        with v1:
            x_col = st.selectbox("X-axis", all_cols, key="line_x")
        with v2:
            y_col = st.selectbox("Y-axis (Value)", numeric_cols or all_cols, key="line_y")
        color_col = st.selectbox("Color by (optional)", ["None"] + categorical_cols, key="line_color")
        fig = px.line(new_df, x=x_col, y=y_col,
                      color=None if color_col == "None" else color_col,
                      title=f"{y_col} over {x_col}", template="plotly_white", markers=True)
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Scatter Plot":
        with v1:
            x_col = st.selectbox("X-axis", numeric_cols or all_cols, key="scatter_x")
        with v2:
            y_col = st.selectbox("Y-axis", numeric_cols or all_cols, key="scatter_y")
        color_col = st.selectbox("Color by (optional)", ["None"] + categorical_cols, key="scatter_color")
        
        fig = px.scatter(new_df, x=x_col, y=y_col,
                         color=None if color_col == "None" else color_col,
                         title=f"{y_col} vs {x_col}", template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Pie Chart":
        if not categorical_cols:
            st.warning("Pie chart needs at least one categorical column.")
        else:
            with v1:
                names_col = st.selectbox("Labels (Category)", categorical_cols, key="pie_names")
            with v2:
                values_col = st.selectbox("Values", numeric_cols or all_cols, key="pie_values")
            fig = px.pie(new_df, names=names_col, values=values_col,
                         title=f"{values_col} by {names_col}", template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)