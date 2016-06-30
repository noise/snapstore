#!/usr/bin/env python
from flask import Flask, Response, request, send_from_directory, url_for, json
from flask.helpers import safe_join
import requests
import os


FILES = os.environ.get('FILES', 'files')
USTORE = 'https://search.apps.ubuntu.com/api/v1'
HEADERS = ['X-Ubuntu-Release', 'X-Ubuntu-Series',
           'X-Ubuntu-Architecture', 'X-Ubuntu-Device-Channel',
           'X-Ubuntu-Wire-Format', 'Authorization']

app = Flask(__name__)
snaps = {}
snaps_by_id = {}


@app.route('/')
def hello():
    return 'Hello snap store example!'


def read_meta(name):
    try:
        fname = safe_join(FILES, name + '.meta')
        with open(fname, 'r') as meta:
            # replace download URLs
            pkg = json.loads(meta.read())
            pkg['download_url'] = url_for('download', name=name + '.snap', _external=True)
            pkg['anon_download_url'] = pkg['download_url']
            return pkg
    except Exception as e:
        print e
        return None


@app.before_first_request
def refresh_meta():
    global snaps, snaps_by_id
    names = [os.path.splitext(n)[0] for n in os.listdir(FILES) if n.endswith('.meta')]
    pkgs = [read_meta(n) for n in names]
    snaps = {pkg['package_name']: pkg for pkg in pkgs}
    snaps_by_id = {pkg['snap_id']: pkg for pkg in pkgs}
    print 'loaded metadata for %d snaps' % len(snaps_by_id)


def _details(name):
    meta = snaps.get(name)
    if meta:
        return meta
    else:
        # passthrough to upstream if we don't have that snap
        # TODO: global toggle for passthrough
        h = {k: v for (k, v) in request.headers if k in HEADERS}
        r = requests.get(USTORE + '/snaps/details/%s' % name, headers=h)
        return r.json()


@app.route('/api/v1/snaps/details/<name>')
def details(name):
    pkg = _details(name)
    return Response(json.dumps(pkg), mimetype='application/hal+json')


@app.route('/api/v1/search')
def search():
    ''' note in 2.0.9 snap install uses the search endpoint
    for package details as well as for snap find '''
    q = request.args.get('q', '')
    if 'package_name' in q:
        name = q.split(':')[1].replace('"', '')
        names = [name]
    else:
        # TODO: hit upstream and merge results
        names = [os.path.splitext(n)[0] for n in os.listdir(FILES)
                 if n.startswith(q) and n.endswith('.meta')]
        if len(names) == 0:
            names = [q]
    data = {'_embedded': {'clickindex:package': [m for m in [_details(n) for n in names] if m]}}
    return Response(json.dumps(data), mimetype='application/hal+json')


@app.route('/api/v1/snaps/metadata', methods=['POST'])
def metadata():
    ''' Metadata is a bulk request from snap refresh that sends a list of
    (snap_id, channel, confinement) tuples. '''
    data = request.get_json(force=True)
    ids = [s['snap_id'] for s in data['snaps']]

    local_ids = [id for id in ids if id in snaps_by_id]
    remote_ids = [id for id in ids if id not in snaps_by_id]

    # print 'local: ', local_ids
    # print 'remote: ', remote_ids
    data = {'_embedded': {'clickindex:package': []}}
    data['_embedded']['clickindex:package'] = [snaps_by_id[id] for id in local_ids]

    if len(remote_ids) > 0:
        h = {k: v for (k, v) in request.headers if k in HEADERS}
        r = requests.post(USTORE + '/snaps/metadata', headers=h, data=request.data)
        up_d = json.loads(r.text)
        data['_embedded']['clickindex:package'].append(up_d['_embedded']['clickindex:package'])

    return Response(json.dumps(data), mimetype='application/hal+json')


@app.route('/download/<name>')
def download(name):
    return send_from_directory(FILES, name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
