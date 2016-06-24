#!/usr/bin/env python
from flask import Flask, Response, request, send_from_directory, url_for, json
from flask.helpers import safe_join

FILES = 'files'


app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello snap store example!'


@app.route('/api/v1/search')
def search():
    ''' note in 2.0.9 snap install uses the search endpoint
    for package details as well as for snap find '''
    name = request.args.get('q')
    # hackity hack hack: find passes q=package_name:"foo"
    if 'package_name' in name:
        name = name.split(':')[1].replace('"', '')

    try:
        fname = safe_join(FILES, name + '.meta')
        with open(fname, 'r') as meta:
            # replace download URLs
            data = json.loads(meta.read())
            pkg = data['_embedded']['clickindex:package'][0]
            pkg['download_url'] = url_for('download', name=name + '.snap',
                                          _external=True)
            pkg['anon_download_url'] = pkg['download_url']
            return Response(json.dumps(data), mimetype='application/hal+json')
    except Exception as e:
        return Response('{}', mimetype='application/hal+json')


@app.route('/download/<name>')
def download(name):
    return send_from_directory(FILES, name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
