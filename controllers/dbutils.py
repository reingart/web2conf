# -*- coding: utf-8 -*-
# intente algo como

response.generic_patterns = ["*",]

def index(): return dict(message="hello from dbutils.py")


@auth.requires((db(db.auth_user).count() < 1) or \
               (auth.has_membership(role="manager")), \
               requires_login=False)
def data():
    datafile = os.path.join(request.folder, "private/db.csv")
    if request.args[0] == "export":
        result = db.export_to_csv_file(open(datafile, "wb"))
    elif request.args[0] == "import":
        result = db.import_from_csv_file(open(datafile, "rb"))
    else:
        raise HTTP(500, "action not supported")
    return dict(action=request.args[0], result=result)

@auth.requires_membership("manager")
def movefieldvalues():
    form = SQLFORM.factory(Field("from_table"), Field("from_field"), Field("to_field"))
    moved = 0
    if form.process().accepted:
        for r in db(db[form.vars.from_table]).select():
            value = r[form.vars.from_field]
            if not value in (None, ""):
                r.update_record({form.vars.to_field:value,})
                moved += 1
        return dict(form=form, moved=moved)
    else:
        return dict(form=form)

@auth.requires_membership("manager")
def pg_keywords():
    from gluon import reserved_sql_keywords
    keywords = reserved_sql_keywords.POSTGRESQL
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
