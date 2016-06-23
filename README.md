Minimalist "Store" for snaps.

Edit /etc/environment, add

```
SNAPPY_FORCE_CPI_URL=http://localhost:5000/api/v1/
```

Then bounce snapd

```
sudo service snapd restart
```

Put snaps (named as name.snap) and metadata (named as name.meta) in files/

Supports snap find <name>, snap install <name>

