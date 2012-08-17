# -*- coding: utf-8 -*-
# try something like

@cache(request.env.path_info,time_expire=60,cache_model=cache.ram)
def index():
    def cram(text, maxlen):
        """Omit part of a string if needed to make it fit in a
           maximum length."""
        text = text.decode('utf-8')
        if len(text) > maxlen:
            pre = max(0, (maxlen-3))
            text = text[:pre] + '...' 
        return text.encode('utf8')
        
    q = db.activity.type!='poster'
    q &= db.activity.type!='project'
    q &= db.activity.status=='accepted'
    q &= db.activity.scheduled_datetime!=None
    rows = db(q).select(db.activity.id,
                        db.activity.title,
                        db.activity.track,
                        db.activity.status,
                        db.activity.abstract,
                        db.activity.level,
                        db.activity.type,
                        db.activity.created_by,
                        db.activity.authors,
                        db.activity.categories ,
                        db.activity.scheduled_datetime,
                        db.activity.scheduled_room,
                        )
    levels = {}
    for i, level in enumerate(ACTIVITY_LEVELS):
        levels[level] = XML("&loz;"* (i+1),)
        
    activities_per_date = {}
    for row in rows:
        activities_per_date.setdefault(\
            row.scheduled_datetime.date(), \
            []).append(row)
            
    rooms = ACTIVITY_ROOMS.copy()

    schedule_tables = {}
    activities = {None: ""}
    activities.update(dict([(row.id, row) for row in rows]))
    schedule = dict([((row.scheduled_datetime,
                       row.scheduled_room),
                      row.id) for row in rows])
    
    ##fields.append(BEAUTIFY(schedule))
    hidden = []

    for day in DAYS:
        table = []
        th = [TH("")] + [TH(room) for room in rooms.values()]
        table.append(THEAD(TR(*th)))
        for slot in SLOTS:
            tr = [TD(slot)]
            common = None
            for room in rooms:
                dt = datetime.datetime.strptime("%s %s" % (day,
                                                           slot),
                                                "%Y-%m-%d %H:%M")
                selected = schedule.get((dt, str(room)))
                activity = selected and activities[int(selected)] \
                           or None

                if activity:
                    author = db.auth_user[activity.created_by]
                    if activity.authors and \
                       len(activity.authors.strip()) > 1:
                        u = PluginMModal(title=activity.authors,
                            content=(author.photo and \
                                     IMG(_alt=author.last_name,
                                         _src=URL(r=request,
                                                  c='default',
                                                  f='fast_download',
                                                  args=author.photo),
                                         _width="100px",
                                         _height="100px", \
                                         _style="margin-left: 5px; \
                                         margin-right: 5px; \
                                         margin-top: 3px; \
                                         margin-bottom: 3px; \
                                         float: left;").xml() or \
                                         '') + \
                                     MARKMIN(author.resume or \
                                             '').xml(),
                                     close=T('close'), width=50,
                                     height=50)
                        hidden.append(u)
                        authors = u.link(cram(activity.authors, 25))
                    else:
                        authors = ''
                        
                    a = PluginMModal(title=activity.title, \
                            content=MARKMIN(activity.abstract or \
                                            '').xml(),
                                     close=T('close'),
                                     width=50, height=50)
                    hidden.append(a)
                    
                    td = TD(
                        a.link(B(cram(activity.title, 50))),
                               BR(),
                               authors and \
                               ACTIVITY_LEVEL_HINT[activity.level] \
                               or '',
                               authors and \
                               I(" %s " % \
                               (', '.join(activity.categories or \
                                [])),
                               BR(), "", authors, "") or "",
                               _style="text-align: center;",
                               _class="%s %s" % (activity.track,
                                                 activity.type.replace(" ", "_")))
                    if activity.type in ACTIVITY_COMMON:
                        tr = [tr[0],]
                        td.attributes["_colspan"] = len(rooms)
                        tr.append(td)
                        break
                    else:
                        tr.append(td)
                else:
                    tr.append(TD())                    

            table.append(TR(*tr))
            
        day = datetime.datetime.strptime(day, "%Y-%m-%d")
        schedule_tables[day] = TABLE(*table, _class="schedule")
                
    d = dict(activities_per_date=activities_per_date,
             levels=levels, hidden=hidden,
             schedule_tables=schedule_tables)
    return response.render(d)
    
#@cache(request.env.path_info,time_expire=60,cache_model=cache.ram)
#@auth.requires_membership(role="manager")
def index_alan():
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
        for i, room in enumerate(sorted(ACTIVITY_ROOMS.keys())):
            headers.append(TH("%s" % (ACTIVITY_ROOMS[room],)))
            SCHEDULE_FRAME[day]["rooms"][room] = ro
            position_track[i+1] = SCHEDULE_FRAME[day]["rooms"][room]
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


@auth.requires_membership(role="manager")
def grid():
    response.view = 'generic.html'
    q = db.activity.type!='poster'
    q &= db.activity.type!='project'
    q &= db.activity.status=='accepted'
    rows = db(q).select(db.activity.id,
                        db.activity.title,
                        db.activity.status,
                        db.activity.scheduled_datetime,
                        db.activity.scheduled_room,
                        )

    rooms = ACTIVITY_ROOMS.copy()
    slots = SLOTS
    days = DAYS

    fields = []
    activities = {None: ""}
    activities.update(dict([(row.id, row.title) for row in rows]))
    schedule = dict([((row.scheduled_datetime, row.scheduled_room), row.id) for row in rows])
    
    ##fields.append(BEAUTIFY(schedule))

    table = []
    for day in days:
        th = [TH(day)] + [TH(room) for room in rooms.values()]
        table.append(TR(*th))
        for slot in slots:
            tr = [TH(slot)]
            for room in rooms:
                dt = datetime.datetime.strptime("%s %s" % (day, slot), "%Y-%m-%d %H:%M")
                selected = schedule.get((dt, str(room)))
                selected = selected and int(selected)
                
                tr.append(
                    TD( 
                        SELECT([OPTION(v,
                                   _value=k,
                                   _selected=k and int(k)==selected) for \
                                   (k, v) in sorted(activities.items(), 
                                                    key=lambda x: x[1].lower())],
                                   _name='slot.%s.%s.%s' % (day, slot, room),
                                   _style='width: 100px')
                    ))
            table.append(TR(*tr))
    
    fields.append(TABLE(*table))
    
    fields.append(INPUT(_type="submit"))
    
    form = FORM(*fields)
        
    out = []
    if form.accepts(request.vars, session, keepvalues=True):
        response.flash = 'form accepted'
        for var in form.vars.keys() :
            val = form.vars[var]
            if var.startswith('slot'):
                #slot.%s.%s
                activity_id = val
                slot, slot_day, slot_time, slot_room = var.split(".")
                dt = datetime.datetime.strptime("%s %s" % (slot_day, slot_time), "%Y-%m-%d %H:%M")
                # clean up slot if previously allocated
                q = db.activity.scheduled_datetime == dt
                q &= db.activity.scheduled_room == slot_room
                db(q).update(scheduled_datetime=None, scheduled_room=None)
                # allocate activity (if selected for this slot) 
                if activity_id:
                    q = db.activity.id==activity_id
                    db(q).update(scheduled_datetime=dt, 
                                 scheduled_room=slot_room)
                out.append("setting %s = d%s %s %s" % (activity_id, slot_day, slot_time, slot_room))
            pass

    elif form.errors:
        response.flash = 'form has errors'

    
    return dict(form=form, out=out)
