'''
Minimalist "Store" for snaps.

Edit /etc/environment, add
  SNAPPY_FORCE_CPI_URL=http://localhost:5000/api/v1/
and bounce snapd

Put snaps (named as name.snap) and metadata (named as name.meta) in files/

Supports snap find <name>, snap install <name>
'''
from flask import Flask, Response, request, url_for, send_from_directory
import sys

FILES = 'files'


app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello basic snap store!"


@app.route("/api/v1/search")
def search():
    ''' note in 2.0.9 snapd still uses search for package details
    before install as well as for find '''
    name = request.args.get('q')
    # hackity hack hack: find passes q=package_name:"foo"
    if 'package_name' in name:
        name = name.split(':')[1].replace('"', '')

    # TODO: sanitize names
    # TODO: replace download URLs in metadata
    try:
        with open(FILES + '/' + name + '.meta', 'r') as meta:
            return Response(meta.read(), mimetype='application/hal+json')
    except Exception as e:
        print e
        return Response('{}', mimetype='application/hal+json')


@app.route("/anon/download-snap/<name>")
def download(name):
    # TODO: sanitize names
    return send_from_directory(FILES, name)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
