# Overview

snapstore is a minimalist example of a "store" for snaps, based on the public API specs (https://wiki.ubuntu.com/AppStore/Interfaces/ClickPackageIndex). It allows anyone to host their own collection of snaps for installation on supported platforms.

See http://snapcraft.io for more information on creating and using snap packages.

# Server setup (with snappy)

```
snap install snapstore-example
```

It will be run as a daemon on the default port 5000.


# Server setup (manual)

Install python-virtualenv.

E.g. on Ubuntu 16.04:
```
sudo apt install python-virtualenv
```

Clone this repo:
```
git clone https://github.com/noise/snapstore.git
cd snapstore
```

Setup virtualenv and install dependencies:
```
virtualenv env
. env/bin/activate
pip install -r requirements.txt
```

Run it:
```
python store.py
```


# File management

Put snaps (named as name.snap) and metadata (named as name.meta) in ./files/ (/var/snap/snapstore-example/current/files/ for snap version). We've already included one sample snap (foobar25).


# Client setup

On any distribution supporting snaps (see http://snapcraft.io), install snapd (requires snapd >=2.0.6).

E.g. on Ubuntu 16.04:
```
sudo apt install snapd
```

Edit /etc/environment, add your store URL, e.g.:
```
SNAPPY_FORCE_CPI_URL=http://localhost:5000/api/v1/
```

Then bounce snapd:
```
sudo service snapd restart
```

# Usage

Supports snap find <name>, snap install <name>

```
$ snap find
Name      Version  Developer  Notes  Summary
bar       0.2      testuser   -      This is a bar snap
baz       0.4      testuser   -      This is a baz snap
foobar25  2.5      testuser   -      This is a test snap

$ snap find ba
Name  Version  Developer  Notes  Summary
bar   0.2      testuser   -      This is a bar snap
baz   0.4      testuser   -      This is a baz snap

$ snap install bar

Name  Version  Rev  Developer  Notes
bar   2.5      1    testuser   -

$ snap refresh bar

Name  Version  Rev  Developer  Notes
bar   2.5      2    testuser   -
```

# Known issues

- It's just an example, probably lots!

# TODO

- passthrough/join for find

