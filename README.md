# Realex lib for python #

## About Realex ##
Realex Payments is a leading European online payment gateway,
headquartered in Dublin with offices in London and Paris.
Established 10 years in May 2010, we provide a complete online payment
solution to over 5,000 clients including Virgin Atlantic,
VHI Healthcare, Party Poker, Daft.ie, Aer Lingus,
AA Insurance amongst many others.

## What and why ##

This lib provides a base form class that can handle "request to" and
"response from" Realex hpp payment. You should inherit from RealexFormBase 
and set your auth creds in it's Meta class 

If you've used django, you may find some parts being similar to how django
handles Forms. This said the lib doesn't use django classes as it's supposed to
be web framework agnostic.

## Required settings ##

    REALEX_MERCHANTID = "your_merchant_id_here"
    REALEX_ACCOUNT = "your_realex_account"
    REALEX_SECRET = "your_secret_here"
    REALEX_POST_URL = "https://hpp.realexpayments.com/pay"
        # https://hpp.sandbox.realexpayments.com/pay
    REALEX_RESPONSE_URL = None # optional, specifies the response url for
                               # realex (in case it's different from where you
                               # submit the request from)

sample usage (with django):

    # forms.py
    
    from realex import RealexFormBase
    from django.conf import settings
    
    # override the base class with credentials 
    class RealexForm(RealexFormBase):
    
        class Meta:
            merchant_id = settings.REALEX_MERCHANTID
            account = settings.REALEX_ACCOUNT
            secret = settings.REALEX_SECRET
            endpoint_url = settings.REALEX_POST_URL

    # views.py
    from .forms import RealexForm

    rx = RealexForm("EUR", 20)
    # as_form and as_fields return html for use in your templates

    # template.py

    {{ rx.as_form }}

    # will render into a full form
    >>> """<form action='https://epage.payandshop.com/epage.cgi' method='POST' >\n 
    >>>    <input type='hidden' name='ORDER_ID' value='20120125132606-7fb6' />\n
    >>>    <input type='hidden' name='TIMESTAMP' value='20120125132606' />\n
    >>>    <input type='hidden' name='MD5HASH' value='b3d4f018e7bfbf99fdfced860a8ea1bd' />\n
    >>>    <input type='hidden' name='CURRENCY' value='EUR' />\n
    >>>    <input type='hidden' name='AMOUNT' value='20' />\n
    >>>    <input type='hidden' name='MERCHANT_ID' value='asdf' />\n
    >>>    <input type='hidden' name='AUTO_SETTLE_FLAG' value='1' /> \n
    >>>    <input type='submit' value='Proceed to secure server'/></form>"""

    {{ rx.as_fields }}
    # will render into fields only so that you can provide the form tag around same.
    >>> """<input type='hidden' name='ORDER_ID' value='20120125132606-7fb6' />\n
    >>>    <input type='hidden' name='TIMESTAMP' value='20120125132606' />\n
    >>>    <input type='hidden' name='MD5HASH' value='b3d4f018e7bfbf99fdfced860a8ea1bd' />\n
    >>>    <input type='hidden' name='CURRENCY' value='EUR' />\n
    >>>    <input type='hidden' name='AMOUNT' value='20' />\n
    >>>    <input type='hidden' name='MERCHANT_ID' value='asdf' />\n
    >>>    <input type='hidden' name='AUTO_SETTLE_FLAG' value='1' />"""


if you need to (for whatever the reason) customize the values on the fields or
add additional values, you can (in your view):

    fields = {"merchant_id": {"class":"form_field", id:"nice_merchant"},
              "currency":{"class":"form_field grey"}}
    form_attr = {"class":"nice_form"}

    rx = RealexForm("EUR", 20, form_attr=form_attr, fields=fields)

    template.py

    {{ rx.as_form }}
    >>> """<form action='https://epage.payandshop.com/epage.cgi' class='nice_form' method='POST' >\n
    >>>    <input type='hidden' name='ORDER_ID' value='20120125133828-a032' />\n
    >>>    <input type='hidden' name='TIMESTAMP' value='20120125133828' />\n
    >>>    <input type='hidden' name='MD5HASH' value='7c6f676a4191393d4e3a311c69ddea87' />\n
    >>>    <input name='CURRENCY' type='hidden' class='form_field grey' value='EUR' />\n
    >>>    <input type='hidden' name='AMOUNT' value='20' />\n
    >>>    <input name='MERCHANT_ID' value='asdf' id='nice_merchant' type='hidden' class='form_field' />\n
    >>>    <input type='hidden' name='AUTO_SETTLE_FLAG' value='1' />\n
    >>>    \n<input type='submit' value='Proceed to secure server'/></form>"""

    {{ rx.as_fields }}
    >>> """<form action='https://epage.payandshop.com/epage.cgi' class='nice_form' method='POST' >\n 
    >>>    <input type='hidden' name='ORDER_ID' value='20120125133828-a032' />\n
    >>>    <input type='hidden' name='TIMESTAMP' value='20120125133828' />\n
    >>>    <input type='hidden' name='MD5HASH' value='7c6f676a4191393d4e3a311c69ddea87' />\n
    >>>    <input name='CURRENCY' type='hidden' class='form_field grey' value='EUR' />\n
    >>>    <input type='hidden' name='AMOUNT' value='20' />\n
    >>>    <input name='MERCHANT_ID' value='asdf' id='nice_merchant' type='hidden' class='form_field' />\n
    >>>    <input type='hidden' name='AUTO_SETTLE_FLAG' value='1' />\n
    >>>    \n<input type='submit' value='Proceed to secure server'/></form>"""

Handling response :

    # You can use the same class you used to prepare the request for response
    # handling.
    rx = RealexForm(data=request.POST)
    try:
        rs.is_valid()
    except PostDictKeyError:
        # Handle error for missing required post keys
        pass
    except SHA1CheckError:
        # Handle SHA1 mismatch
        pass

    # rx.cleaned_data is only available after successful validation
    result = rx.cleaned_data
