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
        domain = "twitter.com"
        website = Website.objects.filter(domain__iexact=domain)[0]

        ul = []
        
        users = UserName.objects.filter(website=website)
        ul.extend((str(x.name).casefold() for x in users))

        users = UserNumber.objects.filter(website=website)
        ul.extend((str(x.number) for x in users))

        ul = set(ul)
        ol=set()
        for l in sys.stdin.readlines():
            x=l.strip().casefold()
            if x not in ul:
                ol.add(x)
        print(os.linesep.join(sorted(ol)))

