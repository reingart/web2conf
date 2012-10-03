# -*- coding: utf-8 -*-
# try something like

@caching
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
    #q &= db.activity.type!='project'
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
                        db.activity.categories,
                        db.activity.duration,
                        db.activity.confirmed,
                        db.activity.scheduled_datetime,
                        db.activity.scheduled_room,
                        )
    levels = {}
    for i, level in enumerate(ACTIVITY_LEVELS):
        levels[level] = XML("&loz;"* (i+1),)

    activities_per_date = {}
    slots_per_date = {}
    rooms_per_date = {}

    if auth.user_id:
        myactivities = db(db.partaker.user_id==auth.user_id).select().as_list()
    else:
        myactivities = None

    for activity in rows:
        date = activity.scheduled_datetime.date()
        time = activity.scheduled_datetime.time()
        room = int(activity.scheduled_room)
        activities_per_date.setdefault(date, []).append(activity)
        if not room in rooms_per_date.get(date, []):
            rooms_per_date.setdefault(date, []).append(room)
        if time not in slots_per_date.get(date, []):
            slots_per_date.setdefault(date, {}).setdefault(time, {})
            # find overlapped slots
            if activity.duration and activity.type not in ('open space', 'project', 'sprint', 'social', 'special'):
                for i in range(activity.duration/60):
                    hidden_slot = activity.scheduled_datetime + datetime.timedelta(minutes=60*i)
                    hidden_slot_time = hidden_slot.time()
                    if hidden_slot_time not in slots_per_date.get(date, []):
                        slots_per_date[date].setdefault(hidden_slot_time, {})
            elif activity.duration:
                # record duration for special activities (social, meetings, sprints, etc.)
                slots_per_date[date][time] = activity.duration

    
    rooms = ACTIVITY_ROOMS.copy()

    schedule_tables = {}
    activities = {None: ""}
    activities.update(dict([(row.id, row) for row in rows]))
    schedule = dict([((row.scheduled_datetime,
                       row.scheduled_room),
                      row.id) for row in rows])

    ##fields.append(BEAUTIFY(schedule))
    hidden = []

    myactivities = db(db.partaker.user_id==auth.user_id).select()

    for day in sorted(activities_per_date.keys()):
        table = []
        th = [TH("")] 
        rooms_names = [name for room, name in sorted(rooms.items()) if room in rooms_per_date[day]]
        rooms_ids = dict([(name, room) for room, name in rooms.items()])
        for name in sorted(set(rooms_names), key=lambda x: rooms_ids[x]): 
            th.append(TH(name, _colspan=rooms_names.count(name)))
        table.append(THEAD(TR(*th)))
        slots = sorted(slots_per_date[day])
        for slot in slots:
            if len(slots)==1 and slots_per_date.get(day, {}).get(slot):
                slot_duration = slots_per_date[day][slot]
                slot_end = datetime.datetime.combine(day, slot) + datetime.timedelta(minutes=slot_duration)
                caption = T("%s to %s") % (slot.strftime("%H:%M"), 
                                        slot_end.strftime("%H:%M"))
            else:
                caption = slot.strftime("%H:%M")            
            tr = [TD(caption, _width="5%", _style="text-align: center;", )]
            common = None
            width = "%d%%" % (100/len(rooms_per_date[day])-5)
            for room in rooms:
                if not room in rooms_per_date[day]:
                    continue   # hide unused rooms
                # find an activity for this slot
                slot_dt = datetime.datetime.combine(day, slot)
                selected = schedule.get((slot_dt, str(room)))
                if selected == False:
                    continue   # spanned row!
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
                    activity_selected = False
                    select_activity = ""
                    if auth.user_id and myactivities:
                        response.flash = ""
                        for act in myactivities:
                            if act["activity"] is not None:
                                if (act["activity"].id==activity.id) and (act["add_me"]):
                                    activity_selected = "on"
                        select_activity = INPUT(value=activity_selected,
                                                _type="checkbox",                        
                                                _id="activity_selected_%s" % activity.id,
                                                _class="activity choice",
                                                _onclick="markActivity('activity_selected_%s', '%s');" % (activity.id, activity.id))
                    td = TD(select_activity,
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
                                     _width=width,
                                     _style="text-align: center;",
                                     _id=not activity.confirmed and "unconfirmed" or "confirmed",
                                     _class="%s %s" % (activity.track,
                                                       activity.type.replace(" ", "_")))
                    if activity.type in ACTIVITY_COMMON:
                        tr = [tr[0],]
                        td.attributes["_colspan"] = len(rooms)
                        tr.append(td)
                        break
                    else:
                        if activity.duration:
                            slot_span = 0
                            for next_slot in slots[slots.index(slot)+1:]:
                                next_slot_dt = datetime.datetime.combine(slot_dt.date(), next_slot)
                                if next_slot_dt > (slot_dt  + datetime.timedelta(minutes=activity.duration-1)):
                                    break
                                else:
                                    # mark the slot as spanned
                                    schedule[(next_slot_dt, str(room))] = False
                                    slot_span += 1
                            if slot_span:
                                td.attributes["_rowspan"] = slot_span + 1
                        tr.append(td)
                else:
                    tr.append(TD(_width=width))

            table.append(TR(*tr))

        schedule_tables[day] = TABLE(*table, _class="schedule")

    d = dict(activities_per_date=activities_per_date,
             levels=levels, hidden=hidden,
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

@auth.requires_login()
def markactivity():
    if request.args[3] == "checked":
        add_me = True
    else:
        add_me = False
    activity = int(request.args[1])
    comment = T("Marked in schedule on %s") % request.now
    participation = db((db.partaker.user_id==auth.user_id)&(db.partaker.activity==activity)).select().first()
    if participation is None:
        db.partaker.insert(user_id=auth.user_id, activity=activity, add_me=add_me, comment=comment)
    else:
        participation.update_record(add_me=add_me, comment=comment)
    raise HTTP(200, T("Done!"))
