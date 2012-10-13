#!/usr/bin/python
# badge.py
# generates badges 
# both pdf for printing, and png for display on a web page.
# expects pyfpdf

# import template (older web2py version)
# newer versions
try:
    from gluon.contrib.pyfpdf import Template
except ImportError:
    raise #Template = local_import('pyfpdf.template').Template

import os
import image_utils

def index():
    "Contact card info page for each attendee"
    q = db.auth_user.email==request.vars.email
    q &= db.auth_user.include_in_delegate_listing==True
    person = db(q).select().first()
    return dict(person=person)
    
@auth.requires_login()
def edit():
    "Form to update badge data"
    
    # edit the current user info (or from another user if manager)
    if request.args and auth.has_membership(role='manager'):
        user_id = request.args[0]
    else:
        user_id = auth.user_id
    user = db(db.auth_user.id==user_id).select().first()
    
    db.auth_user.sponsor_id.comment=XML(A(T('sign up!'),_href=URL('sponsors','sign_up')))

    db.auth_user.first_name.default = user.first_name
    db.auth_user.last_name.default = user.last_name
    db.auth_user.badge_line1.default = user.badge_line1
    db.auth_user.badge_line2.default = user.badge_line2
    db.auth_user.sponsor_id.default = user.sponsor_id
        
    form = SQLFORM.factory(
        db.auth_user.first_name,
        db.auth_user.last_name,
        db.auth_user.badge_line1,
        db.auth_user.badge_line2,
        db.auth_user.sponsor_id,
        )

    if form.accepts(request.vars, session, keepvalues=True):
        db(db.auth_user.id == user_id).update(
                first_name=form.vars.first_name,
                last_name=form.vars.last_name,
                badge_line1=form.vars.badge_line1,
                badge_line2=form.vars.badge_line2,
                sponsor_id=form.vars.sponsor_id,
                )
        response.flash = "Datos actualizados"
        # open a new window with the PDF badge sample:
        response.new_window = URL("sample", args=request.args)
    return {'form': form}



@auth.requires_login()
def sample():
    
    # show the current user badge (or from another user if manager)
    if request.args and auth.has_membership(role='manager'):
        user_id = request.args[0]
    else:
        user_id = auth.user_id
    user = db(db.auth_user.id==user_id).select().first()
    # read elements from db 
    elements = db(db.pdf_element.pdf_template_id==1).select(orderby=db.pdf_element.priority)

    f = Template(format=(75,105),
             elements = list(elements),
             title="Sample Badges", author="web2conf",
             subject="", keywords="")
    f.add_page()

    f['name'] = unicode("%s %s" % (user.first_name or '', user.last_name or ''), "utf8")
    f['company_name'] = unicode("%s %s" % (user.company_name or '', ""), "utf8")
    f['city'] = unicode("%s %s" % (user.city or '', ""), "utf8")
    f['badge_line1'] = unicode(user.badge_line1 or '', "utf8")
    f['badge_line2'] = unicode(user.badge_line2 or '', "utf8")
    if user.country:
        f['flag'] = os.path.join(request.folder, 'static', 'img', FLAGS.get(user.country))
    if user.attendee_type != 'gratis':
        f['attendee_type'] = user.attendee_type

    if user.speaker:
        f['speaker'] = os.path.join(request.folder, 'static', 'badges', "speaker.png")
        f['attendee_type'] = 'DISERTANTE'
        
    # qr-code

    filename = os.path.join(request.folder, 'private', 'qr', "%s.png" % user.id) 
    image_utils.build_qr('http://ar.pycon.org/2012/badge?email=%s' % user.email, filename)
    f['qr'] = filename

    # sponsor logo image:
    
    #fn = 'sponsor.logo.995590468c2f1175.6d732e706e67.png' 
    #fn = "sponsor.logo.b337c3730209cdbf.6d73615f6c6f676f2e706e67.png"
    #fn = "sponsor.logo.a1b1b67475967603.66696572726f5f6c6f676f2e706e67.png"
    #fn = "sponsor.logo.b9d3847ca9270ce7.6d616368696e616c69732e706e67.png"
    if user.sponsor_id:
        fn = db.sponsor[user.sponsor_id].logo
        if fn:
            source = os.path.join(request.folder, 'uploads', fn)
            temp = os.path.join(request.folder, 'private', 'qr', fn) + ".png"
            image_utils.center(source, temp)
            
            # clean company name
            f['company_name'] = ""
        else:
            temp = None 
    else:
        temp = None

    f['sponsor_logo'] = temp
    
    # watermark:
    field = {
            'name': 'homo', 
            'type': 'T', 
            'x1': 65, 'y1': 120, 'x2': 0, 'y2': 0, 
            'font': "Arial", 'size': 30, 'rotate': 45,
            'bold': True, 'italic': False, 'underline': False, 
            'foreground': 0xC0C0C0, 'background': 0xFFFFFF,
            'align': "L", 'text': "SAMPLE", 'priority': 10000}
    f.elements.append(field)
        
    response.headers['Content-Type']='application/pdf'
    return f.render('badge.pdf', dest='S')
    
@auth.requires_membership(role="manager")
def speakers():

    import os.path
    
    # generate sample invoice (according Argentina's regulations)

    speakers = db(db.auth_user.id>684).select(orderby=db.auth_user.id)
    #company_name = "web2conf"
    #attendee_type = "Speaker"
    
    # read elements from db 
    elements = db(db.pdf_element.pdf_template_id==2).select(orderby=db.pdf_element.priority)

    f = Template(format="A4",
             elements = elements,
             title="Speaker Badges", author="web2conf",
             subject="", keywords="")
    
    # calculate pages:
    label_count = len(speakers)
    max_labels_per_page = 5*2
    pages = label_count / (max_labels_per_page - 1)
    if label_count % (max_labels_per_page - 1): pages = pages + 1

    # fill placeholders for each page
    for page in range(1, pages+1):
        f.add_page()
        k = 0
        li = 0
        for speaker in speakers:
            k = k + 1
            if k > page * (max_labels_per_page ):
                break
            if k > (page - 1) * (max_labels_per_page ):
                li += 1
                #f['item_quantity%02d' % li] = it['qty']
                f['name%02d' % li] = unicode("%s %s" % (speaker.first_name, speaker.last_name), "utf8")
                f['company_name%02d' % li] = unicode("%s %s" % (speaker.company_name, ""), "utf8")
                f['city%02d' % li] = unicode("%s %s" % (speaker.city, ""), "utf8")
                if speaker.attendee_type != 'gratis':
                    f['attendee_type%02d' % li] = speaker.attendee_type
                if speaker.attendee_type == 'Disertante':
                    f['speaker%02d' % li] = "/home/web2py/applications/catan2011/static/badges/speaker.png"
                    
                ##f['no%02d' % li] = li

    response.headers['Content-Type']='application/pdf'
    return f.render('invoice.pdf', dest='S')

@auth.requires_membership(role="manager")
def organizers():
    Template = template.Template

    import os.path
    
    # generate sample invoice (according Argentina's regulations)

    speakers = db(db.auth_user.organizer==True).select(orderby=db.auth_user.last_name|db.auth_user.first_name)
    
    # read elements from db 
    elements = db(db.pdf_element.pdf_template_id==3).select(orderby=db.pdf_element.priority)

    f = Template(format="A4",
             elements = elements,
             title="Speaker Badges", author="web2conf",
             subject="", keywords="")
    
    # calculate pages:
    label_count = len(speakers)
    max_labels_per_page = 5*2
    pages = label_count / (max_labels_per_page - 1)
    if label_count % (max_labels_per_page - 1): pages = pages + 1

    # fill placeholders for each page
    for page in range(1, pages+1):
        f.add_page()
        k = 0
        li = 0
        #for speaker in speakers:
        for li in range(1, 11):
           ## k = k + 1
            ##if k > page * (max_labels_per_page ):
            ##    break
            ##if k > (page - 1) * (max_labels_per_page ):
            ##    li += 1
                #f['item_quantity%02d' % li] = it['qty']
                ##f['name%02d' % li] = unicode("%s %s" % (speaker.first_name, speaker.last_name), "utf8")
                ##f['company_name%02d' % li] = unicode("%s %s" % (speaker.company_name.strip(), ""), "utf8")
                f['attendee_type%02d' % li] = "Organizador"
                ##f['no%02d' % li] = li

    response.headers['Content-Type']='application/pdf'
    return f.render('invoice.pdf', dest='S')

def update_speakers():
    q=db(db.author.user_id>0).select()
    ret=[]
    for r in q:
        db(db.auth_user.id==r.user_id).update(attendee_type="Disertante")
        ret.append(r.user_id)
    return dict(ret=ret)
    
def update_organizer():
    form=SQLFORM.factory(Field("first_name"), Field("last_name"), Field("attendee_type", "string", default="Colaborador"))
    if form.accepts(request.vars, session):
        q = db.auth_user.last_name.contains(form.vars.last_name)
        q = q & db.auth_user.first_name.contains(form.vars.first_name)
        if db(q).count()== 1:
            u = db(q).select()[0]
            company = u.company_name and u.company_name or "Instituto Blaise Pascal"
            db(q).update(attendee_type=form.vars.attendee_type, company_name=company)
            u = db(q).select()[0]
            response.flash = "Actualizado: %s, %s (%s)" % (u.last_name, u.first_name, u.id) 
    return dict(f=form)
