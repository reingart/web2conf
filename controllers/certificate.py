# coding: utf8
# try something like
def index(): return dict(message="hello from certificate.py")

def pdf():
    tbl=request.args[0]
    this_id=request.args[1]


    doc = PdfDocument(1)
    doc['nombre'] = 'Juan Perez'
    return doc.render('cert.pdf')
