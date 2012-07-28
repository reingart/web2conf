# coding: utf8

TEST_ADDRESS = "reingart@gmail.com"
BCC_ADDRESS = ['reingart@gmail.com', 'jbc.develop@gmail.com']
AUTHOR_BODY="""
%(authors)s:

Le escribimos para recordarle que su charla '''%(title)s''' ha sido %(status)s.

La fecha y hora asignada es: %(scheduled_datetime)s en el aula %(scheduled_room)s.

Le solicitamos confirmar los datos y revisar los comentarios de la charla ingresando en:
https://ar.pycon.org/2011/activity/confirm/%(id)s
De presentarse algún inconveniente rogamos comunicarse con los organizadores a la brevedad.

IMPORTANTE: Es obligatorio completar sus datos personales (perfil): entidad a la que pertenece (incluyendo links), su reseña biográfica (breve) y subir una foto (tamaño mínimo 100px por 100px), ingresando en:
https://ar.pycon.org/2011/user/profile

Puede ver ejemplos en:
https://ar.pycon.org/2011/activity/speakers

Por consultas generales escribir a pyconar2011@gmail.com o a la lista pyconar2011@listas.usla.org.ar

Desde ya muchas gracias

PyCon Argentina 2011
"""

# -----------------------------------------------------------------------------

ATTENDEE_BODY="""
%(first_name)s %(last_name)s:

Le recordamos que este Viernes 23 y Sábado 24 es la Conferencia de Python Argenina 2011:

http://ar.pycon.org/2011

IMPORTANTE: Por cuestiones de organización le solicitamos confirmar su presencia ingresando en:

http://ar.pycon.org/2011/user/confirm/%(id)s/%(hash)s

La confirmación es OBLIGATORIA. *CUPOS LIMITADOS*

De presentarse algún inconveniente, puede entrar a su perfil y confirmar alli su asistencia:

https://ar.pycon.org/2011/user/profile

Si no ingreso password al inscribirse o lo ha olvidado, puede generar uno nuevo en:

https://ar.pycon.org/2011/user/password

Puede consultar la agenda del evento en:

http://ar.pycon.org/2011/schedule/

Por consultas generales escribir a pyconar2011@gmail.com o a la lista pyconar2011@listas.usla.org.ar

Desde ya muchas gracias

PyCon Argentina 2011
"""


def index(): return dict(message="hello from mailing.py")


@auth.requires(auth.has_membership(role='manager'))
def authors():

    #TODO: track sent mails!
    
    ret  = []
    
    form = SQLFORM.factory(
        db.activity.status,
        Field("subject", "string", default="[PyConAr2011]: Confirmar fecha/hora y completar datos personales"),
        Field("body", "text", default=AUTHOR_BODY),
        Field("test", "boolean", default=True, 
              comment="Only sent a mail to test address"),
        )

    if form.accepts(request.vars, session):
        
        query = db.activity.created_by==db.auth_user.id
        query &= db.activity.status==form.vars.status

        testing = form.vars.test
        
        for row in db(query).select():
            try:
                subject = form.vars.subject
                d = dict(row.activity)
                d['status'] = T(row.activity.status)
                d['scheduled_room'] = ACTIVITY_ROOMS[int(row.activity.scheduled_room)] #TODO: represents
                body = form.vars.body % d
    
                attachments = []#[Mail.Attachment(payload=open(cred), filename=filename),]
                
                if True:
                    mail.send(testing and TEST_ADDRESS or row.auth_user.email,
                          subject,
                          body, # (body.encode("utf8"), None),
                          attachments,
                          bcc=not testing and BCC_ADDRESS or [])
            
                #db.commit()
                ret.append("Ok %s %s" % (row.activity.title, row.auth_user.email))
                if testing: break
            except Exception, e:
                if testing: raise
                ret.append("Fallo %s %s: %s" % (row.activity.title, row.auth_user.email, e))
    elif form.errors:
        response.flash = "Corrija el form!"
    else:
        response.flash = "Complete el form!"
        
    return dict(form=form, result=mail.result, ret=ret, total=len(ret))


@auth.requires(auth.has_membership(role='manager'))
def attendees():
    response.view = "generic.html"
    #TODO: track sent mails!
    
    ret  = []
    
    form = SQLFORM.factory(
        Field("subject", "string", default="[PyConAr] Confirmar Asistencia a la Conferencia Python - 23 y 24 Sept. 2011"),
        Field("body", "text", default=ATTENDEE_BODY),
        Field("test", "boolean", default=True, 
              comment="Only sent a mail to test address"),
        )

    if form.accepts(request.vars, session, keepvalues=True):
       
        query = db.auth_user.id>0
        testing = form.vars.test
        
        for row in db(query).select(orderby=db.auth_user.id):
            try:
                subject = form.vars.subject
                u = row
                d = dict(row)
                s= "%s-%s-%s-%s-%s" % (u.last_name, u.first_name, u.email, u.created_by_ip, u.created_on)
                import hashlib
                d['hash'] = hashlib.md5(s).hexdigest()
        
                body = form.vars.body % d
    
                attachments = []#[Mail.Attachment(payload=open(cred), filename=filename),]
                
                if True:
                    mail.send(testing and TEST_ADDRESS or row.email,
                          subject,
                          body, # (body.encode("utf8"), None),
                          attachments,
                          bcc=not testing and BCC_ADDRESS or [])
            
                #db.commit()
                ret.append("Ok %s %s" % (row.id, row.email,))
                if testing: break
            except Exception, e:
                if testing: raise
                ret.append("Fallo %s %s: %s" % (row.id, row.email, e))
    elif form.errors:
        response.flash = "Corrija el form!"
    else:
        response.flash = "Complete el form!"
        
    return dict(form=form, result=mail.result, ret=ret, total=len(ret))
