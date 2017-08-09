# -*- coding: utf8 -*-

import re

def dict_recursive_update(dict1, dict2):
    u"аналог dict1.update(dict2) с разворачиванием словарей внутри"
    out = dict1.copy()
    for (k, v) in dict2.items():
        if type(v) == dict:
            if type(out.get(k, None)) == dict:
                out[k] = dict_recursive_update(out[k], v)
            else:
                out[k] = v.copy()
        else:
            out[k] = v
    #out.update(dict2)
    return out


def replace_markers_in_text(text='', data={}):
    u"замена макросов ${name} в тексте"
    ret = re.search('\$\{(.*?)\}', text)
    if ret:
        for (k, v) in data.items():
            kt = '${%s}' % (k,)
            text = text.replace(kt, str(v))
    return text
