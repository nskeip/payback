# -*- coding: utf-8 -*-

from django.test.client import Client
from django.core.urlresolvers import reverse
from django.utils import unittest
from models import *
from datetime import datetime
import time

from django.http import HttpResponse

def test_view(request):
    return HttpResponse(str(request.user))

class AuthenticateTestCase(unittest.TestCase):
    def setUp(self):
        user = User.objects.create_user('test', 'test', password='test')
        self.user_hash = HashKey(user=user, code='code', key='zzz')
        self.user_hash.save()
        self.client = Client()

    def test_authenticate(self):

        params = {'a': 1, 'b': 2}

        test_view_url = reverse('test_view')
        resp = self.client.get(test_view_url)
        self.assertEqual(resp.content, 'AnonymousUser')

        resp = self.client.get(test_view_url, params)
        self.assertEqual(resp.content, 'AnonymousUser')

        resp = self.client.get(test_view_url, {'code': self.user_hash.code})
        self.assertEqual(resp.content, 'AnonymousUser')

        resp = self.client.get(test_view_url, {'code': self.user_hash.code, 'sign': 'ololo'})
        self.assertEqual(resp.content, 'AnonymousUser')

        date = HashKey.datetime2str(datetime.utcnow())

        data = {
            'code': self.user_hash.code,
            'sign': HashKey.sign({}, self.user_hash.key, date),
        }
        resp = self.client.get(test_view_url, data)
        self.assertEqual(resp.content, self.user_hash.user.username)

        # with params
        data['sign'] = HashKey.sign(params, self.user_hash.key, date)
        data.update(params)
        resp = self.client.get(test_view_url, data)
        self.assertEqual(resp.content, self.user_hash.user.username)

        # bad code
        data['code'] = 'ololo'
        resp = self.client.get(test_view_url, data)
        self.assertEqual(resp.content, 'AnonymousUser')
