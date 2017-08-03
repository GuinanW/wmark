#!/usr/bin/python
# -*- coding: utf8 -*-

import random
import os
import codecs

def generate_random_int_markers(users, max_num=1e7, min_num=0):
    "Генерирование неповторяющихся числовых маркеров для списка пользователей"
    user_marker = {}
    marker_generates = [-1, ]
    m = -1
    
    for us in users:
        while m in marker_generates:
            m = random.randint(min_num, max_num)
        user_marker[us] = m
        marker_generates.append(m)
    return user_marker

def write_to_file_djvu(infile, outfile, data='', linenum=3):
    with codecs.open(infile, 'rt', encoding='utf8') as inf:
        with codecs.open(outfile, 'wt', encoding='utf8') as outf:
            i=0
            for inline in inf:
                i += 1
                outf.write(inline)
                if i == linenum:
                    outf.write(data)
    return False



def generate_djvu_metainfo(marker_id, user_id, outf=None):
    meta_marker='''(note "n%s")''' % (marker_id, )
    return meta_marker


def generate_djvu_text(marker_id, user_id, outf=None):
    return '''(word 4144 3031 4568 4903 "i%s")''' % (marker_id, )

    
def generate_djvu_ant(marker_id, user_id, outf=None):
    return '''(maparea "#22" "%s" (rect 2954 3429 5 5))''' % (marker_id, )


if __name__ == '__main__':
    markers = generate_random_int_markers(['us', ])
    
    for (user_id, marker_id) in markers.items():
        out_file_dir = os.path.join('_generate', user_id)
        if not os.path.isdir(out_file_dir):
            os.makedirs(out_file_dir)
        print out_file_dir, marker_id
        
        infile_meta = '0340.meta'
        marker = generate_djvu_metainfo(marker_id, user_id)+'\n'
        write_to_file_djvu( infile_meta, os.path.join(out_file_dir, infile_meta), marker, linenum=1) 

        infile_meta = '0823.ant'
        marker = generate_djvu_ant(marker_id, user_id)+'\n'
        write_to_file_djvu( infile_meta, os.path.join(out_file_dir, infile_meta), marker)
        
