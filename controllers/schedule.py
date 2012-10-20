# -*- coding: utf-8 -*-
# try something like

from text_utils import cram

#@caching
def index():
    response.files.append(URL(r=request,c='static',f='css/prettyCheckboxes.css'))
    response.files.append(URL(r=request,c='static',f='js/prettyCheckboxes.js'))

    def timetable():
        q = db.activity.type!='poster'
        #q &= db.activity.type!='project'
        q &= db.activity.status=='accepted'
        q &= db.activity.scheduled_datetime!=None
        rows = db(q).select(db.activity.id,
                            db.activity.title,
                            db.activity.track,
                            db.activity.status,
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
    
        activities = {None: ""}
        activities.update(dict([(row.id, row) for row in rows]))
        schedule = dict([((row.scheduled_datetime,
                           row.scheduled_room),
                          row.id) for row in rows])
    
        hidden = {'speakers': {}, 'activities': {}}
        for activity in rows:
            if activity.created_by not in hidden['speakers'] and len(activity.authors)>2:
                u = PluginMModal(title=activity.authors, content="",
                                         callback=URL('authors', args=[activity.created_by]),
                                         close=T('close'), width=50,
                                         height=50)
                hidden['speakers'][activity.created_by] = u
            if activity.id not in hidden['activities']:
                a = PluginMModal(title=activity.title, content="",
                                     callback=URL('content', args=[activity.id]),                                    
                                     close=T('close'),
                                     width=50, height=50)
                hidden['activities'][activity.id] = a

        q = db.partaker.add_me==True
        if 'votes' in request.vars:
            qv = (db.partaker.comment.contains("vote"))
            if request.vars['votes']=='no':
                qv = ~qv
            q &= qv
        rows = db(q).select(db.partaker.activity,
                            db.partaker.user_id.count().with_alias("partakers"),
                            groupby=db.partaker.activity,)
        partakers = dict([(row.partaker.activity, row.partakers) for row in rows])
        
        return rooms, levels, activities, schedule, activities_per_date, slots_per_date, rooms_per_date, hidden, partakers 
    
    rooms, levels, activities, schedule, activities_per_date, slots_per_date, rooms_per_date, hidden, partakers  = cache.ram(
                                   request.env.path_info + "timetable", 
                                   lambda: timetable(), 
                                   time_expire=0)
    schedule_tables = {}

    if auth.user_id:
        myactivities = db(db.partaker.user_id==auth.user_id).select()
    else:
        myactivities = []
        
    #myactivities = db(db.partaker.user_id==auth.user_id).select()

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
                    if activity.authors and \
                       len(activity.authors.strip()) > 1:
                        u = hidden['speakers'][activity.created_by]
                        authors = u.link(cram(activity.authors, 25))
                    else:
                        authors = ''

                    a = hidden['activities'][activity.id]
                    activity_selected = False
                    select_activity = ""
                    label = "activity_selected_%s" % activity.id
                    if auth.user_id and myactivities is not None:
                        response.flash = ""
                        for act in myactivities:
                            if act["activity"] is not None:
                                if (act["activity"].id==activity.id) and (act["add_me"]):
                                    activity_selected = "on"
                        select_activity = INPUT(value=activity_selected,
                                                _type="checkbox",                        
                                                _id=label,
                                                _class="pretty_checkbox",
                                                _onclick="markActivity('activity_selected_%s', '%s');" % (activity.id, activity.id))
                    attendance = partakers.get(activity.id, "")
                    td = TD(select_activity,
                            LABEL(_for=label),a.link(B(cram(activity.title, 50))),
                                   BR(),
                                   authors and \
                                   ACTIVITY_LEVEL_HINT[activity.level] \
                                   or '',
                                   authors and \
                                   I(" %s " % \
                                       (', '.join(activity.categories or \
                                       [])),
                                       BR(), "", authors, "") or "",
                                   IMG(_src=URL(c='static', f='img/warning.png'),
                                       _title=T("our estimate of attendance reaches the room size"),
                                       _style="float:right; border:0;")
                                       if attendance>=ACTIVITY_ROOMS_EST_SIZES[room]
                                       else "",
                                   TAG.SUP(attendance, _style="float:right;") 
                                       if auth.is_logged_in() and auth.has_membership("manager")
                                       else "",
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
             levels=levels, hidden=hidden['activities'].values()+hidden['speakers'].values(),
             schedule_tables=schedule_tables)
    return response.render(d)

@cache(request.env.path_info,time_expire=60*15,cache_model=cache.ram)
def content():
    "Render the activity summary for each modal box in the schedule"
    if not request.args:
        raise HTTP(404)
    activity = db.activity[request.args[0]]
    if not activity.status=='accepted':
        raise HTTP(403)
    return MARKMIN(activity.abstract or '')

@cache(request.env.path_info,time_expire=60*15,cache_model=cache.ram)
def authors():
    "Render the speaker summary for each modal box in the schedule"
    if not request.args:
        raise HTTP(404)
    author = db.auth_user[request.args[0]]
    if not author.speaker:
        raise HTTP(403)
    if author.photo:
        img = IMG(_alt=author.last_name,
                    _src=URL(r=request, c='default',
                             f='fast_download', args=author.photo),
                    _width="100px", _height="100px", 
                     _style="margin-left: 5px; margin-right: 5px; \
                             margin-top: 3px; margin-bottom: 3px; \
                             float: left;").xml()
    else:
        img = ""
    return img + MARKMIN(author.resume or '').xml()

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

@auth.requires_login()
def ics():
    redirect(URL('bookmarks'))
    
def icalendar(user):
    "Export customized schedule as an iCalendar file"
    import datetime, time
    from cStringIO import StringIO
    
    ical = StringIO()
    # get user bookmarked activities, or all the activities if not logged in:
    if user:
        q = db.partaker.user_id==user.id
        q &= db.partaker.activity==db.activity.id
        q &= db.partaker.add_me==True
        filename = "pycon%s-%s-bookmark.ics" % (request.application, user.last_name)
        calname = "%s - %s" % (response.title, user.last_name)
    else:
        q = db.activity.status=='accepted'
        filename = "pycon%s-bookmark.ics" % (request.application)
        calname = "%s" % (response.title, )
    activities = db(q).select(
        db.activity.id,
        db.activity.title, 
        db.activity.scheduled_datetime, 
        db.activity.scheduled_room, 
        db.activity.duration, 
        db.activity.scheduled_room, 
        db.activity.abstract,
        db.activity.authors,
        db.activity.type,
        )
    ical.write('BEGIN:VCALENDAR')
    ical.write('\nVERSION:2.0')
    ical.write('\nX-WR-CALNAME:%s' % calname)
    ical.write('\nX-WR-TIMEZONE:%s' % time.tzname[0])
    ical.write('\nSUMMARY:%s' % response.title)
    ical.write('\nPRODID:-//PyCon %s Bookmarks//%s//EN' % (request.application, 
                                                     request.env.http_host,))
    ical.write('\nCALSCALE:GREGORIAN')
    ical.write('\nMETHOD:PUBLISH')
    format = '%Y%m%dT%H%M%SZ' 
    
    def ical_escape(text):
        tokens = (("\\", "\\\\"), (";", r"\;"), (",", r"\,"), ("\n", "\\n"), ("\r", ""))
        text = text.decode("utf8", "replace")
        for (escape, replacement) in tokens:
            text = text.replace(escape, replacement)
        return text.encode("utf8", "replace")

    for item in activities:
        if not item.scheduled_datetime or not item.duration:
            continue
        url = '%s://%s%s' % (request.env.wsgi_url_scheme, 
                             request.env.http_host,
                             URL(c='activity', f='accepted', args=item.id))
        # convert local times to UTC
        start = item.scheduled_datetime - datetime.timedelta(seconds=-time.timezone)
        ical.write('\nBEGIN:VEVENT') 
        ical.write('\nUID:%s' % url) 
        ical.write('\nURL:%s' % url)
        ical.write('\nDTSTART:%s' % start.strftime(format))
        ical.write('\nDTEND:%s' % (start+datetime.timedelta(minutes=item.duration)).strftime(format))
        ical.write('\nSUMMARY:%s (%s)' % (ical_escape(item.title), str(T(item.type))))
        authors = ical_escape(item.authors) 
        abstract = ical_escape(item.abstract)
        desc = "%s\\n\\n%s" % (authors, abstract)
        ical.write('\nDESCRIPTION:')
        ical.write(desc)
        if item.scheduled_room:
            location = "%s, " % ACTIVITY_ROOMS.get(int(item.scheduled_room), "")
            location += ACTIVITY_ROOMS_ADDRESS.get(int(item.scheduled_room), "")
            ical.write('\nLOCATION:%s' % location)
        ical.write('\nEND:VEVENT')
    ical.write('\nEND:VCALENDAR')
    
    s = ical.getvalue()
    ical.close()
    
    # remove accents
    
    import unicodedata
    if not isinstance(s, unicode):
        s = unicode(s, "utf8", "ignore")
    nkfd_form = unicodedata.normalize('NFKD', s)
    only_ascii = nkfd_form.encode('ASCII', 'ignore')

    return only_ascii, filename


def bookmarks():
    if auth.is_logged_in():
        user_id = auth.user_id
        user = auth.user
    elif request.args:
        user_id = request.args[0]
        url_hash = request.args[1]
        # check security hash is correct
        user = db.auth_user[user_id]
        if not user.security_hash == url_hash:
            user_id = None
    else:
        user = None

    try:
        ical, filename = icalendar(user)
    except Exception, e:
        raise RuntimeError("%s" % e)

    response.headers['Content-Type']='text/calendar' 
    response.headers["Content-Disposition"] \
            = "attachment; filename=%s" % filename
    return ical

    
@auth.requires_membership(role="manager")
def test_ical():
    ret = []
    rows = db(db.auth_user.id>0).select()
    for u in rows:
        try:
            s, fn = icalendar(u)
            ret.append("%s: ok %s %d "% (u.id, fn, len(s)))
        except Exception, e:
            ret.append("%s: err %s" % (u.id, e))
    response.view = "generic.html"
    return {"ret":ret}
