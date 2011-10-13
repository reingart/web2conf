# coding: utf8
# try something like

#try:
#    from gluon.contrib.pyfpdf import Template
#except ImportError:
# import local module until we can update web2py...
Template = local_import('template').Template

@auth.requires_membership(role="manager")
def speakers():
    template_id = int(request.args[0])
    #attendee_type = request.args[1]
        
    import os.path
    
    speakers = db(db.auth_user.speaker==True).select(orderby=db.auth_user.id)
    #attendee_type = "Speaker"
    
    # read elements from db 
    elements = db(db.pdf_element.pdf_template_id==template_id).select(orderby=db.pdf_element.priority)

    f = Template(format="A4",
             elements = elements,
             title="Speaker Certificate", author="web2conf",
             orientation="Landscape",
             subject="", keywords="")
    
    # fill placeholders for each page
    for speaker in speakers:
        f.add_page()
        f['name'] = unicode("%s %s" % (speaker.first_name, speaker.last_name), "utf8")
        f['attendee_type'] = speaker.attendee_type

    response.headers['Content-Type']='application/pdf'
    return f.render('speaker_cert.pdf', dest='S')
