# -*- coding: utf8 -*-

from nose.tools import assert_raises, eq_
import random

from wmark.funcs import dict_recursive_update, replace_markers_in_text

class TestRecursiveDictUpdate():
    def test_dict_simple_update(self):
        eq_(dict_recursive_update({1: 1, 2: 2}, {1:2}), {1:2, 2:2})
        eq_(dict_recursive_update({1: 1, 2: 2}, {3:1}), {1:1, 2:2, 3:1})
    
    def test_dict_recursive_update(self):
        eq_(dict_recursive_update({1: {11:11, 12:12}, 2:2}, 
                                  {1: {11:13, 13:13}}), 
                                  {1: {11:13, 12:12, 13:13}, 2:2})

class TestReplaceMarkerInText():
    def test_replace_marker(self):
        data = {'marker_id': 42}
        eq_( replace_markers_in_text('6*9 == ${marker_id}', data), '6*9 == 42' )
        eq_( replace_markers_in_text('${user_id} == ${marker_id}', data), '${user_id} == 42' )
