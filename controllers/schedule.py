# coding: utf8
# try something like

@cache(request.env.path_info,time_expire=60,cache_model=cache.ram)
#@auth.requires_membership(role="manager")
def index():
    db.activity['represent']=lambda activity: A('%s by %s' % (activity.title,activity.authors),
       _href=URL(r=request,f='activity_info',args=[activity.id]))
    query=(db.activity.status=='accepted') &(db.auth_user.id==db.activity.created_by)
    query &= db.activity.scheduled_datetime!=None
    query &= db.activity.scheduled_room!=None
    rows=db(query).select(orderby=(db.activity.scheduled_datetime, db.activity.scheduled_room))
    
    activities_per_date = {}
    for row in rows:
        activities_per_date.setdefault(row.activity.scheduled_datetime.date(),[]).append(row)

    levels = {}
    for i, level in enumerate(ACTIVITY_LEVELS):
        levels[level] = XML("&loz;"* (i+1),)
 
    d = dict(activities_per_date =activities_per_date, levels=levels )
    return response.render(d)

@auth.requires_membership(role="manager")
def agenda():
    rows = db(db.activity.id>=1).select(db.activity.id, db.activity.title, db.activity.scheduled_datetime, db.activity.scheduled_room, orderby=db.activity.title)
    
    rooms = ACTIVITY_ROOMS.copy()
    rooms[None] = ""
    fields = []
    for row in rows:
        fields.extend([
            INPUT(_name='activity.%s' % row.id, _value=row.title, _readonly=True),
            INPUT(_name='date.%s' % row.id, requires=IS_EMPTY_OR(IS_DATETIME()), _value=row.scheduled_datetime),
            SELECT([OPTION(rooms[opt],_value=opt, _selected=row.scheduled_room==opt) for opt in sorted(rooms.keys())], _name='room.%s' % row.id),
            BR()])
    fields.append(INPUT(_type="submit"))
    
    form = FORM(*fields)
        
    out = []
    if form.accepts(request.vars, session):
        response.flash = 'form accepted'
        for var in form.vars.keys() :
            activity_id = "." in var and int(var.split(".")[1]) or None
            val = form.vars[var]
            if var.startswith("date") and val and activity_id :
                db(db.activity.id==activity_id).update(scheduled_datetime=val)
                out.append("setting %s=%s" % (var, val))
            if var.startswith("room") and val and activity_id :
                db(db.activity.id==activity_id).update(scheduled_room=val)
                out.append("setting %s=%s" % (var, val))

    elif form.errors:
        response.flash = 'form has errors'

    
    return dict(form=form, out=out)


@auth.requires_membership(role="manager")
def agenda2():
    rows = db(db.activity.id>=1).select(db.activity.id, db.activity.title, db.activity.scheduled_datetime, db.activity.scheduled_room, orderby=db.activity.title)
    
    activities = sorted([(row.id, row.title) for row in rows], key=lambda x: x[1])
    rooms = sorted([(0, "")] + list(ACTIVITY_ROOMS.items()), key=lambda x: x[1])
    

    form = SQLFORM.factory(
        Field("activity_id", 'integer', requires=IS_IN_SET(activities)),
        Field("room", 'integer', requires=IS_IN_SET(rooms)),
        Field("datetime", 'datetime'),
        )
        
    if form.accepts(request.vars, session, keepvalues=True):
        response.flash = 'form accepted'
        db(db.activity.id==form.vars.activity_id).update(scheduled_datetime=form.vars.datetime, scheduled_room=form.vars.room)
    elif form.errors:
        response.flash = 'form has errors'

    
    return dict(form=form)
