from django.core.management.base import BaseCommand, CommandError
from retconpeople.models import UserName, UserNumber, Website
from django.conf.locale import LANG_INFO
from django.db import transaction

import sys
import os


class Command(BaseCommand):
    help = 'Checks the newlined list passed to stdin against the list of \
    known usernames and numbers for <domain> and prints unknown ones to STDOUT'

    def add_arguments(self, parser):
        parser.add_argument('domain', nargs=1, type=str)

    def handle(self, *args, **options):
        # domain="twitter.com"
        domain = args['domain']

        ul = []
        #trim null names
        #UserName.objects.filter(website__domain__iexact=domain,name=None)

        #TODO We shouldn't have to check if name isnull but for some reason we did have to
        users = UserName.objects.filter(website__domain__iexact=domain,name__isnull=False)
        ul.extend((str(x.name).casefold() for x in users))

        users = UserNumber.objects.filter(website__domain__iexact=domain)
        ul.extend((str(x.number) for x in users))

        ul = set(ul)
        ol=set()
        for l in sys.stdin.readlines():
            x=l.strip().casefold()
            if x not in ul:
                ol.add(x)
        print(os.linesep.join(sorted(ol)))

