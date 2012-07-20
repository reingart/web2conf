# -*- coding: utf-8 -*-
import datetime

def schedule_activity_spans(duration, window=5):
    quantity = duration/window -1
    return quantity

def schedule_datetime(day, timestr):
    """ Returns a datetime object
    for the time string."""
    d = [int(s) for s in day.split("-")]
    t = [int(s) for s in timestr.split(":")]
    l = d+t
    return datetime.datetime(*l)

def schedule_date(data):
    """ Returns a date object for
    the date string."""
    return datetime.date(*[int(s) for s in data.split("-")])

def schedule_slots(day, window=5):
    slots = []
    begins = schedule_datetime(day, SCHEDULE_FRAME[day]["begins"])
    ends = schedule_datetime(day, SCHEDULE_FRAME[day]["ends"])
    difference = ends - begins
    quantity = (difference.seconds/60)/window
    newtime = begins
    slots.append(newtime)
    for i in range(quantity):
        newtime += datetime.timedelta(minutes=window)
        slots.append(newtime)
    return slots

def day_begins(day):
    return datetime.datetime()

# This code was extracted from the following site:
# http://codereview.stackexchange.com/questions/5091/
# python-function-to-convert-roman-numerals-to-integers
# -and-vice-versa
# Author: Anthony Curtis Adler

def int_to_roman(integer):
    returnstring=''
    table=[['M',1000],['CM',900],['D',500],['CD',400],['C',100],
           ['XC',90],['L',50],['XL',40],['X',10],['IX',9],
           ['V',5],['IV',4],['I',1]]

    for pair in table:
        while integer-pair[1]>=0:
            integer-=pair[1]
            returnstring+=pair[0]
    return returnstring

def rom_to_int(string):
    table=[['M',1000],['CM',900],['D',500],['CD',400],['C',100],
           ['XC',90],['L',50],['XL',40],['X',10],['IX',9],
           ['V',5],['IV',4],['I',1]]
    returnint=0
    for pair in table:
        continueyes=True
        while continueyes:
            if len(string)>=len(pair[0]):
                if string[0:len(pair[0])]==pair[0]:
                    returnint+=pair[1]
                    string=string[len(pair[0]):]
                else: continueyes=False
            else: continueyes=False
    return returnint


# Schedule structure that specifies
# for each date: when does it starts,
# when does it finishes, and a list of
# day-tracks classified by track code
# and track type.

SCHEDULE_FRAME = {"2012-07-01": {
    "begins": "09:00:00", "ends": "21:00:00", "tracks":{
        "D1":"Science", "D2": "Student Works", "D3": "General", "D4": "Extreme"}},
                  "2012-07-02": {
    "begins": "09:00:00", "ends": "21:00:00", "tracks":{
        "D1":"Science", "D2": "Student Works", "D3": "General", "D4": "Extreme"}},
                  "2012-07-03": {
    "begins": "09:00:00", "ends": "21:00:00", "tracks":{
        "D1":"Science", "D2": "Student Works", "D3": "General", "D4": "Extreme"}        
                  }}

# ("General", "Science", "Student Works", "Extreme")
