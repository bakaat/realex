""" Realex for Python version 0.1 | License http://www.lukaszbaczynski.com/mit-license/
    support @ support@lukaszbaczynski.com

    Python library for handling realex payments by Lukasz Baczynski.
    Setup to work for django. you need to set 2 variables in your
    settings.py module:
        REALEX_MERCHANTID = "your_merchant_id_here"
        REALEX_SECRET = "your_secret_here"
        REALEX_URL = "https://epage.payandshop.com/epage.cgi"

"""

#python
import datetime
import hashlib
import uuid

#libs
from django.conf import settings

#local


class MD5CheckError(Exception):    
    """ Rised on MD5hashes mismatch """
    def __str__(self):
        return "Response MD5 hash dismatch"


class PostDictKeyError(Exception):
    """ Rised when required key is missing from post data"""

    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return "Required Key - %s - not present in POST_DATA"%self.value


class RealexRequest(object):
    """ Class creating a request form that can be POST'ed to 
        realex's url.

        rx = RealexRequest("EUR", "20")
        form = rx.as_form()
        fields = rx.as_fields()

        return render_to_response("template.html", {"form": form, "fields": fields, "rx":rx})

        in template:

            {{ rx.as_form|safe }}
            {{ rx.as_fields|safe }}
            {{ fields|safe }}
            {{ form|safe }}
    """
    merchant_id = None
    
    def __init__(self, currency, amount, **kw):
        """ Required currency and amount,
            kw is a dict of any additional values that you want to be returned
            in realex response
        """
        self.merchant_id = settings.REALEX_MERCHANTID

        #setting values required by Realex
        self.currency = currency
        self.amount = amount
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        uid = uuid.uuid4().hex[-4:]
        self.order_id = "%s-%s"%(self.timestamp, uid)
        self.md5hash = hashlib.md5("%s.%s.%s.%s.%s"%(self.timestamp, self.merchant_id, \
            self.order_id, self.amount, self.currency))
        self.md5hash = hashlib.md5("%s.%s"%(self.md5hash.hexdigest(), settings.REALEX_SECRET)).hexdigest()
        self.auto_settle_flag = 1
        
        #setting additional values that will be returned to you
        for k,v in kw.items():
            if k not in self.__dict__:
                self.__dict__[k] = v
        

    def as_form(self, form_attr = {}, fields={}):
        """ outputs data as a string for render as a form.
            you can add classes or other attributes to fields and form
            by passing values in this fashon:
                form_attr = {"class": "fancy_form graybg"}
                fields = {
                    "merchant_id": {"class": "nice_merchant id", "id": "merchantid"}
                    "currency": {"class": "currency_sign", "style": "color:red;"}
                }
        """
        form_init = {"action": settings.REALEX_URL, "method": "POST"}
        form_attr.update(form_init)
        form_str = "<form %s >\n"%(" ".join(["%s='%s'"%(k,v) for k, v in form_attr.items()]))
        form_str = "%s %s \n<input type='submit' value='Proceed to secure server'/></form>"%(\
            form_str, self.as_fields(fields))
        return form_str
        
        
    def as_fields(self, fields={}):
        """ outputs data as a set of hidden fields for display in a form 
            prepared by user

            fields var allows you to throw in fields with additional values you
            may want for styling or whatever other purpouses. sample look of fields is:
            fields = {
                "merchant_id": {"class": "nice_merchant id", "id": "merchantid"}
                "currency": {"class": "currency_sign", "style": "color:red;"}
            }

            name, value, type key will be stripped from fields dictionary

        """
        fields_str = ""
        for k, v in self.__dict__.items():
            field_init = {"name": k.upper(), "value": v, "type": "hidden"}
            field_data = fields.get(k, {})
            field_data.update(field_init)
            fields_str = "%s<input "%fields_str
            prepare_extras = " ".join(["%s='%s'"%(x, z) for x, z in field_data.items()])
            fields_str = "%s %s />\n"%(fields_str, prepare_extras)
        return fields_str


class RealexResponse(object):
    """ Response object that does basic validation and rises exceptions when needed. 
        after the validation is a success, all values are available either by
        dot notation or by __dict__.get()

        try:
            rs = RealexResponse(post_data)
        except PostDictKeyError:
            #Handle response that keys are missing
        except MD5CheckError:
            #Handle response when md5 check did't succed

        order_id = rs.order_id
        my_custom_value = rs.__dict__.get("my_custom_value", None)
    """
    merchant_id = None
    
    def __init__(self, post_data):
        self.merchant_id = settings.REALEX_MERCHANTID
        self.process_post_keys(post_data)


    def process_post_keys(self, post_data):
        required_in_post = ["TIMESTAMP", "RESULT", "ORDER_ID", "MESSAGE", 
                            "AUTHCODE", "PASREF", "MD5HASH"]

        for item in required_in_post:
            if item not in post_data.keys():
                raise PostDictKeyError(item)

        required_in_post.pop("MD5HASH")

        md5hash = hashlib.md5(".".join([post_data[x] for x in required_in_post]))
        md5hash = hashlib.md5("%s.%s"%(md5hash.hexdigest(), settings.REALEX_SECRET))

        if md5hash != post_data["MD5HASH"]:
            raise MD5CheckError()

        post_data.update(self.__dict__)
        self.__dict__ = post_data