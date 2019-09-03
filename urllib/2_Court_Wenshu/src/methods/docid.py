import re
import execjs
from Crypto.Cipher import AES
# from .my_logger import logger


def DecryptInner(pwd, key):
    mode = AES.MODE_CBC
    cipher = AES.new(key, mode, 'abcd134556abcedf'.encode('utf-8'))
    decrypted = cipher.decrypt(bytes.fromhex(pwd))
    return decrypted.split(b'\x10')[0].decode()


def Decrypt(str1, key):
    result = DecryptInner(str1, key)
    return DecryptInner(result, key)


b64tab = {'0': 52, '1': 53, '2': 54, '3': 55, '4': 56, '5': 57, '6': 58, '7': 59, '8': 60, '9': 61, '+': 62, '/': 63,
          'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7, 'I': 8, 'J': 9, 'K': 10, 'L': 11, 'M': 12,
          'N': 13, 'O': 14, 'P': 15, 'Q': 16, 'R': 17, 'S': 18, 'T': 19, 'U': 20, 'V': 21, 'W': 22, 'X': 23, 'Y': 24,
          'Z': 25, 'a': 26, 'b': 27, 'c': 28, 'd': 29, 'e': 30, 'f': 31, 'g': 32, 'h': 33, 'i': 34, 'j': 35, 'k': 36,
          'l': 37, 'm': 38, 'n': 39, 'o': 40, 'p': 41, 'q': 42, 'r': 43, 's': 44, 't': 45, 'u': 46, 'v': 47, 'w': 48,
          'x': 49, 'y': 50, 'z': 51}


def fromBase64(str1):
    str1 = str1.replace('-', '+').replace('_', '/')
    str2 = re.sub('[^A-Za-z0-9\+\/]', '', str1)
    return _decode(str2)


def _decode(a):
    return btou(Base64_atob(a))


def Base64_atob(a):
    return re.sub('[\s\S]{1,4}', cb_decode, a)


def fromCharCode(n):
    return chr(n % 256)


def cb_decode(cccc):
    cccc = cccc.group()
    l = len(cccc)
    padlen = l % 4
    n = (b64tab[cccc[0]] << 18 if l > 0 else 0) | (b64tab[cccc[1]] << 12 if l > 1 else 0) | (
        b64tab[cccc[2]] << 6 if l > 2 else 0) | (b64tab[cccc[3]] if l > 3 else 0)
    # print n
    # chars = [
    #     fromCharCode(n >>> 16),
    #     fromCharCode((n >>> 8) & 0xff),
    #     fromCharCode(n & 0xff)]
    chars = [
        fromCharCode(n >> 16),
        fromCharCode((n >> 8) & 0xff),
        fromCharCode(n & 0xff)
    ]
    p = len(chars) - [0, 0, 2, 1][padlen]
    chars = chars[0:p]
    return ''.join(chars)


re_btou = '|'.join(['[\xC0-\xDF][\x80-\xBF]', '[\xE0-\xEF][\x80-\xBF]{2}', '[\xF0-\xF7][\x80-\xBF]{3}'])


def cb_btou(cccc):
    cccc = cccc.group()
    if len(cccc) == 4:
        cp = ((0x07 & ord(cccc[0])) << 18) | ((0x3f & ord(cccc[1])) << 12) | ((0x3f & ord(cccc[2])) << 6) | (
                0x3f & ord(cccc[3])),
        offset = cp - 0x10000
        # print offsetoffset
        # return (fromCharCode((offset >>> 10) + 0xD800) + fromCharCode((offset & 0x3FF) + 0xDC00))
        return fromCharCode((offset >> 10) + 0xD800) + fromCharCode((offset & 0x3FF) + 0xDC00)
    elif len(cccc) == 3:
        return fromCharCode(((0x0f & ord(cccc[0])) << 12) | ((0x3f & ord(cccc[1])) << 6) | (0x3f & ord(cccc[2])))
    else:
        return fromCharCode(((0x1f & ord(cccc[0])) << 6) | (0x3f & ord(cccc[1])))


def btou(b):
    return re.sub(re_btou, cb_btou, b)


def get_js(data):
    with open('./js/docid.js', 'r') as f:
        js_data = f.read()
    eval_js = execjs.compile(js_data)
    data = eval_js.call('zip_inflate', data)
    return data


def unzip(str1):
    return btou(get_js(fromBase64(str1)))


def getkey(str1):
    js_str = unzip(str1).replace('_[_][_](', 'return ')[:-4]
    c = execjs.compile(js_str)
    #  这个key 可能解析出来是一串大写字母，这里把这种情况过滤掉了
    raw_key = re.findall('KEY="(.[a-z0-9]+)"', c.eval(''))
    if raw_key:
        return raw_key[0].encode('utf-8')
    else:
        # a = logger()
        # a.info('给了脏数据')
        print('给了脏数据')
        return None


def decode_docid(docid, key):
    if key:
        return Decrypt(unzip(docid), key).replace('\f', '')
    else:
        return None
