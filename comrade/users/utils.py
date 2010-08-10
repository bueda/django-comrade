"""
Generate multipass for single sign-on with Tender.

Requires TENDER_API KEY and TENDER_ACCOUNT_KEY to be in the app settings.py.
"""
from django.conf import settings

import base64
import hashlib
import urllib
import operator
import array
import simplejson
from Crypto.Cipher import AES
from datetime import datetime, timedelta

import commonware.log
logger = commonware.log.getLogger('comrade.users.views')

def multipass(user):
    if (not hasattr(settings, 'TENDER_API_KEY')
            and hasattr(settings, 'TENDER_ACCOUNT_KEY')):
        logger.warning('No TENDER_API_KEY or TENDER_ACCOUNT_KEY defined in'
                'settings -- unable to generate multipass key')
        return

    expires = datetime.utcnow() + timedelta(minutes=5)

    message = {
        "unique_id" : user.id,
        "expires" : expires.isoformat(),
        "display_name" : user.get_full_name(),
        "email" : user.email
    }
    block_size = 16
    mode = AES.MODE_CBC

    iv = "OpenSSL for Ruby"
    json = simplejson.dumps(message, separators=(',',':'))
    salted = settings.TENDER_API_KEY + settings.TENDER_ACCOUNT_KEY
    saltedHash = hashlib.sha1(salted).digest()[:16]

    json_bytes = array.array('b', json[0 : len(json)])
    iv_bytes = array.array('b', iv[0 : len(iv)])

    # xor the iv into the first 16 bytes.
    for i in range(0, 16):
        json_bytes[i] = operator.xor(json_bytes[i], iv_bytes[i])

    pad = block_size - len(json_bytes.tostring()) % block_size
    data = json_bytes.tostring() + pad * chr(pad)
    aes = AES.new(saltedHash, mode, iv)
    encrypted_bytes = aes.encrypt(data)

    return urllib.quote(base64.b64encode(encrypted_bytes))
