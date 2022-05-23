from django.core.management.base import BaseCommand, CommandError
from retconpeople.models import UserName, UserNumber, Website, Person
from sharedstrings.models import Strings
from django.conf.locale import LANG_INFO
from django.db import transaction,IntegrityError
from django.db.models import Count
import requests
import sys
import os


class Command(BaseCommand):
    help = 'Checks users for invalid name formats, and replaces with existing strings or creates new ones as required.'
    def add_arguments(self, parser):
        parser.add_argument('-y',required=False,action='store_true')
        #parser.add_argument('domain', nargs=1, type=str)
        pass

    def cleanup_bad_prefix(self,prefix):
        uman=UserName.objects
        l=list(uman.filter(name__name__istartswith=prefix))
        for u in l:
            try:
                bad_ss=u.name
                fixed= bad_ss.name.replace(prefix,'')
                with transaction.atomic():
                    existing_usernames=UserName.objects.filter(name__name__iexact=fixed,website_id=u.website_id)
                    if existing_usernames.exists():
                        print("Replaced {} with {} for \n\t{}".format(u,existing_usernames[0],existing_usernames[0].belongs_to))
                        u.delete()
                    else:
                        #no such string so create it and
                        u.name=Strings(name=fixed)
                        u.name.save()
                        u.save()
            except Exception as e:
                print("Exception occured tying to fix {} =>{}".format(bad_ss.name,fixed))
                print(e)
                
                # #try to clean up the bad shared strig might error if referenced elsewhere so that's fine
                # try:
                #     bad_ss.delete()
                # except:
                #     pass
    def handle(self, *args, **options):
        if not options['y']:
            print("This utility replaces usernames for common cases without regard for username case or special character meaning per site.")
            print("pass y flag to confirm you have understood the risk.")
            sys.exit(-1)
        self.cleanup_bad_prefix('http://')
        self.cleanup_bad_prefix('https://')
        self.cleanup_bad_prefix('@')
        # UserName.objects.filter(name_id=None).delete()
        # for un in UserName.objects.all():
        #     with transaction.atomic():
        #         try:
        #             name=un.name
        #         except Strings.DoesNotExist:
        #             un.delete()
        # for p in Person.objects.annotate(cnt=Count('usernames')).filter(cnt=1):
        #     uns=p.usernames.first().name.name
        #     si=Strings.objects.filter(name__iexact=uns)
        #     pl=Person.objects.filter(usernames__name__in=si)
        #     n=pl.count()
        #     min_id= min([x.id for x in pl])
        #     if n>1:
        #         if p.id != min_id:
        #             p.delete()

        
        #uman.filter(name__name__istartswith='https://')



        



