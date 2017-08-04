#!/usr/bin/python
# -*- coding: utf8 -*-

import random
import codecs
import string
import os
import re

from .markers import marker_by_type

SEPARATOR_CSV=';'


class User(object):
    def __init__(self, name, user_id, **params):
        self.name = name
        self.id = user_id

    def __str__(self):
        return '%s(%s)' % (self.name, self.id)


class Job(object):
    def __init__(self, name='', filename=None, marker_params=None):
        self.name = name
        self.users = {}
        self.marker = None

    #TODO: заглушка
    @property
    def markers(self):
        return self.marker.markers
        
    def generate_markers(self, typ='int', length=6, **params):
        if typ == 'str':
            self.marker = marker_by_type['random_str'](max_len=length, **params)
        else:
            self.marker = marker_by_type['random_int'](10**length-1, 0)
        print self.users
        self.marker.generate(self.users.values())

    def get_marker_for_user(self, user):
        return self.markers[user.id]

    def export_passwords(self, filename):
        pass

    def write_marker(self, mutable_func, **params):
        for (user_id, marker_id) in self.markers.items():
            user_data = {
                'marker_id': marker_id,
                'user_id'  : user_id,
            }
            mutable_func(user_data, self.name, **params)


class App(object):
    def __init__(self):
        self.jobs = {}
        self.users = {}

    def get_job(self, jobname):
        return self.jobs.get(jobname, None)

    def set_job(self, job):
        if job.users == {}:
            job.users = self.users
        self.jobs[job.name] = job

    def import_users(self, filename):
        if not os.path.isfile(filename):
            raise "Not input file"
            
        with open(filename, 'rt') as inf:
            headers = inf.readline().strip().split(SEPARATOR_CSV)
            for line in inf:
                data = dict(zip(headers, line.strip().split(SEPARATOR_CSV)))
                if 'name' in data and 'user_id' in data:
                    us = User(**data)
                    self.users[us.id] = us

    def import_jobs(self, filename):
        return '' #TODO:
        #simplejson.loads(re.sub('//.*$', '', open('zz/params.json' ,'rt').read(), flags=re.M))
        if not os.path.isfile(filename):
            return False
        with open(filename, 'rt') as inf:
            headers = inf.readline().strip().split(SEPARATOR_CSV)
            job_names = []
            for h in headers:
                if h not in ('user_id', 'name'):
                    job_names.append(h)
                    j = Job(h)
                    self.set_job(j)
            
            for line in inf:
                data = dict(zip(headers, line.strip().split(SEPARATOR_CSV)))
                if 'name' in data and 'user_id' in data:
                    us = User(**data)
                    self.users[us.id] = us
                for j in job_names:
                    self.jobs[j].users[us.id] = self.users[us.id]
                    self.jobs[j].markers[us.id] = data[j]
        print self.jobs
        
    def export_jobs(self, filename):
        job_names = sorted([ x for x in self.jobs.keys() if x in self.jobs ])
        headers = ['name', 'user_id'] + job_names
        
#        with codecs.open(filename, 'wt', encoding='utf8') as outf:
        with open(filename, 'wt') as outf:
            outf.write(SEPARATOR_CSV.join(headers)+'\n')
            for user_name in sorted(self.users.keys()):
                us = self.users[user_name]
                s = '%s%s%s%s' % (us.name, SEPARATOR_CSV, us.id, SEPARATOR_CSV)
                s += SEPARATOR_CSV.join([ str(self.jobs[j].markers[us.id]) for j in job_names ])
                outf.write(s+'\n')

