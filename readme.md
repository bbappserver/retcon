# Retcon ![Django CI](https://github.com/bbappserver/retcon/workflows/Django%20CI/badge.svg)
## Why is it called retcon
 Retcon means retroactive continuity, I needed a name that decribed function and would not conflict with other app names so I choe retcon.

## What does it do?
[Hand waving] Whatever I want.  But mostly it is designed to track meta information files and remote representations of creative works and personalities.  Think of it as the IMDB for niche hobbies.

## How to I run it.
### Initial setup
Install requirements, and initialize the database tables
```
#Install python modules if you need them
python3 -mpip install -r requirements.txt
python3 ./manage.py migrate #Initialize database
python3 ./manage.py importlang #Create language models from system locales
python3 ./manage.py createsuperuser #Create the administrative user
```
### Running
If you updated you need to migrate to bring the database up to date.
```
python3 ./manage.py migrate
```
To run the server
```
python3 ./manage.py runserver
```
There is limited human friendly interactions.  To access human friendly but not great interaction go to
```
http://localhost:8000/admin
```
For machine friendly interaction see
```
http://localhost:8000/api
```

To export a list of users for hydrus
```
http://localhost:8000/api/site/<id>/users.txt
```
e.g.
```
http://localhost:8000/api/site/1/users.txt
```

Models and API are subject to change without notice.  I recommend you abstract out any access to them if you write something that interacts with the system.

### On Creating Website patterns

I recommend quite an elaborate url pattern for capturing websites.  For example the pattern I use for twitter is.
```^(?:https?:\/\/)?(?:www\.)?(?:twitter\.com\/){1,2}([^\/]+)\/?$```
- `^(?:https?:\/\/)?(?:www\.)?` : This pattern captures url with or without scheme and www subdomain
- `twitter\.com\/{1,2}`: The actual domain and trailing slash between one and two times, the second time is for bad url substitiutions. (e.g. `twitter.com/{username}` where `username=twitter.com/foobar`)
- `([^\/]+)`: Actual capture of username string.
- `\/?`: Optional trailing slash

Unfortunatly this can't be just done generically because some sites use a subdomain as their user pattern.
e.g. `username.tumblr.com`

By comparison the substitution pattern is much easer.  Simply use a (python format string)[https://www.python.org/dev/peps/pep-3101/#format-strings] where the item that will be substituted into `{}` is the username.

### About similarities between websites and companies
In may instances company and website records match up almost 1 to 1 seemingly duplicating information, this is just a side effect of many companies having a we presence.  When the archived work is from a company whic became defunt prior to the web it is sensible for them to be seperate.

### Contributing
Contributions and feedback are always welcome.  If you want to complete/suggest a feature, fix a bug, or write some tests feel free to do so and open a pull request.


If you didn't come here from the discord, you should also check out hydrus https://hydrusnetwork.github.io/hydrus/
