# coding: utf8
# try something like
def index(): 
    rows = db(db.sponsor.text!="").select()
    if rows:
        return dict(sponsors_detail=rows)
    else:
        return plugin_flatpage()

def prospectus(): return plugin_flatpage()
