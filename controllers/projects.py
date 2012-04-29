# coding: utf8
# try something like
def index(): 
    rows = db((db.activity.type=='project')&(db.activity.status=='accepted')).select()
    if rows:
        return dict(projects=rows)
    else:
        return plugin_flatpage()

@auth.requires_login()
def apply():
    project = db.activity[request.args(1)]
    partaker = db((db.partaker.activity == request.args(1)) & (db.partaker.user == auth.user_id)).select().first()
    
    db.partaker.user.default = auth.user_id
    db.partaker.user.writable = False
    db.partaker.user.readable = False    
    db.partaker.activity.default = request.args(1)
    db.partaker.activity.writable = False
    db.partaker.activity.readable = False    
    
    if partaker is None:
        form = SQLFORM(db.partaker)
        if form.accepts(request.vars, session, formname="new"):
            if not form.vars.activity in (None, ""):
                db.partaker.insert(user=auth.user_id, activity=form.vars.activity)
            session.flash = T("Thanks for joining the partakers list")
            redirect(URL(c="projects", f="index"))
    else:
        db.partaker.id.readable = False
        form = SQLFORM(db.partaker, partaker.id)
        if form.accepts(request.vars, session, formname="update"):
            session.flash = T("Your project's info was updated")
            redirect(URL(c="projects", f="index"))

    return dict(form=form, partaker=partaker, project=project)

@auth.requires_login()
def dismiss():
    partaker = db.partaker[request.args(1)]
    project = partaker.activity
    
    partaker.delete_record()
    session.flash = T("You dismissed the project" + " " + str(project.title))
    redirect(URL(c="projects", f="index"))

@auth.requires(user_is_author_or_manager(activity_id=request.args(1)))
def partakers():
    project = db.activity[request.args(1)]
    partakers = db(db.partaker.activity == project.id).select()
    return dict(partakers=partakers, project=project)
