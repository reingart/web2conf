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
    form = SQLFORM(db.fa, request.args[0], readonly=True)
    response.view = 'generic.html'
    return dict(form=form)
