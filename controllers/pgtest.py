# coding: utf8
# intente algo como
from gluon import reserved_sql_keywords
keywords = reserved_sql_keywords.POSTGRESQL

def index(): return dict(message="hello from pgtest.py")

@auth.requires_membership("manager")
def test_keywords():
    response.generic_patterns = ["*",]
    report = UL()
    fields = UL()
    for table in db:
        if str(table).upper() in keywords:
            report.append(LI("Table %s is a pg keyword" % table))
        for field in table:
            print "field", str(field)
            if str(field).split(".")[1].upper() in keywords:
                report.append(LI("Field %s is a pg keyword" % field))
            fields.append(LI(str(field)))
    return dict(report=report, fields=fields)
