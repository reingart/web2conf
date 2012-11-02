# coding: utf8

#    plugin_dineromail: DineroMail web2py plugin
#    Copyright (C) 2012 Alan Etkin
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    * Web2py is Licensed under the LGPL license version 3
#    (http://www.gnu.org/licenses/lgpl.html)
#    Copyright (c) by Massimo Di Pierro (2007-2011)
#
#    contact: spametki@gmail.com


# function or lambda, for calling after each payment notification
# example:
# PLUGIN_DINEROMAIL_ON_UPDATE = lambda data: my_function(data["transaction_code"])
# where data stores the updated record fields
# transaction_code is the alphanumeric id used for the web-store button or form

if not "PLUGIN_DINEROMAIL_ON_UPDATE" in globals():
    PLUGIN_DINEROMAIL_ON_UPDATE = None

# Create and keep this variables in private model files
if not "PLUGIN_DINEROMAIL_ACCOUNT" in globals():
    PLUGIN_DINEROMAIL_ACCOUNT = None

if not "PLUGIN_DINEROMAIL_PASSWORD" in globals():
    PLUGIN_DINEROMAIL_PASSWORD = None

if not "PLUGIN_DINEROMAIL_COUNTRY" in globals():
    PLUGIN_DINEROMAIL_COUNTRY = None # mexico, argentina, chile, brasil, ...

PLUGIN_DINEROMAIL_URLS = {"mexico": "http://mexico.dineromail.com/vender/Consulta_IPN.asp",
                          "chile": "http://chile.dineromail.com/vender/Consulta_IPN.asp",
                          "argentina": "http://argentina.dineromail.com/vender/Consulta_IPN.asp",
                          "brasil": "http://brasil.dineromail.com/vender/Consulta_IPN.asp"}

PLUGIN_DINEROMAIL_SHOP_CHECK_IN = {"mexico": None,
                          "chile": None,
                          "argentina": "https://argentina.dineromail.com/Shop/Shop_Ingreso.asp",
                          "brasil": None}

PLUGIN_DINEROMAIL_REPORT_STATUSES = {1: ("Correct"),
                                     2: ("Malformed"),
                                     3: ("Invalid account number"),
                                     4: ("Invalid password"),
                                     5: ("Invalid query type"),
                                     6: ("Ivalid operation ID"),
                                     7: ("Invalid account or password"),
                                     8: ("No operations found"),
                                     9: ("???"),}
                                     
PLUGIN_DINEROMAIL_STATUSES = {1: T("Pending"), 2: T("Credited"),
                              3: T("Cancelled")}
                              
PLUGIN_DINEROMAIL_METHODS = {1: T("DineroMail funds"),
                             2: T("Cash (or third party cash services"),
                             3: T("Credit card"),
                             4: T("Bank account transfer"),
                             5: T("Cash (Oxxo or 7Eleven)")}
                             
PLUGIN_DINEROMAIL_CURRENCIES = {1: T("Pesos/Reales"), 2: T("USD")}

# account movement notifications sent by the webservice
db.define_table("plugin_dineromail_notification",
                Field("posted", "datetime",
                      default=request.now,
                      writable=False,
                      comment=T("Date and time of submission")),
                Field("category", comment=T("Type of notification")),
                Field("operation_type", comment=T("Type of operation")),
                Field("code", comment=T("Operation number")),
                migrate=migrate)

# Stores webservice updated operation status
db.define_table("plugin_dineromail_operation",
                Field("report_status", "integer",
                      represent=lambda status, row: \
                      PLUGIN_DINEROMAIL_REPORT_STATUSES[status]),
                Field("code", unique=True), # webservice operation id
                Field("posted"),
                Field("status", "integer",
                      represent=lambda status, row: \
                      PLUGIN_DINEROMAIL_STATUSES[status]),
                Field("transaction_code"), # client transaction_id
                Field("customer_email"),
                Field("customer_address"),
                Field("customer_comment"),
                Field("customer_name"),
                Field("customer_phone"),
                Field("customer_document_type"),
                Field("customer_document_number"),
                Field("amount", "double"),
                Field("net_amount", "double"),
                Field("method", "integer",
                      represent=lambda method, row: \
                      PLUGIN_DINEROMAIL_METHODS[method]),
                Field("means"),
                Field("installments", "integer"),
                Field("sales_document_type"),
                Field("sales_document_number"),
                Field("item_descriptions", "list:string"),
                Field("item_currencies", "list:integer"),
                Field("item_prices", "list:string"),
                Field("item_quantities", "list:integer"),
                migrate=migrate)

def plugin_dineromail_update_reports(data):
    # retrieve webservice reports
    # TODO: complete transaction xml mapping to local db
    # and return readable report logs
    import urllib
    import urllib2    
    message = None
    updated = 0
    
    query = plugin_dineromail_create_query(data)
    query_data = urllib.urlencode({"DATA": query})
    
    f = urllib2.urlopen(PLUGIN_DINEROMAIL_URLS[PLUGIN_DINEROMAIL_COUNTRY],
                        query_data)
    # apparently dineromail is answering in latin1:
    # 'utf8' codec can't decode byte 0xf1 in position 443: invalid continuation byte
    s = f.read().decode("latin1", "replace").encode("utf8")
    tag = TAG(s)
    
    # check if report is ok
    status = int(tag.element("estadoreporte").flatten())
    if status == 1:
        for operation in tag.elements("operacion"):
            row_data = dict(item_descriptions=list(),
                            item_quantities=list(),
                            item_currencies=list(),
                            item_prices=list())

            row_data["report_status"] = int(tag.element("estadoreporte").flatten())
            row_data["code"] = operation.element("id").flatten()
            row_data["posted"] = operation.element("fecha").flatten()
            row_data["status"] = int(operation.element("estado").flatten())
            row_data["transaction_code"] = \
                operation.element("numtransaccion").flatten()
            row_data["customer_email"] = \
                operation.element("comprador").element("email").flatten()
            row_data["customer_name"] = \
                operation.element("comprador").element("nombre").flatten()
            row_data["customer_document_number"] = \
                operation.element("comprador").element("numerodoc").flatten()
            row_data["amount"] = float(operation.element("monto").flatten())
            row_data["net_amount"] = float(operation.element("montoneto").flatten())
            row_data["method"] = int(operation.element("metodopago").flatten())
            row_data["means"] = operation.element("mediopago").flatten()
            try:
                row_data["installments"] = int(operation.element("cuotas").flatten())
            except ValueError:
                # Invalid installment number
                row_data["installments"] = 0

            for item in operation.elements("item"):
                row_data["item_descriptions"].append(item.element("descripcion").flatten())
                row_data["item_currencies"].append(int(item.element("moneda").flatten()))
                row_data["item_prices"].append(float(item.element("preciounitario").flatten()))
                row_data["item_quantities"].append(int(item.element("cantidad").flatten()))

            # operation id lookup
            row = db(db.plugin_dineromail_operation.code == \
                operation.element("id").flatten()).select().first()
            
            if row is not None:
                row.update_record(**row_data)
                operation_id = row.id
            else:
                operation_id = db.plugin_dineromail_operation.insert(**row_data)
                
            row_data["id"] = operation_id
            updated += 1

            # Send data to the app's callback if defined
            if PLUGIN_DINEROMAIL_ON_UPDATE is not None:
                PLUGIN_DINEROMAIL_ON_UPDATE(row_data)

        message = T("Updated %s operations") % updated
        return (True, message)
    else:
        error = PLUGIN_DINEROMAIL_REPORT_STATUSES[status]
        message = T("Message: %(noops)s. Error: %(error)s") % \
    dict(noops=T("No operations updated"),
         error=T(error))
        ##raise RuntimeError(message)
        return (False, message)

# build a basic query for the remote payment database
def plugin_dineromail_create_query(data):
    if isinstance(data, basestring):
        data = [data,]
    ids = "".join(["<ID>%s</ID>" % o for o in data])
    operations = "<OPERACIONES>%s</OPERACIONES>" % ids

    account = PLUGIN_DINEROMAIL_ACCOUNT
    password = PLUGIN_DINEROMAIL_PASSWORD

    report = 1
    query = """<REPORTE>
  <NROCTA>%(account)s</NROCTA>
  <DETALLE>
    <CONSULTA>
      <CLAVE>%(password)s</CLAVE>
      <TIPO>%(report)s</TIPO>
      %(operations)s
    </CONSULTA>
  </DETALLE>
</REPORTE>""" % {"account": account, "password": password,
                 "report": report, "operations": operations}
    return query

def plugin_dineromail_check_status(code, update=False):
    """ Return transaction status updating
    from webservice if specified.

    code is the id generated for button, form or link
    used in the client application.
    returns the (state, description) of the operation if found or
    (None, None)
    update=<bool> is optional and forces a remote operation
    details update.
    """
    
    report = dict()
    if not isinstance(code, (list, set, tuple)):
        code = [code,]
    elif isinstance(code, dict):
        code = code.keys()
    if update:
        result, message = \
        plugin_dineromail_update_reports(code)
    else:
        result = message = None
    try:
        # Get the locally stored transaction detail
        query = db.plugin_dineromail_operation.code == code[0]
        if len(code) > 0:
            for n, c in enumerate(code):
                if n > 0:
                    query |= db.plugin_dineromail_operation.code == c
        operations = db(query).select()
        for operation in operations:
            report[operation.code] = {"status": operation.status,
                                       "description": PLUGIN_DINEROMAIL_STATUSES[operation.status]}
    except AttributeError, e:
        report[None] = {"status": None,
                        "description": T("No payment records found for codes %s (%s)") % (str(code), e)}
    report["result"] = result
    report["message"] = message
    return report
