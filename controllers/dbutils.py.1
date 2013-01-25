# -*- coding: utf-8 -*-
# intente algo como

response.generic_patterns = ["*",]

def index(): return dict(message="hello from dbutils.py")

@auth.requires_membership("manager")
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
    response.generic_patterns = ["*",]
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
