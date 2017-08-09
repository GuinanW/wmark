#!/usr/bin/python
# -*- coding: utf8 -*-

import random
import codecs
import string
import os
import re

from .markers import marker_by_type
from .encoders import encoder_by_type
from .writers import writer_by_format
from wmark.funcs import replace_markers_in_text


SEPARATOR_CSV=';'

class User(object):
    def __init__(self, name, user_id, **params):
        self.name = name
        self.id = user_id

    def __str__(self):
        return '%s(%s)' % (self.name, self.id)


class Job(object):
    def __init__(self, name='', filename='', params={}):
        self.name = name
        self.filename = filename
        self.__page_num__ = params.get('page_num', None)

        self.users = {}
        self.app = None

        self.encoder = None
        self.marker = None
        if 'marker' in params and 'type' in params['marker'] and params['marker']['type'] in marker_by_type:
            self.marker = marker_by_type[ params['marker']['type'] ](**params['marker'])

        if 'encoder' in params and params['encoder'] in encoder_by_type:
            self.encoder = encoder_by_type[params['encoder']](job=self, **params)

    @property
    def page_num(self):
        if self.__page_num__:
            return self.__page_num__
        if type(self.filename) == int:
            self.__page_num__ = self.filename
        else:
            ret = re.search('([0-9]+)', self.filename)
            if ret:
                self.__page_num__ = int(ret.group())
        return self.__page_num__

    def generate_markers(self, typ='int', length=6, **params):
        self.marker.generate(self.users.values())

    def get_marker_for_user(self, user):
        return self.marker.get_user( user )

    def get_data_for_user(self, user):
        marker_id = self.marker.get_user( user )
        return {
            'marker_id': marker_id,
            'user_id'  : user.id,
            'user_name' : user.name,
            'job_name' : self.name,
            'job_filename': self.filename
        }

    def write_marker_for_user(self, user, **params):
        user_data = self.get_data_for_user(user)
        if 'outfile' in params:
            outfile = params['outfile']
        else:
            outfile = replace_markers_in_text( os.path.join(self.app.params.get('outfile', ''), str(self.filename)), user_data )
        if self.encoder:
            self.encoder.encode(outfile, user_data)

    def write_markers(self, **params):
        for user in self.users.values():
            self.write_marker_for_user(user)


class App(object):
    def __init__(self, filename_params=None):
        self.jobs = {}
        self.users = {}
        self.writer = None
        self.params = {}
        if filename_params:
            self.load(filename_params)

    def get_job(self, jobname):
        return self.jobs.get(jobname, None)

    def set_job(self, job):
        if job.users == {}:
            job.users = self.users
        self.jobs[job.name] = job
        job.app = self

    def load(self, filename_params=None):
        import json
        text = re.sub('//.*$', '', open(filename_params ,'rt').read(), flags=re.M)
        params = json.loads(text)

        if 'users' in params:
            self.import_users(params['users'])

        if 'format' in params and params['format'] in writer_by_format:
            self.writer = writer_by_format[params['format']](params.get('infile'), self)

        for j in params.get('jobs', {}):
            for f in j.get('files', ['', ]):
                if 'name' in j:
                    jobname = '%s_%s' % (j['name'], f)
                else:
                    jobname = '%s_%s_%s' % (j.get('encode', 'unk'), j.get('marker', {}).get('type', 'unk'), f)
                f = os.path.join( params.get('template_dir', ''), f )
                self.set_job( Job(jobname, f, j) )

        self.import_markers(self.params.get('markers', '_markers.csv'))

        for job in self.jobs.values():            
            job.generate_markers()
        self.params = params

    def import_users(self, filename):
        if not os.path.isfile(filename):
            raise "Not input users file %s" % (filename, )

        with open(filename, 'rt') as inf:
            headers = inf.readline().strip().split(SEPARATOR_CSV)
            for line in inf:
                data = dict(zip(headers, line.strip().split(SEPARATOR_CSV)))
                if 'name' in data and 'user_id' in data:
                    us = User(**data)
                    self.users[us.id] = us

    def import_markers(self, filename):
        if not os.path.isfile(filename):
            return False
        with open(filename, 'rt') as inf:
            headers = inf.readline().strip().split(SEPARATOR_CSV)
            job_names = []
            for line in inf:
                data = dict(zip(headers, 
                            [ s.strip('"') for s in line.strip().split(SEPARATOR_CSV)
                        ]))
                if 'user_id' not in data or data['user_id'] not in self.users:
                    continue
                
                user = self.users[data['user_id']]

                for (jobname, job) in self.jobs.items():
                    if jobname in data:
                        try: 
                            value = job.marker.convert_from_string(data[jobname])
                            job.marker.set_user(user, value, True)
                        except: pass

    def export_jobs(self, filename):
        job_names = sorted([ x for x in self.jobs.keys() if x in self.jobs ])
        headers = ['name', 'user_id'] + job_names

        with open(filename, 'wt') as outf:
            outf.write(SEPARATOR_CSV.join(headers)+'\n')
            for user_name in sorted(self.users.keys()):
                us = self.users[user_name]
                s = '"%s"%s"%s"%s' % (us.name, SEPARATOR_CSV, us.id, SEPARATOR_CSV)
                s += SEPARATOR_CSV.join([ '"%s"' % (self.jobs[j].get_marker_for_user(us), ) for j in job_names ])
                outf.write(s+'\n')

    def run(self):
        if self.writer:
            self.writer.write()
        self.export_jobs(self.params.get('markers', '_markers.csv'))
        
