# Retcon
## Why is it called retcon
 Retcon means retroactive continuity, I needed a name that decribed function and would not conflict iwth other app names so I choe retcon.

## What does it do?
[Hand waving] Whatever I want.  But mostly it is designed to track meta information files and remote representations of creative works and personalities.  Think of it as the IMDB for niche hobbies.

## How to I run it.
### Initial setup
Install requirements, and initialize the database tables
```
#Install python modules if you need them
python3 -mpip install django djangorestframework
python3 ./manage.py migrate #Initialize database
python3 ./manage.py importlang #Create language models from system locales
python3 ./manage.py createsuperuser #Create the administrative user
```
### Running
If you updated you need to migrate to bring the database upt to date.
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
http://localhost:8000/API
```

Models and API are subject to change without notice.  I recommend you abstract out any access to them if you write something that interacts with the system.

### Contributing
Contributions and feedback are always welcome.  If you want to complete/suggest a feature, fix a bug, or write some tests feel free to do so and open a pull request.


If you didn't come here from the discord, you should also check out hydrus https://hydrusnetwork.github.io/hydrus/
