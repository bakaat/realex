=========================================
Realex lib for python prepared for django
=========================================

Realex Payments is a leading European online payment gateway, headquartered in Dublin with offices in London and Paris. 
Established 10 years in May 2010, we provide a complete online payment solution to over 5,000 clients including Virgin Atlantic, 
VHI Healthcare, Party Poker, Daft.ie, Aer Lingus, AA Insurance amongst many others.


As one of clients is using realex there was a need to develop simple python library that
can be used with django.

as this lib is not tested, send errors and problems to: support@lukaszbaczynski.com


settings.py:

::

    REALEX_MERCHANTID = "your_merchant_id_here"
    REALEX_SECRET = "your_secret_here"
    REALEX_URL = "https://epage.payandshop.com/epage.cgi"
    

sample usage in a view:

::

    rx = realex.RealexRequest("EUR", 20)
    #as_form and as_fields return html for render (you can use them in templates as well)
    rx.to_form()
    >>> """<form action='https://epage.payandshop.com/epage.cgi' method='POST' >\n 
    >>>    <input  type='hidden' name='ORDER_ID' value='20120125132606-7fb6' />\n
    >>>    <input  type='hidden' name='TIMESTAMP' value='20120125132606' />\n
    >>>    <input  type='hidden' name='MD5HASH' value='b3d4f018e7bfbf99fdfced860a8ea1bd' />\n
    >>>    <input  type='hidden' name='CURRENCY' value='EUR' />\n
    >>>    <input  type='hidden' name='AMOUNT' value='20' />\n
    >>>    <input  type='hidden' name='MERCHANT_ID' value='asdf' />\n
    >>>    <input  type='hidden' name='AUTO_SETTLE_FLAG' value='1' /> \n
    >>>    <input type='submit' value='Proceed to secure server'/></form>"""
    
    rx.to_fields() 
    >>> """<input  type='hidden' name='ORDER_ID' value='20120125132606-7fb6' />\n
    >>>    <input  type='hidden' name='TIMESTAMP' value='20120125132606' />\n
    >>>    <input  type='hidden' name='MD5HASH' value='b3d4f018e7bfbf99fdfced860a8ea1bd' />\n
    >>>    <input  type='hidden' name='CURRENCY' value='EUR' />\n
    >>>    <input  type='hidden' name='AMOUNT' value='20' />\n
    >>>    <input  type='hidden' name='MERCHANT_ID' value='asdf' />\n
    >>>    <input  type='hidden' name='AUTO_SETTLE_FLAG' value='1' />"""
    
sample usage in a template:

::

    {{ rx.to_form|safe }}
    {{ rx.to_fields|safe }}

if you need to (for whatever the reason) customize the values on the fields or add 
additional values, you can (in your view):

::

    fields = {"merchant_id": {"class":"form_field", id:"nice_merchant"}, "currency":{"class":"form_field grey"}}
    form_attr = {"class":"nice_form"}
    
    form = rx.to_form(form_attr=form_attr, fields=fields)
    >>> """<form action='https://epage.payandshop.com/epage.cgi' class='nice_form' method='POST' >\n 
    >>>    <input  type='hidden' name='ORDER_ID' value='20120125133828-a032' />\n
    >>>    <input  type='hidden' name='TIMESTAMP' value='20120125133828' />\n
    >>>    <input  type='hidden' name='MD5HASH' value='7c6f676a4191393d4e3a311c69ddea87' />\n
    >>>    <input  name='CURRENCY' type='hidden' class='form_field grey' value='EUR' />\n
    >>>    <input  type='hidden' name='AMOUNT' value='20' />\n
    >>>    <input  name='MERCHANT_ID' value='asdf' id='nice_merchant' type='hidden' class='form_field' />\n
    >>>    <input  type='hidden' name='AUTO_SETTLE_FLAG' value='1' />\n 
    >>>    \n<input type='submit' value='Proceed to secure server'/></form>"""
    
    fields = rx.to_fields(fields=fields)
    >>> """<form action='https://epage.payandshop.com/epage.cgi' class='nice_form' method='POST' >\n 
    >>>    <input  type='hidden' name='ORDER_ID' value='20120125133828-a032' />\n
    >>>    <input  type='hidden' name='TIMESTAMP' value='20120125133828' />\n
    >>>    <input  type='hidden' name='MD5HASH' value='7c6f676a4191393d4e3a311c69ddea87' />\n
    >>>    <input  name='CURRENCY' type='hidden' class='form_field grey' value='EUR' />\n
    >>>    <input  type='hidden' name='AMOUNT' value='20' />\n
    >>>    <input  name='MERCHANT_ID' value='asdf' id='nice_merchant' type='hidden' class='form_field' />\n
    >>>    <input  type='hidden' name='AUTO_SETTLE_FLAG' value='1' />\n 
    >>>    \n<input type='submit' value='Proceed to secure server'/></form>"""
    
