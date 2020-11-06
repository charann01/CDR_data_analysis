# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 21:50:16 2020

@author: Charann A
"""

#Importing required libraries
import re
import numpy as np
import datetime 
import pandas as pd

#Input format  : ["20190620032717.906", "20200325142652.52",'' ,"20180901002735.207"]
#Output format : [('20190620', '032717'), ('20200325', '142652'), (nan, nan), ('20180901', '002735')]

def datetime_divider(data):
    for index in range(len(data)):
        if(re.match("^\d",str(data[index]))):
            regex = re.compile( "\d{1,8}" )
            a = regex.findall(str(data[index]))
            data[index] = a[0],a[1]
        else:
            data[index] = np.nan,np.nan 
    return data

#Input format  : ['20190620', '20200325', '' , '20180901']
#Output format : ['2019-06-20', '2020-03-25', nan, '2018-09-01']

def date_modifier(data):
    for index in range(len(data)):
        if(re.match("^\d",str(data[index]))):
            year, month, day = str(data[index][:4]),str(data[index][4:6]),str(data[index][6:])
            data[index] = "-".join([year,month,day])
        else:
            data[index] = np.nan
    return data

#Input format  : ['032717', '142652', '' , '002735']
#Output format : ['3:27:17 AM', '2:26:52 PM', nan, '12:27:35 PM']

def time_modifier(data):
    for index in range(len(data)):
        if(re.match("^\d",str(data[index]))):
            hours, minutes, seconds = int(data[index][:2]), data[index][2:4], data[index][4:]
            meridiem = "AM"
            if ( hours < 12 and hours != 0 ):
                hr = str(hours)
            else:
                meridiem = "PM"
                if ( hours == 12 or hours == 0 ):
                    hr = str(12)
                else:
                    hr = str( hours-12 )
            data[index] = ":".join([hr,minutes,seconds]) + " " + meridiem
    return data

#Input format  : ['20190620032717.9', '20190620130614.8', '' , '20190620125700.4']
#Output format : ['2019-06-20 03:27:17', '2019-06-20 13:06:14', nan, '2019-06-20 12:57:00']

def call_time_fetcher(data):
    for index in range(len(data)):
        data[index] = str(data[index])
        if data[index]!="nan" and index != 0:
            year = data[index][:4]
            month = data[index][4:6]
            day = data[index][6:8]
            hours = data[index][8:10]
            minutes = data[index][10:12]
            seconds = str(round(float(data[index][12:])))
            if int(seconds) >= 60:
                seconds = int(seconds) -60
                minutes = int(minutes)+1 
            if int(minutes) >=60:
                hours = int(hours)+1
                minutes  = int(minutes) - 60 
            data[index] = f"{year}-{month}-{day} {hours}:{minutes}:{seconds}"
        else:
            data[index] = np.nan
    return data

#Input format  : ['2019-06-20', '2019-06-21', '' , '2019-06-18']
#Output format : ['Thursday', 'Friday', nan , 'Tuesday']

day_name= ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday','Sunday']
def weekly_range(data):
    for index in range(len(data)):
        if(re.match("^\d",str(data[index]))) and index!= 0:
            year, month, date = (data[index][:4]), (data[index][5:7]), (data[index][8:]) 
            data[index] = " ".join([year,month,date])
            day = datetime.datetime.strptime(data[index], '%Y %m %d').weekday()
            data[index] = day_name[day]
        else:
            data[index] = np.nan
    return data

#Input format  : ['03:27:17 AM', '02:26:52 PM', '' , '12:27:35 PM']
#Output format : ['03:00-03:59', '14:00-14:59', nan , '12:00-12.59']

def hourly_range(data):
    for index in range(len(data)):
        data[index] = str(data[index])
        if data[index]!="nan":
            if re.search("PM", data[index]):
                time_data =  re.findall("\d+", data[index])
                if time_data[0] != "12":
                    time_data = int(time_data[0]) + 12
                else:
                    time_data = time_data[0]
                
            else:
                time_data =  re.findall("\d+", data[index])
                if int(time_data[0]) == 12:
                    time_data = f"0{int(time_data[0]) - 12}"
                else:
                    time_data = time_data[0]
            data[index] = f"{time_data}:00 - {time_data}:59"
        else:
            data[index] = np.nan
    return data


# Replacing Strings in the columns 5,7,12 with standard Terminology

def replace_simple_with_Standard_terminology(dataframe):
    dataframe[5] = dataframe[5].replace('Originating', 'Outgoing')
    dataframe[5] = dataframe[5].replace('Terminating', 'Incoming')
    dataframe[267] = dataframe[267].replace('Success', 'Voice Portal')
    dataframe[312] = dataframe[312].replace('Shared Call Appearance', 'Secondary Device')
    return dataframe

# Removing unwanted data in column 312

def remove_Unwanted_data (datacolumn) :
    for index in range(len(datacolumn)):
        if (datacolumn[index] == 'Primary Device' or datacolumn[index]=='Secondary Device'):
            continue
        else:
            datacolumn[index] = np.nan   
    return datacolumn

# If the data in column 147 is missing, then generate the data from 312 and 267

def combine_All_Services(data1, data2, data3):
    for index in range(len(data1)):
        if (data1[index] is np.nan ):
            if (data2[index] is not np.nan and data3[index] is not np.nan):
                data1[index] = str( data2[index]  ) + "," + str(data3[index])
            elif ( data2[index] is not np.nan ):
                data1[index] = data2[index]
            else:
                data1[index] = data3[index]
        else:
            continue     
    return data1

# Importing the dataset 

dataset_name = "raw_cdr_data.csv"                
raw_cdr_data  = pd.read_csv(dataset_name,header= None, low_memory= False)

# Separating time and date in Column 9 and 13 which contains data and time in reqular pattern
raw_cdr_data["date"], raw_cdr_data["time"] = zip(*datetime_divider(raw_cdr_data[9].tolist()))

# Converting the columns 'date' and 'time' to standard form
raw_cdr_data['date'] = date_modifier(raw_cdr_data["date"].tolist())
raw_cdr_data["time"] = time_modifier(raw_cdr_data["time"].tolist())

# Replacing the technical terms in columns 5,267,312 with standard terms
raw_cdr_data = replace_simple_with_Standard_terminology(raw_cdr_data)

# Removing the unwanted data in column 312 such that it contains only "Primary device" and "Secondary device"
raw_cdr_data[312] = remove_Unwanted_data(raw_cdr_data[312].tolist())

# If the data in column 147 is missing, then generating and replacing the data from 312 and 267
raw_cdr_data[147] = combine_All_Services(raw_cdr_data[147].tolist(), raw_cdr_data[312].tolist(), raw_cdr_data[267].tolist())

# We create two temporary columns to calculate the duration
raw_cdr_data["starttime"] = pd.to_datetime(call_time_fetcher(raw_cdr_data[9].tolist()))
raw_cdr_data["endtime"] = pd.to_datetime(call_time_fetcher(raw_cdr_data[13].tolist()))
raw_cdr_data["duration"] =  (raw_cdr_data["endtime"] - raw_cdr_data["starttime"]).astype("timedelta64[m]")

# Creating 1 hour range for 24 hours
raw_cdr_data["hourly_range"] = hourly_range(raw_cdr_data["time"].tolist())

# Storing the day name in weekly range column
raw_cdr_data["weekly_range"] = weekly_range(raw_cdr_data["date"].tolist())

# Remove columns not required
raw_cdr_data = raw_cdr_data.drop("time", axis=1)
    
# Save the transformed data in CSV format for further use
raw_cdr_data.to_csv("cdr_data.csv", index = None)

