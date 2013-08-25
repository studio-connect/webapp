#!/usr/bin/env python
import os
from app import app
from app import db
import unittest
import tempfile


class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_filename = tempfile.mkstemp()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + \
                                                self.db_filename
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        db.create_all()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_filename)

    def add_peer(self):
        rv = self.client.post('/peers/add/', data=dict(
            name='Test1',
            host='::1'
            ))
        return rv

    def test_empty_db(self):
        """Start with a blank database."""
        rv = self.client.get('/peers/')
        assert b'No entries here so far' in rv.data

    def test_index(self):
        rv = self.client.get('/')
        assert b'load' in rv.data

    def test_404_not_found(self):
        rv = self.client.get('/bigbangtheory')
        assert b'Ups, site not found!' in rv.data

    def test_peers_add(self):
        self.add_peer()
        rv = self.client.get('/peers/')
        assert b'Test1' in rv.data
        assert b'Pending' in rv.data
        rv = self.add_peer()
        assert b'IPv6 address already exist' in rv.data

    def test_peers_edit(self):
        self.add_peer()
        rv = self.client.get('/peers/edit/1')
        assert b'Add Peer' in rv.data

        self.client.post('/peers/edit/1', data=dict(
            name='Test2',
            host='::1'
            ))
        rv = self.client.get('/peers/')
        assert b'Test2' in rv.data
        assert b'Test1' not in rv.data
        assert b'Pending' in rv.data

    def test_peers_delete(self):
        self.add_peer()
        self.client.get('/peers/delete/1')
        rv = self.client.get('/peers/')
        assert b'Test1' not in rv.data

    def test_peers_call(self):
        rv = self.client.get('/peers/call/')

    def test_accept_peer(self):
        self.test_api_peer_invite()
        self.client.get('/peers/accept/1')
        rv = self.client.get('/peers/')
        assert b'Pending' in rv.data

    def test_api_peer_status(self):
        self.add_peer()
        self.client.get('/api1/peer_status',
                        environ_base={'REMOTE_ADDR': '::1'})
        rv = self.client.get('/peers/')
        assert b'Online' in rv.data

    def test_api_peer_status_bad(self):
        self.add_peer()
        rv = self.client.get('/api1/peer_status',
                             environ_base={'REMOTE_ADDR': 'BAD'})
        assert b'denied' in rv.data
        rv = self.client.get('/peers/')
        assert b'Pending' in rv.data

    def test_api_peer_invite(self):
        rv = self.client.post('/api1/peers', environ_base={'REMOTE_ADDR': '::1'})
        assert b'true' in rv.data
        rv = self.client.get('/peers/')
        assert b'Invite' in rv.data



if __name__ == '__main__':
    unittest.main()