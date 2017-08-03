#!/usr/bin/python
# -*- coding: utf8 -*-

import os
import urllib
import re
import lxml.html
import codecs

def get_list(sk_id, dump_file=None, reserv_num=0):
    url='https://skladchik.com/threads/%s/' % (sk_id, )
#    if os.path.isfile('/dev/shm/tmp.html'):
#        data=open('/dev/shm/tmp.html', 'rt').read()
#    else:
    data=urllib.urlopen(url).read()
#        open('/dev/shm/tmp.html', 'wt').write(data)
    eroot = lxml.html.fromstring(data)
    if dump_file:
        outf = codecs.open(dump_file, 'wt', encoding='utf8')
        outf.write('name;user_id\n')

    for x in eroot.xpath('//div[@id="ShareList"]//li//a'):
        user_name = x.text
        user_id = x.attrib.get('data-userid', '')
        if not user_id:
            user_id = re.findall('\.([0-9]+)/', x.attrib.get('href', ''))[0]
        
        if dump_file and user_name and user_id:
            outf.write('%s;%s\n' % (user_name, user_id))

    #запас
    if reserv_num > 0:
        for i in range(reserv_num):
            outf.write('_reserv%i;%s\n' % (i, i))
        
    outf.close()
    
if __name__ == '__main__':
    get_list('41232', '_users_h.csv', 5) #id темы, куда сохранять, сколько резерва
