#!/usr/bin/python
# -*- coding: utf8 -*-

import random
import codecs
import string
import os
import re

from common import App, Job, write_mutate_file

import subprocess

def im_write_text(text, filename='', visibility=False):
    if visibility: #картинка в размер текста
        cmd = """convert -background white -fill '#dddddd' -font 'DejaVu-Sans-Mono-Bold' \
                    -pointsize 12 label:'%s' '%s' """ % (text, filename)
    else: #мелкий текст на боольшой картинке
        cmd = """convert -size %ix%i xc:white -fill '#000000' -font 'Nimbus-Mono-L' \
                 -pointsize 8 -gravity center -draw "text 0,0 '%s'" -monochrome '%s' """ % (
                    random.randint(200,400), random.randint(200,600), text, filename)
    #-kerning 2.5 
    subprocess.call(cmd, shell=True)

def marker_for_file(user_data, jobname, **params):
    print user_data, jobname, params
    
    out_file_dir = os.path.join('_generate', user_data['user_id'])
    if not os.path.isdir(out_file_dir):
        os.makedirs(out_file_dir)
    write_mutate_file(jobname, os.path.join(out_file_dir, jobname), user_data)


def mutate_pdf_file(infile, user, jobs):
    from pdfrw import PdfReader, PdfWriter, PageMerge
    from pdfrw.objects.pdfname import PdfName

    out_file_dir = os.path.join('_out', user.id)
    if not os.path.isdir(out_file_dir):
        os.makedirs(out_file_dir)

    filename = os.path.join(out_file_dir, os.path.basename(infile))
    print filename, user, jobs
        
    trailer = PdfReader(infile)

    for (jobname, job) in jobs.items():
        visibility = False
        if jobname.startswith('v'):
            visibility = True
            jobname = jobname.replace('v', '')
            
        if not jobname.isdigit(): continue
        pn = int(jobname)
        
        wmarkfn = '/tmp/%s_%s.pdf' % (user.id, pn)
        
        im_write_text(job.get_marker_for_user(user), wmarkfn, visibility)
            
        wmark_trailer = PdfReader(wmarkfn)

        wmark_page = wmark_trailer.pages[0]
        wmark = PageMerge().add(wmark_page)[0]

        page = trailer.pages[pn]
        mbox = tuple(float(x) for x in page.MediaBox)
        page_x, page_y, page_x1, page_y1 = mbox
        print page_x, page_y, page_x1, page_y1, wmark.h, wmark.w
        
        #wmark.scale(0.02)
        if visibility:
            wmark.y = int(page_y + wmark.h + 40)
            wmark.x = int(page_x1 - wmark.w - 40)
        else:
            wmark.y = random.randint(int(page_y), int(page_y1 - wmark.h)) + 40
            wmark.x = random.randint(int(page_x), int(page_x1 - wmark.w)) + 40

        PageMerge(page).add(wmark, prepend=not visibility).render()

        del wmark_trailer
        os.remove(wmarkfn)
    
    if 'meta_info' in jobs:
        trailer.Info[PdfName('ConTeXt.Version')] = 'v%s' % (jobs['meta_info'].get_marker_for_user(user), )
    PdfWriter(filename, trailer=trailer).write()


if __name__ == '__main__':
    jobs_file = '_jobs_pdf.csv'
    infile_pdf = '_in/book.pdf'

    app = App()
    app.import_jobs(jobs_file)
    if app.users == {}:
        app.import_users('_users.csv')
    
    files_tmpl = ['meta_info', '310', '584', '94', 'v54', 'v615']

    for tmpl in files_tmpl:
        j = app.get_job(tmpl)
#        print tmpl, j.markers
        if not j:
            j = Job(tmpl)
            app.set_job(j)
            if tmpl.startswith('v'):
                j.generate_markers(length=4)
            else:
                j.generate_markers(length=6)

    for us in app.users.values():
        mutate_pdf_file(infile_pdf, us, app.jobs)
    

    app.export_jobs(jobs_file)
