import store
import unittest
from flask import json


class StoreTestCase(unittest.TestCase):

    def setUp(self):
        # TODO: setup fixture data, test revision bumps
        store.app.config['TESTING'] = True
        self.c = store.app.test_client()
        self.headers = {
            'X-Ubuntu-Series': 16,
            'X-Ubuntu-Architecture': 'amd64'
        }

    def tearDown(self):
        pass

    def test_hello(self):
        r = self.c.get('/')
        assert 'Hello' in r.data

    def test_details_ok(self):
        ''' snap install bar '''
        r = self.c.get('/api/v1/snaps/details/bar')
        j = json.loads(r.data)
        assert j['package_name'] == 'bar'

    def test_details_empty(self):
        ''' snap install xyzzy '''
        r = self.c.get('/api/v1/snaps/details/xyzzy', headers=self.headers)
        j = json.loads(r.data)
        assert 'No such package' in j['errors']

    def test_search_old_install_path(self):
        ''' snap install bar (<= snapd 2.0.??) '''
        r = self.c.get('/api/v1/search?q=package_name:"bar"')
        j = json.loads(r.data)
        assert j['_embedded']['clickindex:package'][0]['package_name'] == 'bar'

    def test_search_all(self):
        ''' snap find '''
        r = self.c.get('/api/v1/search?q=')
        j = json.loads(r.data)
        assert len(j['_embedded']['clickindex:package']) == 3

    def test_search_partial(self):
        ''' snap find ba '''
        r = self.c.get('/api/v1/search?q=ba')
        j = json.loads(r.data)
        assert len(j['_embedded']['clickindex:package']) == 2

    def test_search_exact(self):
        ''' snap find foobar25 '''
        r = self.c.get('/api/v1/search?q=foobar25')
        j = json.loads(r.data)
        assert j['_embedded']['clickindex:package'][0]['package_name'] == 'foobar25'

    def test_metadata_local(self):
        ''' snap refresh (>= snapd 2.0.??)
        with only snaps from our local repo '''
        r = self.c.post('/api/v1/snaps/metadata',
                        data=json.dumps({'snaps': [
                            {'snap_id': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxbar',
                             'revision': 1, 'confinement': 'strict'}],
                            "fields": ["download_url", "revision"]}),
                        headers=self.headers)
        j = json.loads(r.data)
        assert len(j['_embedded']['clickindex:package']) == 1

    def test_metadata_remote(self):
        ''' snap refresh (>= snapd 2.0.??)
        with only snaps from upstream repo '''
        r = self.c.post('/api/v1/snaps/metadata',
                        data=json.dumps({'snaps': [
                            {'snap_id': 'mVyGrEwiqSi5PugCwyH7WgpoQLemtTd6',
                             'revision': 1, 'confinement': 'strict'}],
                            "fields": ["download_url", "revision"]}),
                        headers=self.headers)
        j = json.loads(r.data)
        assert len(j['_embedded']['clickindex:package']) == 1

    def test_metadata_mixed(self):
        ''' snap refresh (>= snapd 2.0.??)
        with snaps from both local and remote '''
        r = self.c.post('/api/v1/snaps/metadata',
                        data=json.dumps({'snaps': [
                            {'snap_id': 'mVyGrEwiqSi5PugCwyH7WgpoQLemtTd6',
                             'revision': 1, 'confinement': 'strict'},
                            {'snap_id': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxbar',
                             'revision': 1, 'confinement': 'strict'}
                            ],
                            "fields": ["download_url", "revision"]}),
                        headers=self.headers)
        j = json.loads(r.data)
        assert len(j['_embedded']['clickindex:package']) == 2

if __name__ == '__main__':
    unittest.main()
