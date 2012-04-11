# coding: utf8
# try something like
def index(): 
    rows = db((db.sponsor.text!="")&(db.sponsor.active==True)).select()
    if rows:
        return dict(sponsors_detail=rows)
    else:
        return plugin_flatpage()

def prospectus(): return plugin_flatpage()

@auth.requires_login()
def sign_up():
    if request.args:
        q = db.sponsor.id == request.args[0]
        if not auth.has_membership(role="manager"):
            q &= db.sponsor.created_by == auth.user.id
        sponsor = db(q).select().first()
    else:
        sponsor = None
    db.sponsor.number.default = db(db.sponsor.id>0).count() + 1
    form = SQLFORM(db.sponsor, sponsor)
    if form.accepts(request.vars, session):
        session.flash = T("Sponsor sign-up form successfully processed")
        redirect(URL(f="edit"))
    elif form.errors:
        response.flash = T("Sponsor form has errors!")
    else:
        response.flash = T("Complete the Sponsor form")
    return dict(form=form)
        
def edit():
    if auth.has_membership(role="manager"):
        q = db.sponsor.id>0
    else:
        q = db.sponsor.created_by == auth.user.id
    rows = db(q).select(db.sponsor.id, db.sponsor.name)
    return dict(rows=rows)

def expo(): return plugin_flatpage()
