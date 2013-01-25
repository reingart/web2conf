# coding: utf8

""" Get default site options (option name, default value) """

TWITTER_HASH = get_option("TWITTER_HASH", "pyconar")
UNAVAILABLE = get_option("UNAVAILABLE", False)
ALLOW_VOTE = get_option("ALLOW_VOTE", False)

# Feeds data
PLANET_DESCRIPTION = get_option("PLANET_DESCRIPTION", 'Conferencia Python Argentina 2012 - Buenos Aires')
PLANET_TITLE = get_option("PLANET_TITLE", 'PyCon Argentina 2012')

EMAIL_VERIFICATION=get_option("EMAIL_VERIFICATION", True)

##response.title=PLANET_TITLE
##response.subtitle=get_option("LAYOUT_SUBTITLE", '')
response.header=(get_option("LAYOUT_HEADER_FIRST", "PyCon Argentina 2012"), get_option("LAYOUT_HEADER_SECOND", "12 al 17 de Noviembre - Quilmes - Buenos Aires"))
response.footer=get_option("LAYOUT_FOOTER", '''Conferencia Nacional del Lenguaje Python <b>Noviembre de 2012</b> en Buenos Aires (organizado por miembros de <a href="http://www.python.org.ar/">PyAr</a>). <br/>
Más Información: <a href="http://python.org.ar/pyar/Eventos/Conferencias">http://python.org.ar/</a>&nbsp;
Contacto: <a href="http://groups.google.com/group/pybaires">pybaires@googlegroups.com</a>''')
response.keywords=get_option("SITE_KEYWORDS", 'python, software libre, web2py, argentina, PyCon, ')
response.description=PLANET_DESCRIPTION

# return an unavailable message if the site has been disabled (only managers allowed)
if (not request.controller in ("appadmin", "user")) or (request.function != "login"):
    if not auth.has_membership("manager"):
        if UNAVAILABLE:
            raise HTTP(503, "<html><body><h1>Service unavailable</h1><div>%s</div><br /><div>%s</div></body></html>" % (T(get_option("UNAVAILABLE_MESSAGE", T("Your request could not be processed due to maintenance issues"))), A(T("Access for site managers"), _href=URL("user", "login"))))
