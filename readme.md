# What

Transform a roster into an email with a live image tally.

![](readme-img/roster.png?raw)


![](readme-img/render.png?raw)
# Usage

## Image
```bash
./soccerimg.py 05/31 > rm_me.png && feh rm_me.png && rm rm_me.png
```
OR
```bash
sudo mount --bind . cgi-bin/
(sleep 3; curl 0.0.0.0:8000/cgi-bin/current_roster.png|feh -) &
python -m CGIHTTPServer 
```

Depends on roster tsv (e.g an exported google sheet), defined in `config.ini`.

Roster tsv contains rows of match dates with columns like:

>  date, size, time, Total, ♀, player1, player2 ♀, player3, ....

 * `size` is like 6v6, 8v8
 * `Total` and `♀` count the number of players (all, female) "in" on a given date.
 * A `♀` in the player name column header denotes female.
 * players columns are 0 or 1 for out or in

## Email

Depenends on tsv sheet defined in `config.ini` that should have an "email" column. Hard coded to only take 11 rows. 

`./email_notice.py "this week's message"`

# Config

## config.ini
copy `config.ini.example` template to `config.ini`.


## apache
```
LoadModule cgid_module modules/mod_cgid.so
<Directory /srv/http/pisa_head_count>
        Options ExecCGI
        SetHandler cgi-script
</Directory>
```
