#!/usr/bin/python
# badge.py
# generates badges for PyCon
# both pdf for printing, and png for display on a web page.
# expects to find pdf417_enc.4.4

import subprocess
from cStringIO import StringIO
import Image,ImageFile

BARCODE_FIELDS=[ 'id', 'first_name', 'last_name', 'company_name', 
        'address1', 'address2', 'city', 'state', 'zip_code', 
        'phone_number', 'email', 'attendee_type', ]

def err_missing( message='Badge generation error.'):
    session.flash=T(message+'  Notify web administrator.')
    redirect(URL(r=request,c='default',f='index',args=[],vars={}))

def ds_to_wad(row):
    """
    dataset to wad of data in the format the bar code scanner expects.
    >>> ds_to_wad(test_dataset()[0])[:41]
    '1234\\x03Ivan\\x03Krsti\\xc4\\x87\\x03Ico\\x03123 Main St.\\x03Apt 1a'

    """

    # convert each field to string, 
    # delimit char 3, terminte chr 26 (^Z, 0x16)
    wad =  '\03'.join([ '%s'%row[f] for f in BARCODE_FIELDS ])+'\26'

    return wad

def mk_barcode(data_to_encode):

    """
    makes a barcode png out of the passed data.
    
    https://sourceforge.net/projects/pdf417encode/
    pdf417prep and pdf417_enc need to be in the path.

    3 steps: 
    prep,  (not sure why this is a seperate step)
    encode to image
    convert to png.
    """

    # make prepped data
    p = subprocess.Popen(["pdf417prep"],
        stdin=subprocess.PIPE,stdout=subprocess.PIPE,)
    (stdout, stderr) = p.communicate(input=data_to_encode)
    prepped = stdout

    # generate barcode out of prepped data
    p = subprocess.Popen(["pdf417_enc", "-t", "pbm"],
        stdin=subprocess.PIPE,stdout=subprocess.PIPE,)
    (stdout, stderr) = p.communicate(input=prepped)
    img = stdout

    # convert the image to png 
    buffin = StringIO(img)
    p = subprocess.Popen(["pnmtopng", ],
        stdin=subprocess.PIPE,stdout=subprocess.PIPE,)
    (stdout, stderr) = p.communicate(input=img)
    png=stdout

    return png

def badge_png(ds):

    """
    make a badge image based on real data

    >>> badge_png(test_dataset())[1:4]
    'PNG'
    """
    # This is for badge_png preview image:

    try: import poppler
    except:
        err_missing('Python-poppler library not installed; can\'t generate preview.')

    try: from gtk.gdk import Pixbuf,COLORSPACE_RGB
    except: err_missing( 'Library not installed: gtk.gdk; can\'t generate preview.')

    ######

    # get pdf
    pdf = mkpdf(ds,sample=True)

    # render pdf onto pixbuf
    pixbuf = Pixbuf(COLORSPACE_RGB,False,8,286,225)
    doc = poppler.document_new_from_data(pdf,len(pdf),password='')
    page0=doc.get_page(0)
    page0.render_to_pixbuf(0,0,8,11,1,0,pixbuf)
    
    # save pixbuf as png
    # There has to be a better way to get the image?
    lst=[]
    pixbuf.save_to_callback(lambda b,l: l.append(b), 'png', user_data=lst)
    png=''.join(lst)

    return png


def mkpdf(ds, sample=False):
    """
    Return a pdf made from the passed dataset.
    Sample - True when creating a sample badge, 
             includes graphics and perf lines.
    """

    try: from cStringIO import StringIO
    except: err_missing('cStringIO library not installed;')

    try:
	from reportlab.pdfbase import pdfmetrics
	from reportlab.pdfbase.ttfonts import TTFont
    except: err_missing('python-reportlab library missing;')

    try: from dabo.dReportWriter import dReportWriter
    except: err_missing('Dabo Reportwriter not installed.')

    import os

    static_path = '%sstatic/badges/'% request.folder
    xmlfile  = '%s/badge_full.rfxml' % static_path

    # buffer to create pdf in
    buffer = StringIO()

    # register fonts (hardcoded is lame.)  
    # reportlab has some code, trying to figure out how to use it.)
    
    # check the fonts are installed on the system;  error page if not:

    if not (os.access(TRUETYPE_PATH,os.R_OK)|os.access(GSFONTS_PATH,os.R_OK)):
	err_missing('Missing fonts; unable to generate badge(s).')
                 
    pdfmetrics.registerFont(TTFont("FreeSans", "%s/FreeSans.ttf" % TRUETYPE_PATH))

# what happens here if these font paths don't exist?
#  will pdfmetrics handle the error gracefully, or do you need try/except here?
    afmFile = os.path.join(GSFONTS_PATH, 'n019004l.afm')
    pfbFile = os.path.join(GSFONTS_PATH, 'n019004l.pfb')
    justFace = pdfmetrics.EmbeddedType1Face(afmFile, pfbFile)
    faceName = 'NimbusSanL-Bold' # pulled from AFM file
    pdfmetrics.registerTypeFace(justFace)
    justFont = pdfmetrics.Font('NimbusSanL-Bold',
                               faceName,
                               'WinAnsiEncoding')
    pdfmetrics.registerFont(justFont) 

    afmFile = os.path.join(GSFONTS_PATH, 'n019003l.afm')
    pfbFile = os.path.join(GSFONTS_PATH, 'n019003l.pfb')
    justFace = pdfmetrics.EmbeddedType1Face(afmFile, pfbFile)
    faceName = 'NimbusSanL-Regu' # pulled from AFM file
    pdfmetrics.registerTypeFace(justFace)
    justFont = pdfmetrics.Font('NimbusSanL-Regu',
                               faceName,
                               'WinAnsiEncoding')
    pdfmetrics.registerFont(justFont) 
    # end of register fonts code.

    for row in ds:

        # make a barcode for each row, add it to the dataset
        wad=ds_to_wad(row)
        row['barcode']=mk_barcode(wad)
    
        # bod: badge on demand.  
        # set bod in each row
        row['bod']=not sample


    # generate the pdf in the buffer, using the layout and data
    try:
        rw = dReportWriter(OutputFile=buffer, ReportFormFile=xmlfile, Cursor=ds)
        rw.write()
    except:
        err_missing('ReportWriter write failing... ')

    # get the pdf out of the buffer
    pdf = buffer.getvalue()
    buffer.close()

    return pdf

def mkall():
    """
    badges for everone.

    >>> mkall()[:8]
    '%PDF-1.3'
    """

    ds = [row for row in db().select(db.auth_user.ALL, orderby=db.auth_user.last_name)]
    # for some reason this gives te barcode heartburn:
    # ds = db().select(db.auth_user.ALL, orderby=db.auth_user.last_name)

    pdf = mkpdf(ds,sample=False)
    response.headers['Content-Type']='application/pdf'
    response.headers['Content-Disposition'] = 'filename=badge_all.pdf'

    return pdf


# test functions

def test_dataset(source='dict'):
    """
    returns a dataset sutible for passing to mkpdf()
    
    source=dict uses a hardcoded dict.
    source=first pulls a record from the db (where id=1)

    >>> test_dataset()[0]['name']
    'Ivan Krsti\\xc4\\x87'
     
    """
 
    def static(): 
        row={'id': 1234, 'first_name':'Ivan', 'last_name': 'Krsti\xc4\x87', 
        'name':'Ivan Krsti\xc4\x87', 
        'badge_line1':'laptop.org', 'badge_line2':'Sprint Leader: OLPC',
            'key_note':True, 'speaker':True, 'vendor':True,
            'session_chair':True, 'sponsor':True,
            't_shirt_size':'L',
            'company_name': 'Ico',
            'address1':'123 Main St.', 'address2':'Apt 1a',
        'city': 'Anytown', 'state':'XX', 'zip_code':'12345-6789', 
        'phone_number': '123-456-7890', 'email':'ivan@example.com', 
        'attendee_type':'A+', 
        'food_preference': 'normal',
            }
        """ normal vegetarian vegan kosher halal """        
        return row

    def first_in_db():
        row = db().select(db.auth_user.ALL)[0]
        return row

    def name_as_data():
        """
        use the fild names as the data
        """
        row = first_in_db()
        for k in row.keys(): row[k]=k
        return row

    row = {'dict': static(),
          'first': first_in_db(),
          'fields': name_as_data(),
         }[source]
    
    return [row]

def firstds(): 
    """
    returns the first row from wherever badge data comes from

    >>> firstds()[0]['id']
    1

    {'badge_line1': 'http://www.tatapo.com', 'vendor': True, 't_shirt_size': 'man/2xlarge', 'badge_line2': 'http://www.tatapo.com', 'id': 1, 'speaker': True, 'sponsor': True, 'name': 'cemoso0', 'key_note': True, 'session_chair': True}
    """ 
    return test_dataset('first')
 
def test_pdf():
    """ 
    dynamically generate a badge from sample data.
    return a pdf of the badge sutible for printing on badge stock.
    """

    ds = test_dataset('fields')+ \
        test_dataset('dict')+ \
        test_dataset('first')

    pdf = mkpdf(ds,sample=True)
    
    response.headers['Content-Type']='application/pdf' 
    response.headers['Content-Disposition'] = 'filename=badge.pdf'

    return pdf

def test_png():
    """
    returns a png made from a pdf made from test data

    >>> test_png()[:20]
    '\\x89PNG\\r\\n\\x1a\\n\\x00\\x00\\x00\\rIHDR\\x00\\x00\\x01\\x1e'

    """
    ds = test_dataset('first')
    png = badge_png(ds)
    response.headers['Content-Type']='image/png' 
    return png
     
def badge_pdf():
    """ 
    dynamically generate a badge from data.
    return a pdf of the badge sutible for printing on badge stock.
    """
    # from simple examples:
    # return dict(request=request) #,session=session,response=response)

    tbl=request.args[0]
    this_id=request.args[1]

    rows = [db(db[tbl].id == this_id).select()[0]]
    pdf = mkpdf(rows)
    response.headers['Content-Type']='application/pdf' 
    response.headers['Content-Disposition'] = 'filename=badge.pdf'
    return pdf

def test_bc():
    """
    >>> test_bc()[:20]
    '\\x89PNG\\r\\n\\x1a\\n\\x00\\x00\\x00\\rIHDR\\x00\\x00\\x01^'

    """
    # use the field names as the data, delimit with char 3.
    wad =  '\03'.join(BARCODE_FIELDS) 
    img = mk_barcode(wad)

    response.headers['Content-Type']='image/png' 
    return img


