#!/usr/bin/python
# -*- coding: utf8 -*-

import random
import codecs
import string
import os
import re
import subprocess

from common import generate_random_int_markers, generate_random_str_markers
from common import App, Job, write_mutate_file

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


def one_marker_for_user():
    markers = generate_random_int_markers(['us', ])

    files_tmpl = [f for f in os.listdir('.') 
                    if f[f.rfind('.'):] in ('.txt', '.meta', '.ant') ]
    print files_tmpl

    for (user_id, marker_id) in markers.items():
        out_file_dir = os.path.join('_generate', user_id)
        if not os.path.isdir(out_file_dir):
            os.makedirs(out_file_dir)
        print out_file_dir, marker_id
        
        user_data = {
            'marker_id': marker_id,
            'user_id'  : user_id,
        }

        for infile_meta in files_tmpl:
            write_mutate_file(infile_meta, os.path.join(out_file_dir, infile_meta), user_data)

#    #загоняем пароли
#    for user_id in users:
#        out_file_dir = os.path.join('_generate', user_id)
#        with codecs.open(os.path.join(out_file_dir, '_pass'), 'wt') as f:
#            f.write(generate_random_str_markers(13))


def marker_for_file(user_data, jobname, **params):
    out_file_dir = os.path.join('_generate', user_data['user_id'])
    if not os.path.isdir(out_file_dir):
        os.makedirs(out_file_dir)
    write_mutate_file(jobname, os.path.join(out_file_dir, jobname), user_data)


def im_write_text(user_data, jobname, **params):
    out_file_dir = os.path.join('_generate', user_data['user_id'])
    if not os.path.isdir(out_file_dir):
        os.makedirs(out_file_dir)

    text = user_data['marker_id']
    filename = os.path.join(out_file_dir, jobname)
    tmp_filename = '/tmp/%s_%s.ppm' % (user_data['user_id'], jobname)
    if params.get('visibility', False):
        cmd = """convert %s -fill '#bbbbbb' -density 90 -font 'DejaVu-Sans-Mono-Bold' \
                -pointsize 16 -gravity SouthEast -draw "text 150,100 '%s'" '%s' """ % (jobname, text, tmp_filename)
    else:
        cmd = """convert %s -fill '#fafafa' -density 90 -font 'Nimbus-Mono-L-Bold' \
                -pointsize 24 -draw "text %i,%i '%s'" '%s' """ % (
                        jobname, random.randint(300,500), random.randint(400,800),
                        text, tmp_filename)
    #-kerning 2.5 
    if subprocess.call(cmd, shell=True) == 0:
        cmd = """ c44 -dpi 200 -slice 72+11+10+10 "%s" "%s.bg44" """ % (tmp_filename, filename)
        subprocess.call(cmd, shell=True)
    os.remove(tmp_filename)

if __name__ == '__main__':
    app = App()
    app.import_jobs('_jobs.csv')
    if app.users == {}:
        app.import_users('_users.csv')
    
    files_tmpl = [f for f in os.listdir('.') 
                    if os.path.isfile(f) and f[f.find('.'):] in ('.txt', '.meta', '.ant', '.h.png', '.v.png', '.pass') ]

    for tmpl in files_tmpl:
        j = app.get_job(tmpl)
        tmpl_ext = tmpl[tmpl.find('.'):]

        if not j:
            j = Job(tmpl)
            app.set_job(j)
            if tmpl_ext in ('.pass'):
                j.generate_markers(typ='str', length=14)
            elif tmpl_ext in ('.v.png'):
                j.generate_markers(typ='int', length=4)
            else:
                j.generate_markers(length=6)

        if tmpl_ext in ('.h.png'):
            j.write_marker(im_write_text)
        elif tmpl_ext in ('.v.png'):
            j.write_marker(im_write_text, visibility=True)
        else:
            j.write_marker(marker_for_file)

    app.export_jobs('_jobs.csv')
