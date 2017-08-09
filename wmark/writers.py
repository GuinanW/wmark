# -*- coding: utf8 -*-

import os
import re
import random

from wmark.funcs import replace_markers_in_text

class Writer(object):
    u"Класс обработки файлов"
    format = None

    def __init__(self, infile, app, **params):
        self.infile = infile
        self.app = app

    def write(self):
        for user in self.app.users.values():
            self.write_for_user('', user, self.app.jobs)

class WriterPdf(Writer):
    format = 'pdf'

    def write_for_user(self, outfile, user, jobs):
        from pdfrw import PdfReader, PdfWriter, PageMerge
        from pdfrw.objects.pdfname import PdfName

        if 'outfile' in self.app.params:
            out_file = replace_markers_in_text( self.app.params['outfile'], {'user_id': user.id} ) #TODO: словарь побольше сделать
        else:
            out_file = replace_markers_in_text( '${user_id}/%s' % (os.path.basename(self.infile), {'user_id': user.id} ) )

        out_file_dir = os.path.dirname( out_file )
        if not os.path.isdir(out_file_dir):
            os.makedirs(out_file_dir)

        trailer = PdfReader(self.infile)

        for (jobname, job) in jobs.items():
            if job.encoder.type in ('meta_info_pdf', ):
                job.encoder.encode(trailer, job.get_data_for_user(user))
                continue

            visibility = job.encoder.params.get('visible', True)
            page_num = job.page_num

            wmarkfn = '/tmp/%s_%s.pdf' % (user.id, page_num)

            job.write_marker_for_user(user, outfile=wmarkfn)
            wmark_trailer = PdfReader(wmarkfn)

            wmark_page = wmark_trailer.pages[0]
            wmark = PageMerge().add(wmark_page)[0]

            page = trailer.pages[page_num]
            mbox = tuple(float(x) for x in page.MediaBox)
            page_x, page_y, page_x1, page_y1 = mbox
            #print page_x, page_y, page_x1, page_y1, wmark.h, wmark.w
            #TODO: position

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

        PdfWriter(out_file, trailer=trailer).write()

class WriterDjvuPrep(Writer):
    format = 'djvu_for_bash'

    def write_for_user(self, outfile, user, jobs):
        for (jobname, job) in jobs.items():
            outfile = replace_markers_in_text(self.app.params.get('outfile', '${user_id}/'), job.get_data_for_user(user))
            outfile = replace_markers_in_text( outfile, {'filename': os.path.basename(job.filename) } )
            d = os.path.dirname(outfile)
            if not os.path.isdir(d): os.makedirs(d)
            job.write_marker_for_user(user, outfile=outfile)


writer_by_format = dict([ (x.format, x) for x in
            [ WriterPdf, WriterDjvuPrep ]
        ])
