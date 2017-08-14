#!/usr/bin/python
# -*- coding: utf8 -*-

import random
import codecs
import string
import os
import re
import subprocess

from .funcs import dict_recursive_update, replace_markers_in_text


class Encoder(object):
    type = None #название encoder'a
    default_params = {} #параметры по умолчанию

    def __init__(self, **params):
        self.params = dict_recursive_update( self.default_params.copy(), params )
        self.job = params.get('job', None)

    def encode(self, outfile, data={}):
        pass


class EncoderTextEdit(Encoder):
    u"Создание текстового файла с текстом"
    type = 'text_file'
    default_params = {
            'text': '${marker_id}'
        }

    def encode(self, outfile, data={}):
         with codecs.open(outfile, 'wt', encoding='utf8') as outf:
             outf.write(replace_markers_in_text(self.params['text'], data))


class EncoderTextTemplate(Encoder):
    u"Редактирование текстового файла, с подстановкой макросов типа ${name}"
    type = 'text_tmpl_file'
    default_params = { }

    def __init__(self, **params):
        super(EncoderTextTemplate, self).__init__(**params)
        if 'job' in params:
            self.template_file = params['job'].filename

    def encode(self, outfile, data={}):
        with codecs.open(self.template_file, 'rt', encoding='utf8') as inf:
            with codecs.open(outfile, 'wt', encoding='utf8') as outf:
                for inline in inf:
                    inline = replace_markers_in_text(inline, data)
                    outf.write(inline)
        return False


class EncoderImage(Encoder):
    u"Создание картинки с маркером"
    type = 'image_file'
    default_params = {
            'font': {'name': 'Nimbus-Mono-L', 'size': 8, 'color': '#000000'},

            'text': '${marker_id}',
            'position': (0, 0),
            'visible': True,
        }

    def calc_position(self, position):
        if len(position) == 2:
            return position
        elif len(position) == 4:
            return (
                random.randint(position[0], position[1]), 
                random.randint(position[2], position[3])
            )

    def encode(self, outfile, data={}, infile=''):
        text = replace_markers_in_text(self.params['text'], data)
        if self.params['visible']: #картинка в размер текста
            cmd = """convert %s -background white -fill '%s' -font '%s' \
                        -pointsize %i label:'%s' '%s' """ % (
                        self.job.filename,
                        self.params['font']['color'],
                        self.params['font']['name'],
                        self.params['font']['size'],
                        text, outfile)
        else: #мелкий текст на боольшой картинке
            cmd = """convert -size %ix%i xc:white -fill '%s' -font '%s' \
                        -pointsize %i -gravity center -draw "text 0,0 '%s'" '%s' """ % (
                        random.randint(200,400), random.randint(200,600),
                        self.params['font']['color'],
                        self.params['font']['name'],
                        self.params['font']['size'],
                        text, outfile)
        #-kerning 2.5
        subprocess.call(cmd, shell=True)


class EncoderDjvuColor(EncoderImage):
    u"Создание цветной картинки с маркером для djvu"
    type = 'image_color_djvu'

    def encode(self, outfile, data={}):
        text = replace_markers_in_text(self.params['text'], data)
        tmp_filename = '/tmp/%s_%s.ppm' % (data['user_id'], self.job.name)
        x, y = self.calc_position( self.params.get('position', (50,0)) )
        cmd = """convert %s -density 90 -fill '%s' -font '%s' \
                    -pointsize %s -gravity NorthWest -draw "text %i,%i '%s'" '%s' """ % (
                        self.job.filename,
                        self.params['font']['color'],
                        self.params['font']['name'],
                        self.params['font']['size'],
                        x,y,
                        text,
                        tmp_filename)
        #-kerning 2.5
        if subprocess.call(cmd, shell=True) == 0:
            cmd = """ c44 -dpi 200 -slice 72+11+10+10 "%s" "%s.bg44" """ % (tmp_filename, outfile)
            subprocess.call(cmd, shell=True)
        if os.path.isfile(tmp_filename):
            os.remove(tmp_filename)


class EncoderMetaInfoPdf(Encoder):
    u"Добавление в полей в свойства pdf файла"
    type = 'meta_info_pdf'
    default_params = {
            'text': '${marker_id}',
            'field_name': 'ConTeXt.Version',
        }

    def encode(self, outfile, data={}):
        from pdfrw.objects.pdfname import PdfName
        outfile.Info[PdfName(self.params['field_name'])] = replace_markers_in_text(self.params['text'], data)



encoder_by_type = dict([ (x.type, x) for x in
            [ EncoderTextEdit, EncoderTextTemplate, EncoderImage, EncoderDjvuColor, EncoderMetaInfoPdf ]
        ])
