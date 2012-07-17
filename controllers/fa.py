#############################################
# Submit Financial Aid Application
#############################################

def index(): return plugin_flatpage()

@auth.requires_login()
def application():
    if datetime.datetime.today() > FACUTOFF_DATE:
        session.flash=XML(T('<b><font color="red">Applications are no longer being accepted.</b><br>(Financial Aid Application deadline: %s)</font>') % FACUTOFF_DATE)
        redirect(URL(r=request,c='default',f='index'))

    fa=db(db.fa.person==auth.user.id).select().first()
    form=SQLFORM(db.fa, fa,)
    if form.accepts(request.vars, session):
        session.flash = "Thanks! Confirmation email sent!"
        email_fa(fa and 'updated' or 'created')
        redirect(URL("index"))
    elif form.errors:
        response.flash = "The form contains errors!"
    else:
        response.flash = "Please complete the form!"    
    return dict(form=form)

@auth.requires(auth.has_membership(role="colaborator") 
            or auth.has_membership(role="manager"))
def view():
    fa = db(db.fa.id==request.args[0]).select().first()
    manager = auth.has_membership(role="manager")
    form = SQLFORM(db.fa, request.args[0], readonly=not manager, deletable=manager)
    if form.accepts(request.vars, session):
        redirect(URL('edit'))
    response.view = 'generic.html'
    return dict(form=form)

@auth.requires_membership(role="manager")
def edit():
    rows = db(db.fa.person==db.auth_user.id).select(db.fa.id, db.auth_user.last_name, db.auth_user.first_name, db.auth_user.email, db.fa.grant_amount)
    table = SQLTABLE(rows, truncate=None, linkto=lambda fld, typ, ref: URL('view', args=fld))
    response.view = 'generic.html'
    return dict(table=table)

@auth.requires_membership(role="manager")
def grant_all():
    rows = db(db.fa).select()
    for fa in rows:
        db(db.fa.id==fa.id).update(grant_amount=fa.total_amount_requested, status='approved')
    redirect(URL('edit'))
