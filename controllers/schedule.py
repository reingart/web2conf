# -*- coding: utf-8 -*-
# try something like

@cache(request.env.path_info,time_expire=60,cache_model=cache.ram)
#@auth.requires_membership(role="manager")
def index():
    query = (db.activity.status=='accepted') & \
            (db.auth_user.id==db.activity.created_by)
    query &= db.activity.scheduled_datetime != None
    query &= db.activity.scheduled_room != None
    
    rows = db(query).select(orderby=(db.activity.scheduled_datetime,
                          db.activity.scheduled_room))

    activities_per_date = {}
    for row in rows:
        activities_per_date.setdefault(\
            row.activity.scheduled_datetime.date(), \
            []).append(row)

    db.activity['represent']=lambda activity: \
        A('%s by %s' % (activity.title,activity.authors),
          _href=URL(r=request,f='activity_info',args=[activity.id]))

    levels = {}
    for i, level in enumerate(ACTIVITY_LEVELS):
        levels[level] = XML("&loz;"* (i+1),)

    # TODO move this code to the view
    schedule_tables = {}
    for day in SCHEDULE_FRAME.keys():
        day_as_date = datetime.date(*[int(s) for s in day.split("-")])
        slots = schedule_slots(day)
        headers = [TH(),]
        position_track = {0: None}
        position_spans = {0: None}
        for i, track in enumerate(sorted(SCHEDULE_FRAME[day]["tracks"].keys())):
            headers.append(TH("%s (%s) %s" % (SCHEDULE_FRAME[day]["tracks"][track],
                                              track, int_to_roman(i+1))))
            position_track[i+1] = SCHEDULE_FRAME[day]["tracks"][track]
            position_spans[i+1] = 0
            
        table_width = len(headers)
        thead = THEAD(TR(*headers))
        trs = []

        if day_as_date in activities_per_date.keys():
            for i_dt, dt in enumerate(slots):
                tds = []
                activity_start = False
                start_of_activity = False
                common = False
                # Which activities start here?
                for i, track in position_track.iteritems():
                    if common:
                        cell = True
                    else:
                        cell = False
                    if (i != 0)  and (common == False):
                        for row in activities_per_date[day_as_date]:
                            if cell == False:
                                this_track = row.activity.track == track
                                is_next = row.activity.scheduled_datetime >= dt
                                is_common = row.activity.type in ACTIVITY_COMMON
                                if (this_track or is_common) and is_next:
                                    try:
                                        next_slot = slots[i_dt + 1]
                                        activity_start = row.activity.scheduled_datetime < next_slot
                                    except IndexError, e:
                                        # end of time slots!
                                        activity_start = True
                                    if activity_start:
                                        if is_common:
                                            common = is_common
                                            colspan = table_width -1
                                        else:
                                            colspan = None
                                        rowspan = schedule_activity_spans(row.activity.duration)
                                        if rowspan > 0:
                                            position_spans[i] = rowspan
                                        tds.append(TD(row.activity.title,
                                                        _rowspan=rowspan,
                                                        _colspan=colspan,
                                                        _class=row.activity.type.replace(" ", "-")))
                                        cell = True
                                        start_of_activity = True

                        if not cell:
                            if not position_spans[i] > 0:
                                tds.append(TD(_class="empty"))
                            else:
                                position_spans[i] -= 1

                if start_of_activity:
                    tr_class = "odd"
                    # mark the time at the first cell
                    tds.insert(0, TD(dt, _class="time"))
                else:
                    tr_class = None
                    tds.insert(0, TD(_class="empty"))

                # *list function argument is not working
                # trs.append(TR(*tds, _class=tr_class))
                a_tr = TR(_class=tr_class)
                [a_tr.append(td) for td in tds]
                trs.append(a_tr)

        tbody = TBODY(*trs)
        schedule_tables[day] = TABLE(thead, tbody, _class="schedule")

    d = dict(activities_per_date=activities_per_date,
             levels=levels,
             schedule_tables=schedule_tables)
             
    return response.render(d)

@auth.requires_membership(role="manager")
def agenda():
    if 'order' in request.vars:
        order = {'title': db.activity.title,
                 'track': db.activity.title,
                 'status': db.activity.status,
                 'scheduled_datetime': db.activity.scheduled_datetime,
                 'scheduled_room': db.activity.scheduled_room,
                }[request.vars['order']]
    else:
        order = (db.activity.type, db.activity.track, db.activity.title)
    response.view = 'generic.html'
    q = db.activity.type!='poster'
    q &= db.activity.type!='project'
    rows = db(q).select(db.activity.id,
                                        db.activity.title,
                                        db.activity.status,
                                        db.activity.scheduled_datetime,
                                        db.activity.scheduled_room,
                                        orderby=order)
    
    rooms = ACTIVITY_ROOMS.copy()
    statuses = ['pending','accepted','rejected', 'declined']
    rooms[None] = ""
    fields = []
    for row in rows:
        fields.extend([
            INPUT(_name='activity.%s' % row.id, _value=row.title,
                  _readonly=True),
            INPUT(_name='date.%s' % row.id,
                   requires=IS_EMPTY_OR(IS_DATETIME()),
                  _value=row.scheduled_datetime),
            SELECT([OPTION(opt,
                           _value=opt,
                           _selected=row.status==opt) for \
                           opt in statuses],
                           _name='status.%s' % row.id),
            SELECT([OPTION(rooms[opt],
                           _value=opt,
                           _selected=row.scheduled_room==opt) for \
                           opt in sorted(rooms.keys())],
                           _name='room.%s' % row.id), BR()])
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
            if var.startswith("status") and val and activity_id :
                db(db.activity.id==activity_id).update(status=val)
                out.append("setting %s=%s" % (var, val))
            if var.startswith("room") and val and activity_id :
                db(db.activity.id==activity_id).update(scheduled_room=val)
                out.append("setting %s=%s" % (var, val))

    elif form.errors:
        response.flash = 'form has errors'

    
    return dict(form=form, out=out)


@auth.requires_membership(role="manager")
def agenda2():
    response.view = 'generic.html'
    rows = db(db.activity.id>=1).select(db.activity.id,
                                        db.activity.title,
                                        db.activity.scheduled_datetime,
                                        db.activity.scheduled_room,
                                        orderby=db.activity.title)
    
    activities = sorted([(row.id, row.title) for row in rows], key=lambda x: x[1])
    rooms = sorted([(0, "")] + list(ACTIVITY_ROOMS.items()), key=lambda x: x[1])
    

    form = SQLFORM.factory(
        Field("activity_id", 'integer', requires=IS_IN_SET(activities)),
        Field("room", 'integer', requires=IS_IN_SET(rooms)),
        Field("datetime", 'datetime'),
        )
        
    if form.accepts(request.vars, session, keepvalues=True):
        response.flash = 'form accepted'
        db(db.activity.id==form.vars.activity_id).update(
            scheduled_datetime=form.vars.datetime,
            scheduled_room=form.vars.room)
    elif form.errors:
        response.flash = 'form has errors'

    return dict(form=form)
