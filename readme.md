# Usage
```bash
./soccerimg.py 05/31 > rm_me.png && feh rm_me.png && rm rm_me.png
```
OR
```bash
sudo mount --bind . cgi-bin/
(sleep 3; curl 0.0.0.0:8000/cgi-bin/roster.py|feh -) &
python -m CGIHTTPServer 
```

## apache
```
LoadModule cgid_module modules/mod_cgid.so
<Directory /srv/http/pisa_head_count>
        Options ExecCGI
        SetHandler cgi-script
</Directory>
```
