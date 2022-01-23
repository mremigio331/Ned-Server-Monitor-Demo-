import streamlit as st
import os
import glob
import pandas as pd
from time import strptime
from datetime import datetime
from pytz import timezone
from time import strptime
from datetime import datetime
from dateutil import tz
from datetime import datetime
import pytz
import pydeck as pdk
from dateutil.relativedelta import relativedelta
import numpy as np
from datetime import datetime, timedelta


import db_connect as db

def home():
	
	header = st.container()
	dataset= st.container()

	#Side Bar
	result = st.sidebar.button('Load Data')
	if result:
		search()

	auth_logs = db.auth_logs_to_df()
	auth_logs.sort_values(by=['Date_Time'], inplace=True, ascending=False)
	#auth_logs = auth_logs.set_index('Date_Time')

	# Jumpbox Data
	jump_boxes = []
	jump_boxes_options = (auth_logs['Box'].unique().tolist())
	for i in jump_boxes_options:
	    jump_boxes.append(i)
	jump_boxes.sort()
	jump_boxes.insert(0, 'All')

	side_jumpbox = st.sidebar.selectbox('Servers', (jump_boxes))

	if side_jumpbox == 'All':
	    failed_logs = auth_logs.loc[auth_logs['Access'] == 'Failed']
	    pass_logs = auth_logs.loc[auth_logs['Access'] == 'Successful']

	else: 
	    for i in jump_boxes_options:
	        if side_jumpbox == i:
	            failed_logs = auth_logs.loc[auth_logs['Access'] == 'Failed']
	            pass_logs = auth_logs.loc[auth_logs['Access'] == 'Successful']

	            failed_logs = failed_logs.loc[auth_logs['Box'] == i]
	            pass_logs = pass_logs.loc[auth_logs['Box'] == i]
	        else:
	            pass

	# Country
	country_boxes = []
	pass_country_options = (pass_logs['Country'].unique().tolist())
	fail_country_options = (failed_logs['Country'].unique().tolist())


	for i in pass_country_options:
	    if i not in country_boxes:
	        country_boxes.append(i)
	for i in fail_country_options:
	    if i not in country_boxes:
	        country_boxes.append(i)
	    
	country_boxes.sort()
	country_count = len(country_boxes)
	country_boxes.insert(0, 'All')
	country_count = len(country_boxes) - 1
	country_text = 'Which Country ? Total = ' + str(country_count)
	side_country = st.sidebar.selectbox(country_text, (country_boxes))        


	if side_country == 'All':
	    pass

	else: 
	    for i in country_boxes:
	        if side_country == i:
	            failed_logs = failed_logs.loc[auth_logs['Country'] == i]
	            pass_logs = pass_logs.loc[auth_logs['Country'] == i]
	        else:
	            pass


	# city
	city_boxes = []
	pass_city_options = (pass_logs['City'].unique().tolist())
	fail_city_options = (failed_logs['City'].unique().tolist())


	for i in pass_city_options:
	    if i not in city_boxes:
	        city_boxes.append(i)
	for i in fail_city_options:
	    if i not in city_boxes:
	        city_boxes.append(i)
	    
	city_boxes.sort()   
	city_boxes.insert(0, 'All')
	city_count = len(city_boxes) - 1
	city_text = 'Which City ? Total = ' + str(city_count)
	side_city = st.sidebar.selectbox(city_text, (city_boxes))      

	if side_city == 'All':
	    pass

	else: 
	    for i in city_boxes:
	        if side_city == i:
	            failed_logs = failed_logs.loc[auth_logs['City'] == i]
	            pass_logs = pass_logs.loc[auth_logs['City'] == i]
	        else:
	            pass    
	    
	    
	    
	    
	# Dates

	d = datetime.today() - timedelta(days=7)

	dates = []
	pass_date_options = (pass_logs['Date'].unique().tolist())
	fail_date_options = (failed_logs['Date'].unique().tolist())

	for i in pass_date_options:
	    if i not in dates:
	        dates.append(i)
	for i in fail_date_options:
	    if i not in dates:
	        dates.append(i)     

	all_dates_check = st.sidebar.checkbox('All Dates')

	if all_dates_check:
		pass

	else:

		layout = st.sidebar.columns([2, 1])

		min_date = min(dates)
		year = min_date.split('/')[0]
		month = min_date.split('/')[1]
		date = min_date.split('/')[2]

		min_date_time = datetime(int(year), int(month), int(date))

		with layout[0]:
			start_date = st.date_input('Start Date:', value=datetime(2021, 12, 31), max_value=datetime(2021, 12, 31))  # omit "sidebar"

		with layout[0]:
			end_date = st.date_input('End Date:', value=(datetime(2021, 12, 26)), min_value=datetime(2021, 12, 1),
									 max_value=datetime(2021, 12, 31))  # omit "sidebar"

		new_start = str(start_date).replace('-', '/')
		new_end = str(end_date).replace('-', '/')

		pass_logs = pass_logs[(pass_logs['Date'] > new_end) & (pass_logs['Date'] <= new_start)]
		failed_logs = failed_logs[(failed_logs['Date'] > new_end) & (failed_logs['Date'] <= new_start)]

	st.sidebar.image('Images/Ned_Logo_Pictorial_T.png')



	with header: 
	    
	    st.title('Home Page')
	    
	with dataset:    
	    tcol_1, tcol_2 = st.columns(2)
	    bcol_1, bcol_2 = st.columns(2)


	    tcol_1.header('Successful Authorizations')
	    tcol_1.subheader('Successful Data Frame')
	    tcol_1.dataframe(pass_logs[['Date_Time','Source_IP','Box','City','Country','User','By_Way']])
	    
	    

	    tcol_2.header('Failed Authorizations')
	    tcol_2.subheader('Failed Data Frame')
	    tcol_2.dataframe(failed_logs[['Date_Time','Source_IP','Box','City','Country','User']])
	    
	    
	    bcol_1.subheader('Successful Connection IPs Map')

	    bcol_1.pydeck_chart(
	        pdk.Deck(
	            map_style='mapbox://styles/mapbox/dark-v10',
	            layers = [
	            	pdk.Layer(
	                    "HeatmapLayer",
	                    pass_logs,
	                    opacity=0.9,
	                    get_position=['Lon', 'Lat']
	                ),
	                pdk.Layer(
	                    'ScatterplotLayer',
	                    pass_logs.drop_duplicates(),
	                    get_position='[Lon, Lat]',
	                    pickable=True,
	                    opacity=0.8,
	                    stroked=True,
	                    filled=True,
	                    radius_scale=6,
	                    radius_min_pixels=5,
	                    radius_max_pixels=100,
	                    line_width_min_pixels=1,
	                    get_fill_color=[0, 128, 0],
	                    get_line_color=[0, 0, 0]
	                ),
	            ],
	        tooltip={"html": "<b>Box: </b> {Box} <br /> "
	        "<b>Lon: </b> {Lon} <br /> "
            "<b>Lat: </b>{Lat} <br /> "
            "<b> City: </b>{City} <br /> "
            "<b> Country: </b>{Country}"}
	        )
	    )
	    bcol_2.subheader('Failed Connection IPs Map')
	    bcol_2.pydeck_chart(
	        pdk.Deck(
	            map_style='mapbox://styles/mapbox/dark-v10',
	            layers = [
	            	pdk.Layer(
	                    "HeatmapLayer",
	                    failed_logs,
	                    opacity=2,
	                    get_position=['Lon', 'Lat']
	                ),
	                 pdk.Layer(
	                    'ScatterplotLayer',
	                    failed_logs.drop_duplicates(),
	                    get_position='[Lon, Lat]',
	                    pickable=True,
	                    opacity=0.8,
	                    stroked=True,
	                    filled=True,
	                    radius_scale=6,
	                    radius_min_pixels=5,
	                    radius_max_pixels=100,
	                    line_width_min_pixels=1,
	                    get_fill_color=[255,0,0],
	                    get_line_color=[0,0,0]
	                ),
	                 
	            ],
	        tooltip={"html": "<b>Box: </b> {Box} <br /> "
	        "<b>Lon: </b> {Lon} <br /> "
            "<b>Lat: </b>{Lat} <br /> "
            "<b> City: </b>{City}"
            "<b> Country: </b>{Country} <br /> "}
	        )
	 	)

def search():
	st.info('Log pull disabled in demo mode.')
	#db.log_update()
	#auth_logs = db.auth_logs_to_df()
	#auth_logs.sort_values(by=['Date_Time'], inplace=True, ascending=False)