# coding: utf8
# intente algo como
import datetime

def index():
    is_manager = False
    events = db(db.event.show == True).select(orderby=db.event.starts)
    if auth.has_membership("manager"):
        is_manager = True
    return dict(events=events, is_manager=is_manager)
