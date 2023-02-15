import streamlit as st 
import pandas as pd
import numpy as np
from datetime import date
import datetime
import plotly.graph_objs as go
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster


st.set_page_config(layout="wide",)

df = pd.read_csv("crimes.csv", parse_dates = ["Date"])


df["hour"] = df["Time"].str[0:2].astype("int")
df["Date"] = pd.to_datetime(df["Date"].dt.date)

df_temp = df.copy()

DayOfWeek = df["DayOfWeek"].unique()
crime_category = df["Category"].unique()
PdDistrict = df.loc[~df["PdDistrict"].isna()]["PdDistrict"].unique()


side_bar = st.sidebar

with side_bar.form("MyForm"):

    c1,c2,c3  = st.columns(3)

    with c2:

        submitted = st.form_submit_button('Submit')

    st.header("San Francisco Crimes - Streamlit App")


    start_date = st.date_input("Start Date",value = datetime.date(2016,1,1),
                                            min_value = datetime.date(2016,1,1),
                                            max_value = datetime.date(2016,12,31))
    
    end_date = st.date_input("End Date",value = datetime.date(2016,12,31),
                                        min_value = datetime.date(2016,1,1),
                                        max_value = datetime.date(2016,12,31))
    
    time = st.slider(label = "Select time range", min_value = 0, max_value = 23, value = (0,23), step = 1)
    Days = st.multiselect(label = "Select days", options = ["Monday","Tuesday","Wednesday",
                                                            "Thursday","Friday","Saturday","Sunday"], default = ["Sunday","Wednesday"])
    
    crimes = st.multiselect(label = "Select crime category", options = crime_category, default = "WEAPON LAWS")
    districts = st.multiselect(label = "Select district", options = PdDistrict, default = PdDistrict)


# Additional table

add_table = df.copy()

add_table["Date"] = add_table["Date"].dt.date
add_table = add_table.loc[(add_table["Date"] >= start_date) & (add_table["Date"] <= end_date)]
add_table = add_table.loc[(add_table["hour"] >= time[0]) & (add_table["hour"] <= time[1])]
add_table = add_table.loc[add_table["DayOfWeek"].isin(Days)]
add_table = add_table.loc[add_table["Category"].isin(crimes)]
add_table = add_table.loc[add_table["PdDistrict"].isin(districts)]

tab1,tab2 = st.tabs(["Dashboard","Additional table"])

with tab2:
    st.dataframe(data = add_table,height = 600)


# Zapis do .csv/.xlsx


@st.cache
def convert_df_csv(add_table):
    return add_table.to_csv(index = False).encode('utf-8')
csv = convert_df_csv(add_table)


with side_bar:
        
    st.download_button(label = "Download CSV",
                data = csv,
                file_name = "DATA_" + date.today().strftime("%Y-%m-%d") + ".csv")
    

# BarChart

with tab1: 

    a = len(add_table)
    b = len(add_table.drop_duplicates(subset = ["IncidntNum"]))
    N = len(add_table)
    result = a/b
    result = np.round(result,3)

    x1,x2,x3,x4= st.columns(4)

    with x1:

        st.metric(label="Total number of crimes", value= N)

    with x2:

        st.metric(label="Number of violations per each crime", value= result)



    y1,y2 = st.columns(2)

    with y1:

        df_barplot = add_table.groupby("hour").agg({"Time":"count"}).reset_index()

        data = [go.Bar(x = df_barplot["hour"], y = df_barplot["Time"],
                    text = df_barplot["Time"], marker_color='rgb(26, 118, 255)', marker_line_color='rgb(8,48,107)',opacity=0.6)]
        layout = go.Layout(title = "Crimes divided into hours",
                        xaxis_title = "Hours",
                        yaxis_title = "Number of cases",
                        hovermode = False,
                        # hoverlabel=dict(
                        #                    bgcolor="white",
                        #                    font_size=16,
                        #                      font_family="Rockwell"),
                        xaxis = dict(dtick = 1))


        fig = {"data" : data, "layout" : layout}

        st.plotly_chart(fig,use_container_width=True)


    with y2:

        # The most popular crimes

        df_short = add_table.groupby("Descript").agg({"IncidntNum":"count"}, as_index = False)\
                                            .sort_values(by = "IncidntNum", ascending = False)\
                                            .head(10)
        df_short.columns = ["N"]
        df_short.reset_index(inplace = True)

        st.dataframe(df_short,use_container_width = True)

# Map



    df_map = add_table.copy()


    mean_x = np.mean(df_map["X"])
    mean_y = np.mean(df_map["Y"])

    m = folium.Map(location = [mean_y, mean_x])
    marker_cluster = MarkerCluster().add_to(m)

    for index, row in df_map.iterrows():

        folium.CircleMarker([row["Y"], row["X"]], popup = row["Descript"], fill = True).add_to(marker_cluster)

    folium_static(m,width = 1000)








    














