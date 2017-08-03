#!/usr/bin/python
# -*- coding: utf8 -*-

import random
import codecs
import string
import os
import re

SEPARATOR_CSV=';'

def generate_random_int_markers(users, max_num=1e7, min_num=0):
    "Генерирование неповторяющихся числовых маркеров для списка пользователей"
    user_markers = {}
    m = -1
    marker_generates = [m, ]
    
    for us in users:
        while m in marker_generates:
            m = random.randint(min_num, max_num)
        user_markers[us] = m
        marker_generates.append(m)
    return user_markers

def generate_random_str_markers(users, max_len=6, min_len=None, lowercase=False, digits=True, special_chars=''):
    if not min_len:
        min_len = max_len
    if min_len == max_len:
        marker_len = max_len
    else:
        marker_len = random.randint(min_len, max_len)

    tmpl_str = '' #строка с используемыми символами
    if lowercase: tmpl_str += string.ascii_lowercase
    else: tmpl_str += string.ascii_letters
    if digits: tmpl_str += string.digits
    if special_chars: tmpl_str += special_chars
    tmpl_len = len(tmpl_str)

        
    user_markers = {}
    m = ''
    marker_generates = [m, ]
    
    for us in users:
        while m in marker_generates:
            m = ''.join([ tmpl_str[random.randint(0, tmpl_len-1)] for _ in xrange(marker_len) ])
        user_markers[us] = m
        marker_generates.append(m)
    return user_markers
    

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
        self.markers = {}
        
    def generate_markers(self, typ='int', length=6, **params):
        users_id = self.users.keys()
        if typ == 'str':
            self.markers = generate_random_str_markers(users_id, max_len=length, **params)
        else:
            self.markers = generate_random_int_markers(users_id, 10**length-1, 0)

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

def write_mutate_file(infile, outfile, data={}):
    re_key = re.compile('\$\{(.*?)\}')
    
    with codecs.open(infile, 'rt', encoding='utf8') as inf:
        with codecs.open(outfile, 'wt', encoding='utf8') as outf:
            for inline in inf:
                ret = re_key.search(inline)
                if ret:
                    for (k,v) in data.items():
                        kt = '${%s}' % (k,)
                        inline = inline.replace(kt, str(v))
                outf.write(inline)
    return False
