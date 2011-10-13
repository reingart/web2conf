#!/usr/bin/python

# helper utility for creating badge layout.

# uses badge.rfxml as the master, 
# generates badge_full which is what the site uses.

# badge_full has copies of things, 
# this process eliminates the need to manually update the copies.
# copies the badge objects to the 2nd badge (what becomes the back)
# copies the biz-card objects to all the un-used tickets.

# badge_samp is for generating the sample thumbnail png.
# not generating the full thing, and then croping most of it saves some cpu


from dabo.lib import xmltodict
import copy

def pt2f(pt):
    return float(pt.strip("'").split()[0])

def get_attrib_val(obj, attrib):
    for attribs in obj['children']:
        if attribs['name']==attrib:
            return attribs['cdata']

def set_attrib_val(obj, attrib, val):
    for attribs in obj['children']:
        if attribs['name']==attrib:
            attribs['cdata'] = val

# get master copy into a dict
rf=open('badge.rfxml').read()
rfd=xmltodict.xmltodict(rf)

objs=rfd['children'][7]['children'][1]['children']
newobjs=copy.deepcopy(objs)

for obj in newobjs:
    x = pt2f(get_attrib_val(obj,'x'))
    y = pt2f(get_attrib_val(obj,'y'))
    comment = get_attrib_val(obj,'Comment')
    if x <= 290 and y >=370 and comment == "'copy badge'":
        print comment
        # found a badge object, copy it, shift it 288 points to the right.
        newobj=copy.deepcopy(obj)
        x = get_attrib_val(obj,'x')
        newx = "'%s pt'" % (pt2f(x)+288)
        set_attrib_val(newobj, 'x', newx )
        objs.append(newobj)

    if 260-115<=y<=260 and comment=="'copy biz'":
        print comment
        # found a ticket object, 
        # copy it into the other ticket locations (3x4 grid of 199x115 tickets)
        for row in range(4):
            for col in range(3):
                # 0,0 is the original, 
                # so don't make a 2nd copy of it.
                if (row,col)!=(0,0):
                    newobj=copy.deepcopy(obj)
                    x = get_attrib_val(obj,'x')
                    newx = "'%s pt'" % (pt2f(x)+199*col)
                    set_attrib_val(newobj, 'x', newx )
                    newy = "'%s pt'" % (y-115*row)
                    set_attrib_val(newobj, 'y', newy )
                    objs.append(newobj)

rfxml = xmltodict.dicttoxml(rfd)
open('badge_full.rfxml','w').write(rfxml)



