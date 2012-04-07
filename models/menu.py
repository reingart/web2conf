# coding: utf8

#############################################
# Insert Sponsors Logo
#############################################

sponsors=db(db.sponsor.id>0).select(orderby=db.sponsor.number)
response.sponsors={}
for sponsor in sponsors:
    if sponsor.level:
        response.sponsors.setdefault(sponsor.level, []).append(sponsor)

#randomize sponsors...
##import random
##random.shuffle(response.sponsors[str(SPONSOR_LEVELS[1])])
