import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import os
import re
import statsmodels
from wordcloud import WordCloud
import warnings
import string

warnings.filterwarnings('ignore')

config = {
    'directory_data': 'src/tasks/task-3-EDA/Dashboards/Final Dashboards/Mirambika-hazardous_waste_dashboard/',
    'directory_df1': 'src/tasks/task-3-EDA/Dashboards/Final Dashboards/Mirambika-hazardous_waste_dashboard/hazardous_EAV2-6_32151-0002.csv',
    'directory_df2': 'src/tasks/task-3-EDA/Dashboards/Final Dashboards/Mirambika-hazardous_waste_dashboard/hazardous_EAV2-6_32151-0003.csv'
}
stopwords = ["waste", "and", "from", "other", "etc", "still", "it", "it's", "its", "they", "this", "that", "that'll",
            "these""those", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do",
            "does", "a", "an", "the", "and", "as", "while", "of", "at", "by", "for", "with", "into", "to", "from",
            "in", "out", "on"]
Most_Important_labels = 10


def clean_text(text):
    text = text.lower().strip()
    text = ''.join([char for char in text if char not in string.punctuation])
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    tokens = text.split()
    tokens = [word for word in tokens if word not in stopwords]
    cleaned_text = ' '.join(tokens)
    return cleaned_text

def main():
    st.markdown('<style>div.block-container{text-align: center}{border:1px solid red}{padding-top:0.5rem;}</style>',
                unsafe_allow_html=True)

    file_1 = st.file_uploader(":file_folder: Upload the CSV file for overall waste quantity data", type=['.csv'])
    file_2 = st.file_uploader(":file_folder: Upload the CSV file for state-wise waste quantity data", type=['.csv'])

    if file_1 is not None:
        filename = file_1.name
        st.write(f"{filename} uploaded successfully")
        overall_waste_qty = pd.read_csv(config['directory_data'] + filename)
    else:
        overall_waste_qty = pd.read_csv(config['directory_df1'])

    if file_2 is not None:
        filename = file_2.name
        st.write(f"{filename} uploaded successfully")
        statewise_waste_qty = pd.read_csv(config['directory_data'] + filename)
    else:
        statewise_waste_qty = pd.read_csv(config['directory_df2'])

    column1, column2 = st.columns((2))

    # Preprocessing on overall_waste_qty dataframe
    overall_waste_qty = overall_waste_qty.rename(
        columns={'year': 'year', 'type of waste': 'type_of_waste', 'waste producers': 'waste_producers',
                'waste quantities': 'waste_quantities',
                'waste quantities generated by primary producers': 'waste_quantities_generated_by_primary_producers'})
    overall_waste_qty['type_of_waste'] = overall_waste_qty['type_of_waste'].apply(clean_text)

    if 'Unnamed: 0' in overall_waste_qty.columns.tolist():
        overall_waste_qty.drop(['Unnamed: 0'], axis=1, inplace=True)

    overall_waste_qty = overall_waste_qty.astype(
        {'waste_producers': int, 'waste_quantities': float, 'waste_quantities_generated_by_primary_producers': float,
        'year': str, 'type_of_waste': str})

    statewise_waste_qty = statewise_waste_qty.rename(
        columns={'Year ': 'year', 'Federal State ': 'federal_state', 'Number of Waste Producers': 'waste_producers',
                'Waste Quantity (1000 t)': 'waste_quantities',
                'Waste Quantity Handed Over to Primary Producers (1000 t)': 'waste_quantities_returned_to_primary_producers'})

    statewise_waste_qty = statewise_waste_qty.astype({'year': str})
    statewise_waste_qty['waste_producers'] = pd.to_numeric(statewise_waste_qty['waste_producers'], errors='coerce')
    statewise_waste_qty['waste_quantities'] = pd.to_numeric(statewise_waste_qty['waste_quantities'], errors='coerce')
    statewise_waste_qty['waste_quantities_returned_to_primary_producers'] = pd.to_numeric(
        statewise_waste_qty['waste_quantities_returned_to_primary_producers'], errors='coerce')
    statewise_waste_qty['waste_qty_per_producer'] = statewise_waste_qty['waste_quantities'] / statewise_waste_qty[
        'waste_producers']
    statewise_waste_qty.loc[statewise_waste_qty['waste_qty_per_producer'] == np.nan, 'waste_qty_per_producer'] = -1

    startYear = overall_waste_qty['year'].min()
    endYear = overall_waste_qty['year'].max()

    with column1:
        start_year_input = st.text_input("Start Year", startYear)
        end_year_input = st.text_input("End Year", endYear)
        overall_waste_qty1 = overall_waste_qty.loc[
            (overall_waste_qty['year'] >= start_year_input) & (overall_waste_qty['year'] <= end_year_input)].copy(deep=True)
        statewise_waste_qty1 = statewise_waste_qty.loc[
            (statewise_waste_qty['year'] >= start_year_input) & (statewise_waste_qty['year'] <= end_year_input)].copy(
            deep=True)

        st.subheader(f"Distribution of yearly waste quantity produced (1000 tons) | {start_year_input} - {end_year_input}")
        fig = px.histogram(overall_waste_qty1, x='waste_quantities', template='seaborn', histnorm='probability')
        st.plotly_chart(fig, use_container_width=True, height=200)
        st.text('This is some interpretation of Figure 1.')

        st.subheader(f"Trend of Total Waste Quantity produced | {start_year_input} - {end_year_input}")
        overall_waste_qty1_grouped = overall_waste_qty1.groupby(by=["year"]).sum()[
            ["waste_quantities", "waste_quantities_generated_by_primary_producers"]].reset_index()
        fig = px.line(overall_waste_qty1_grouped, x="year",
                    y=["waste_quantities", "waste_quantities_generated_by_primary_producers"], template='seaborn')
        st.plotly_chart(fig, use_container_width=True, height=200)
        st.text("This is some interpretation of Figure 3")

        st.subheader(f"Waste Quantity produced v/s Number of Producers | {start_year_input} - {end_year_input}")
        fig = px.scatter(overall_waste_qty1, x="waste_producers",
                        y=["waste_quantities", "waste_quantities_generated_by_primary_producers"], template='seaborn',
                        trendline='ols')
        st.plotly_chart(fig, use_container_width=True, height=200)
        st.text("This is some interpretation of Figure 5")

        text = ' '.join(overall_waste_qty1['type_of_waste'])
        wordcloud = WordCloud(width=1000, height=400, background_color='white').generate(text)
        st.image(wordcloud.to_array(), use_column_width=True)
        st.text("These are the most common words in the description")

    with column2:
        states = st.multiselect("Select the states for analysis", statewise_waste_qty1['federal_state'].unique())
        if not states:
            statewise_waste_qty2 = statewise_waste_qty1.copy(deep=True)
        else:
            statewise_waste_qty2 = statewise_waste_qty1.loc[statewise_waste_qty1['federal_state'].isin(states)]

        st.subheader(f"Distribution of yearly waste quantity produced (1000 tons) | Statewise | {start_year_input} - {end_year_input}")
        fig = px.histogram(statewise_waste_qty2, y='waste_quantities', x='federal_state', template='seaborn')
        st.plotly_chart(fig, use_container_width=True, height=200)
        st.text('This is some interpretation of Figure 2.')

        st.subheader(f"Trend of Waste Quantity produced | Statewise | {start_year_input} - {end_year_input}")
        all_selected_states = statewise_waste_qty2['federal_state'].unique().tolist()
        statewise_waste_qty2_grouped = pd.DataFrame()
        statewise_waste_qty2_grouped['year'] = sorted(statewise_waste_qty2['year'].unique().tolist())
        columns_to_plot = []
        for each_state in all_selected_states:
            each_state_waste_qty = \
                statewise_waste_qty2.loc[statewise_waste_qty2['federal_state'] == each_state].groupby(by=["year"]).sum()[
                    ["waste_quantities"]].reset_index().sort_values(by=['year'])
            statewise_waste_qty2_grouped[each_state] = each_state_waste_qty['waste_quantities']
            columns_to_plot.append(each_state)

        fig = px.line(statewise_waste_qty2_grouped, x="year", y=columns_to_plot, template='seaborn')
        st.plotly_chart(fig, use_container_width=True, height=200)
        st.text("This is some interpretation of Figure 4")

        statewise_waste_qty2_grouped = pd.DataFrame()
        statewise_waste_qty2_grouped['year'] = sorted(statewise_waste_qty2['year'].unique().tolist())
        columns_to_plot = []
        for each_state in all_selected_states:
            each_state_waste_qty = \
                statewise_waste_qty2.loc[statewise_waste_qty2['federal_state'] == each_state].groupby(by=["year"]).sum()[
                    ["waste_qty_per_producer"]].reset_index().sort_values(by=['year'])
            statewise_waste_qty2_grouped[each_state] = each_state_waste_qty['waste_qty_per_producer']
            columns_to_plot.append(each_state)
        st.subheader(f"Trend of Waste Quantity produced per producer | {start_year_input} - {end_year_input}")
        fig = px.line(statewise_waste_qty2_grouped, x="year", y=columns_to_plot, template='seaborn')
        st.plotly_chart(fig, use_container_width=True, height=200)
        st.text("This is some interpretation of Figure 6")

if __name__ == '__main__':
    main()
