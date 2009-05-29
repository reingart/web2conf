#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os.path
from optparse import OptionParser

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

head,tail = os.path.split(__file__)
sys.path.insert(1,head)

import ReportDesigner

def reg_font_afm(head,root):
    afmFile = os.path.join(head,root+".afm")
    pfbFile = os.path.join(head,root+".pfb")

    (topLevel, glyphData) = pdfmetrics.parseAFMFile(afmFile)
    faceName=topLevel['FontName']

    justFace = pdfmetrics.EmbeddedType1Face(afmFile, pfbFile)
    pdfmetrics.registerTypeFace(justFace)
    justFont = pdfmetrics.Font(faceName, faceName, 'WinAnsiEncoding')
    pdfmetrics.registerFont(justFont)
    return

def reg_font_ttf(fontname,fontfile):
    pdfmetrics.registerFont(TTFont(fontname,fontfile ))
    return

def reg_font(fontpathname):
    """
    given full path/name.ext of font file,
    split into head,root,ext and punt.
    """

    head,tail = os.path.split(fontpathname)
    root,ext = os.path.splitext(tail)
    if ext=='.ttf': reg_font_ttf(root,fontpathname)
    if ext=='.afm': reg_font_afm(head,root)

    return


def run( options, args ):

    app = ReportDesigner.DesignerController()
    app.setup()

    for fontfile in options.fonts:
        #f=pdfmetrics.getTypeFace(fontname) 
        reg_font(fontfile)

    if args:
        for fileSpec in args:
            form = ReportDesigner.ReportDesignerForm()
            form.editor.openFile(fileSpec)
            form.Visible = True
    else:
        form = ReportDesigner.ReportDesignerForm()
        form.editor.newFile()
        form.Visible = True
    app.start()

if __name__ == "__main__":
    
    parser = OptionParser()
    parser.add_option("-r", "--register-font",
        action="append", dest="fonts", metavar="font",
        help="register the font, one per -r.", )
    (options, args) = parser.parse_args()

    run( options, args )

