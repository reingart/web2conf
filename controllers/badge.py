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
    Template = local_import('pyfpdf.template').Template

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
