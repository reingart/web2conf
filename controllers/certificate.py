# coding: utf8
# try something like

try:
    from gluon.contrib.pyfpdf import Template
except ImportError:
    # import local module until we can update web2py...
    Template = local_import('template').Template
    raise
    
@auth.requires_membership(role="manager")
def speakers():
    template_id = int(request.args[0])
    speakers = db(db.auth_user.speaker==True).select(orderby=db.auth_user.id)
    return render_pdf(speakers, template_id, "Disertante", "S")

@auth.requires_membership(role="manager")
def attendees():
    template_id = int(request.args[0])
    q = db.auth_user.speaker==False
    q &= db.auth_user.attendee_type == "gratis"
    speakers = db(q).select(orderby=db.auth_user.id)
    return render_pdf(speakers, template_id, "Participante", "A")

@auth.requires_membership(role="manager")
def bono():
    template_id = int(request.args[0])
    q = db.auth_user.speaker==False
    q &= db.auth_user.attendee_type != "gratis"
    speakers = db(q).select(orderby=db.auth_user.id)
    return render_pdf(speakers, template_id, "Participante", "B")
    
def render_pdf(users, template_id, attendee_type, flag=""):    
    # read elements from db 
    elements = db(db.pdf_element.pdf_template_id==template_id).select(orderby=db.pdf_element.priority)

    f = Template(format="A4",
             elements = elements,
             title="Speaker Certificate", author="web2conf",
             orientation="Landscape",
             subject="", keywords="")
    
    # fill placeholders for each page
    for user in users:
        f.add_page()
        s = unicode("%s %s" % (user.first_name, user.last_name), "utf8")
        if user.dni:
            s = u"%s (DNI %s)" % (s, user.dni)
        f['name'] = s
        f['id'] = "%s%s" % (user.id, flag)
        f['attendee_type'] = attendee_type
        #break

    response.headers['Content-Type']='application/pdf'
    return f.render('speaker_cert.pdf', dest='S')
