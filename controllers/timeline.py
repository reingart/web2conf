# -*- coding: utf-8 -*-

import datetime

def time_distance(a, b):
    td = a - b
    difference = td.days*24*60*60 + td.seconds
    return abs(difference)

def event_spans(event):
    event_duration = event.ends - event.starts
    spans = event_duration.days
    if spans < 1:
        spans = 1
    return spans

def fill_free_slots(event, fields, start, end):
    fs = list()
    spans = event_spans(event)
    for x, value in enumerate(fields):
        position_date = start + datetime.timedelta(x)
        position_date_next = position_date + datetime.timedelta(1)
        if (event.starts >= position_date) and (event.starts < position_date_next):
            if value is None:
                # free space
                fs.append(event.id)
                spans -= 1
            else:
                fs.append(value)
        elif (event.starts < position_date) and (event.ends > position_date_next):
            if value is None:
                # free non-starting event cell
                fs.append(0)
                spans -= 1
            else:
                fs.append(value)
        else:
            fs.append(value)
            
    if spans == 0:
        return fs
    else:
        return None


def index():

    is_manager = False
    events_set = db(db.event.show == True)
    events = events_set.select(orderby=db.event.starts)
    if auth.has_membership("manager"):
        is_manager = True

    # obtain boundaries
    start = events.first().starts
    end = events.last().ends
    duration = end - start
    length = duration.days

    # a map of filled/empty row cells
    filled = list()

    # event time distances from today
    deltas = dict()

    # loop trough each event in db
    for i, event in enumerate(events):
        # loop trough each created table line
        free = None
        
        deltas[time_distance(request.now, event.starts)] = event.id
        deltas[time_distance(request.now, event.ends)] = event.id
        
        for j, fields in enumerate(filled):
            # search a free space
            free = fill_free_slots(event, fields, start, end)
            if free is not None:
                filled[j] = free
                break

        if free is None:
            # no space, create a new row
            free = fill_free_slots(event,
                                   [None for x in range(length)],
                                   start, end)
            filled.append(free)

    try:
        next_event = deltas[sorted(deltas)[0]]
    except (IndexError, KeyError):
        next_event = None

    return dict(events=events, is_manager=is_manager, event_spans=event_spans,
                cells=filled, next_event=next_event)
