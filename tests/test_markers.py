# -*- coding: utf8 -*-

from nose.tools import assert_raises
import random


from wmark.common import User
from wmark.markers import *

class TestMarkerRandomInt:
    def setUp(self):
        #self.users = [User('us_%i' % (i,), random.randint(0, 1e7)) for i in range(100)]
        self.users = [User('us_%i' % (i,), i) for i in range(10)]
        self.marker = MarkerRandomInt()
        self.marker.generate( self.users )

    def teardown(self):
        pass

    def test_generate(self):
        assert len(self.marker.markers.keys()) == len(self.users)
        assert len(self.marker.markers.keys()) == len(self.marker.__marker_generates__)

    def test_generate_one(self):
        old_user = self.users[1]
        old_marker_id = self.marker.markers[old_user.id]
        assert old_marker_id == self.marker.get_user(old_user)

        new_user1 = User('us_test_1', 10001)
        assert new_user1.id not in self.marker.markers
        assert self.marker.get_user(new_user1) != None
        assert new_user1.id in self.marker.markers

    def test_validity(self):
        assert self.marker.validity(12)
        assert self.marker.validity(9999999)
        assert self.marker.validity(0)

        assert not self.marker.validity(10000000)
        assert not self.marker.validity(-1)
        assert not self.marker.validity('12')
        assert not self.marker.validity('zz')


class TestMarkerRandomString:
    def setUp(self):
        #self.users = [User('us_%i' % (i,), random.randint(0, 1e7)) for i in range(100)]
        self.users = [User('us_%i' % (i,), i) for i in range(10)]
        self.marker = MarkerRandomString()
        self.marker.generate( self.users )

    def teardown(self):
        pass

    def test_generate(self):
        assert len(self.marker.markers.keys()) == len(self.users)
        assert len(self.marker.markers.keys()) == len(self.marker.__marker_generates__)

    def test_generate_one(self):
        old_user = self.users[1]
        old_marker_id = self.marker.markers[old_user.id]
        assert old_marker_id == self.marker.get_user(old_user)

        new_user1 = User('us_test_1', 10001)
        assert new_user1.id not in self.marker.markers
        assert self.marker.get_user(new_user1) != None
        assert new_user1.id in self.marker.markers
