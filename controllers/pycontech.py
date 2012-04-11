# coding: utf8
# try something like

import os

raise RuntimeError("remove this line to use!")

# connect to pycon-tech (django) database
pg=DAL('postgres://postgres:saraza@localhost/pycon2010')

# configure path to common/talkdata
PATH = "C:\\PuTTY\\2010\\"

def index(): return dict(message="hello from pycontech.py")

def navbar():
    # import django navbar
    rows = pg.executesql("SELECT id, name, url, parent_id FROM navbar_navbarentry ORDER BY parent_id, \"order\"")
    db(db.navbar.id>0).delete()
    for row in rows:
        db.navbar.insert(
            id=row[0],
            title=row[1],
            url=row[2],
            parent_id=row[3],
        )
    response.view = "generic.html"
    return dict(rows=rows)
    
def flatpages():
    # import django flatpages
    rows = pg.executesql("SELECT id, url, title, content FROM django_flatpage ORDER BY id")
    db(db.plugin_flatpage.id>0).delete()
    for row in rows:
        parts = row[1].split("/")
        controller =  parts[2]
        function = parts[3] or 'index'
        arg = parts[4:] and parts[4] or ''
        db.plugin_flatpage.insert(
            id=row[0],
            controller=controller,
            function=function,
            arg=arg,
            title=row[2],
            body=row[3],
            lang="es",
            format='HTML',
        )
    response.view = "generic.html"
    return dict(rows=rows)

def users():
    # import django auth_users, gmaps_address and usermgr_profile into auth_user
    sql = """
        select  a.id, a.first_name, a.last_name, a.email, a.date_joined, 
            p.url, p.affiliation, p.bio, p.location, p.email_ok, p.listing_ok, p.sponsor_ok,
            g.latitude, g.longitude
        from auth_user a 
        left join usermgr_userprofile p on p.user_id=a.id
        left join gmaps_gaddress g on g.name=a.username 
        order by a.id
    """
    rows = pg.executesql(sql)
    # remove old users
    db(db.auth_user.id>0).delete()
    for row in rows:
        db.auth_user.insert(
            id=row[0],
            first_name=row[1],
            last_name=row[2],
            email=row[3],
            created_on=row[4],
            personal_home_page=row[5],
            company_home_page=row[5],
            company_name=row[6],
            resume=row[7],
            address=row[8],
            confirmed=row[9],
            include_in_delegate_listing=row[10],
            sponsors=row[11],
            latitude=row[12],
            longitude=row[13],
            country="Argentina", #!!!!!
        )
    response.view = "generic.html"
    return dict(rows=rows)


def talks():
    # import pycontech event/schedule/scheduledevent into activity
    # change FROM order to import events with no proposals 
    #        (keynotes, plenary, lightning, etc.)
    sql = """
select e.id, COALESCE(p.title, e._title), COALESCE(p.duration, e._duration), COALESCE(p.summary, e._summary), p.description, p.submitter_id, p.level, p.categories, 
se.start, se.room_id, e.type
from propmgr_proposal p
left join schedule_event e on p.id = e.proposal_id
left join schedule_scheduledevent se on se.event_id = e.id
 """
    rows = pg.executesql(sql)
    levels = {'B': "Beginner",'I':"Intermediate", 'A':"Advanced", None: ''}
    types = {"E": 'talk', "P": 'plenary', "B": 'break', None: 'talk'}
    # remove old talks
    db(db.activity.id>0).delete()
    for row in rows:
        event_id, title, duration, summary, description, submitter_id, level_id, categories, start, room_id, event_type = row
        autor = db.auth_user[submitter_id]
        authors = autor and "%s %s" % (autor.first_name, autor.last_name) or ''
        status = start and 'accepted' or 'pending'
        activity_id = db.activity.insert(
            authors=authors,
            title=title,
            duration=duration,
            abstract=summary,
            description=description,
            created_by=submitter_id,
            level=levels[level_id],
            scheduled_datetime=start,
            scheduled_room=room_id,
            status=status,
            categories=categories and categories.split(", ") or [],
            confirmed=True,
            type=types[event_type],
        )    
        # insert author(s):
        if submitter_id:     # todo: pycon-tech sometime doesn't have authors!?
            db.author.insert(user_id=submitter_id, activity_id=activity_id)
            # activate speaker flag (for speaker page):
            q = db.auth_user.id==submitter_id
            q &= db.auth_user.speaker==False
            r = db(q).update(speaker=True)
    response.view = "generic.html"
    return dict(rows=rows)


def sponsors():
    # import sponsorship_websitelogo into sponsors
    sql = """
        select  s.id, s.name, s.level, s.index, s.logo, 
            s.url, s.alt
        from sponsorship_websitelogo s
        where s.visible=True
        order by s.level, s.index
    """
    rows = pg.executesql(sql)
    # change the mapping according your event:
    levels = {"8:Organizer": "Organizer", 
           "7:Thanks": "Agradecimiento Especial",
            "3:Gold": "Sponsor Oro",
            "4:Silver": "Sponsor Plata",
            "5:Bronze": "Sponsor Bronce",
            "51:Bronze": "Sponsor Bronce",
            "52:Pyme": "Sponsor Pyme",
            "9:Colaborator": "Colaborador",}
    # remove old sponsors
    db(db.sponsor.id>0).delete()
    for row in rows:
        # Manual uploads (programatically read and store the logo image)
        filename = row[4]
        stream = open(os.path.join(PATH, filename),'rb')
        logo = db.sponsor.logo.store(stream, filename)
        # do the work:
        db.sponsor.insert(
            id=row[0],
            name=row[1],
            level=levels[row[2]],
            number=row[3],
            logo=logo,
            url=row[5],
            alt=row[6],
        )
    response.view = "generic.html"
    return dict(rows=rows)
