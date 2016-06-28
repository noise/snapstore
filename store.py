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
        return None


@app.route('/api/v1/details/<name>')
def details(name):
    meta = read_meta(name)
    if meta:
        data = {'_embedded': {'clickindex:package': [meta]}}
        return Response(json.dumps(data), mimetype='application/hal+json')
    else:
        # passthrough to upstream if we don't have that snap
        f = request.args.get('fields')
        h = {k: v for (k, v) in request.headers if k in HEADERS}
        r = requests.get(USTORE + '/search?q=package_name:"%s"&fields=%s' % (name, f), headers=h)
        return Response(json.dumps(r.json()), mimetype='application/hal+json')


@app.route('/api/v1/search')
def search():
    ''' note in 2.0.9 snap install uses the search endpoint
    for package details as well as for snap find '''
    q = request.args.get('q', '')
    if 'package_name' in q:
        name = q.split(':')[1].replace('"', '')
        return details(name)
    else:
        names = [os.path.splitext(n)[0] for n in os.listdir(FILES)
                 if n.startswith(q) and n.endswith('.meta')]
        if len(names) == 0:
            names = [q]
    data = {'_embedded': {'clickindex:package': []}}
    data['_embedded']['clickindex:package'] = [m for m in [read_meta(n) for n in names] if m]
    return Response(json.dumps(data), mimetype='application/hal+json')


@app.route('/download/<name>')
def download(name):
    return send_from_directory(FILES, name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
