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
    help = 'Checks to see if resources for named users are dead (HTTP 404)'
    def add_arguments(self, parser):
        #parser.add_argument('domain', nargs=1, type=str)
        pass

    def cleanup_bad_prefix(self,prefix):
        uman=UserName.objects
        l=uman.filter(name__name__istartswith=prefix)
        for u in l:
            bad_ss=u.name
            fixed= bad_ss.name.replace(prefix,'')
            
            ssf=Strings.objects.filter(name=fixed)
            if ssf.exists():
                u.name=ssf[0]

                try:
                    u.save()
                except IntegrityError:
                    #an integrity error on uniquenes is likely and probable if
                    #since this string was already in use it probably already applies to a username pair
                    
                    #As a final check lets make sure the fixed user is already on the same person
                    others=UserName.objects.filter(name=u.name)
                    failed=False
                    for uo in others:
                        if uo.belongs_to_id != u.belongs_to_id:
                            failed=True
                            print("Failted to fix username {} because of a person identity mismatch".format(fixed))
                            print("Person id {} != {}".format(u.belongs_to,uo.belongs_to))
                        if failed:
                            raise IntegrityError("Username identity mismatch")
            else:
                with transaction.atomic():
                    #no such string so create it and
                    u.name=Strings(name=fixed)
                    u.name.save()
                    u.save()
                
                # #try to clean up the bad shared strig might error if referenced elsewhere so that's fine
                # try:
                #     bad_ss.delete()
                # except:
                #     pass
    def handle(self, *args, **options):
        # self.cleanup_bad_prefix('http://')
        # self.cleanup_bad_prefix('https://')
        # UserName.objects.filter(name_id=None).delete()
        # for un in UserName.objects.all():
        #     with transaction.atomic():
        #         try:
        #             name=un.name
        #         except Strings.DoesNotExist:
        #             un.delete()
        for p in Person.objects.annotate(cnt=Count('usernames')).filter(cnt=1):
            uns=p.usernames.first().name.name
            si=Strings.objects.filter(name__iexact=uns)
            pl=Person.objects.filter(usernames__name__in=si)
            n=pl.count()
            min_id= min([x.id for x in pl])
            if n>1:
                if p.id != min_id:
                    p.delete()

        
        #uman.filter(name__name__istartswith='https://')



        



