# -*- coding: utf-8 -*-

import datetime

def index():
    is_manager = False
    events_set = db(db.event.show == True)
    events = events_set.select(orderby=db.event.starts)
    if auth.has_membership("manager"):
        is_manager = True

    # obtain boundaries
    timeline_events = events_set.select()
    # orderby=db.event.starts
    start = timeline_events.first().starts
    end = timeline_events.last().ends
    duration = end - start
    length = duration.days
    trs = list()
    for i, event in enumerate(timeline_events):
        event_duration = event.ends - event.starts
        event_length = event_duration.days
        event_span = 0
        tds = list()
        for x in range(length):
            position_date = start + datetime.timedelta(x)
            position_date_next = position_date + datetime.timedelta(1)
            if (event.starts >= position_date) and (event.starts < position_date_next):
                event_span = event_length
                tds.append(TD(A(event.title, _href="#%s" % event.id), _colspan=event_span, _class="event"))
            else:
                if (event.starts < position_date) and (event.ends > position_date_next):
                    event_span -= 1
                if event_span <= 0:
                    tds.append(TD(_class="empty"))
        if i % 2 == 0:
            tr_class = "even"
        else:
            tr_class = "odd"
        trs.append(TR(*tds, _class=tr_class))
        
    return dict(events=events, is_manager=is_manager, table=TABLE(*trs))
