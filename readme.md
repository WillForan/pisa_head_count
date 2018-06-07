```bash
./soccerimg.py 05/31 > rm_me.png && feh rm_me.png && rm rm_me.png
```
OR
```bash
sudo mount --bind . cgi-bin/
(sleep 3; curl 0.0.0.0:8000/cgi-bin/roster.py|feh -) &
python -m CGIHTTPServer 
```

