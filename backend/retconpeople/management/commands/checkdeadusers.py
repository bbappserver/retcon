from django.core.management.base import BaseCommand, CommandError
from retconpeople.models import UserName, UserNumber, Website
from django.conf.locale import LANG_INFO
from django.db import transaction
import requests
import sys,time,random
import os


class Command(BaseCommand):
    help = 'Checks to see if resources for named users are dead (HTTP 404)'
    def add_arguments(self, parser):
        prxhelp="A python substitution string for the actual url to test e.g. https://nitter.net/{}"
        parser.add_argument('domain', nargs=1, type=str)
        parser.add_argument('proxy_domain_format_string', nargs='?', type=str,help=prxhelp)
        parser.add_argument('--head', action='store_true',help='use head instead of get. can save on bandwidth, but unsupported by some servers')
        parser.add_argument('-y', action='store_true',help='Assume yes to all prompts')

    def handle(self, *args, **options):
        # domain="twitter.com"
        domain = options['domain'][0]

        ul = []
        #trim null names
        #UserName.objects.filter(website__domain__iexact=domain,name=None)

        #TODO We shouldn't have to check if name isnull but for some reason we did have to
        site=Website.objects.get(domain__iexact=domain)
        #unl=UserName.objects.filter(status__ne=UserName.STATUS_DEAD,website=site)
        unl=site.user_names.all().exclude(status=UserName.STATUS_DEAD)

        if not options['proxy_domain_format_string'] is None:
            fmt = options['proxy_domain_format_string']
        else:
            fmt=site.user_id_format_string
        i=0
        N= unl.count()
        for u in unl:
            try:
                i+=1
                if i %10 ==0:
                    print("{}/{}".format(i,N))
                    #time.sleep(3*random.random())
                if i%100 ==0:
                    time.sleep(10*random.random())
                #url=fmt.format(u.name)
                url=fmt.format(u.name)
                
                if options['head']:
                    resp=requests.head(url)
                else:
                    resp=requests.get(url)
                #time.sleep(.25*random.random())
                if resp.status_code ==404:

                    if not options['y']:
                        choice=input("{} looks dead, mark as dead?[y/n]".format(u.name))
                    else:
                        choice='y'
                    if choice == 'y':
                        u.status=UserName.STATUS_DEAD
                        u.save()
            except Exception as e:
                print("An exception occured processing username({})".format(u.id))
                print(e)



        



