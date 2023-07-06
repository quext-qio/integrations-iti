import base64
import hashlib
import json
import Crypto

class Utilities:

    def encrypt(raw, SECRET_KEY):
        """
        Encryption of the raw string using the custom created secret key
        """
        BS = 16
        key = hashlib.md5(SECRET_KEY.encode('utf8')).hexdigest()[:BS]
        def pad(s): return s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
        if isinstance(raw, bytes):
            raw = raw.decode('utf-8')
        raw = pad(raw).encode("UTF-8")
        iv = Crypto.Random.new().read(Crypto.Cipher.AES.block_size)
        cipher = Crypto.Cipher.AES.new(key.encode("UTF-8"), Crypto.Cipher.AES.MODE_CBC, iv)
        return base64.urlsafe_b64encode(iv + cipher.encrypt(raw)).decode('utf-8')


    def decrypt(encryptedString, encrypted_key):
        key = base64.b64decode(encrypted_key)

        encryptedObj = json.loads(base64.b64decode(encryptedString).decode())

        IV = base64.b64decode(encryptedObj['iv'])
        encrypedValue = base64.b64decode(encryptedObj['value'])

        decobj = Crypto.Cipher.AES.new(key, Crypto.Cipher.AES.MODE_CBC, IV)
        data = decobj.decrypt(encrypedValue)
        return Crypto.Util.Padding.unpad(data, 16)