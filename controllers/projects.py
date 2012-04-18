# coding: utf8
# try something like
def index(): 
    rows = db((db.activity.type=='project')&(db.activity.status=='accepted')).select()
    if rows:
        return dict(projects=rows)
    else:
        return plugin_flatpage()
