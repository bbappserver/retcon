from django.core.management.base import BaseCommand, CommandError
from retconstorage.models import NamedFile
from django.db import transaction
import os,sys
import os.path
import stat
import progress.spinner
from retconcreatives.models import Series,Episode,Company

class Command(BaseCommand):
    help = 'Scan files at the specified path and add them as path relative to prefix'

    def add_arguments(self, parser):
        pass
        # parser.add_argument('prefix', nargs=1, type=str)
        # parser.add_argument('root', nargs=1, type=str)

    def handle(self, *args, **options):
        sname = input("Series name: ")
        cname = input("Company name: ")

        candidates=Series.search(sname)
        should_create=False
        while len(candidates)!=1:
                sname = input("Series name: ")
                candidates=Series.search(sname)
                if len(candidates) >1:
                    print("Found:\n{}".format(candidates))
                elif len(candidates)==0:
                    yn=input("No such series create it (y/n)?")
                    if yn=='y':
                        should_create=True
                        break

        print("Using:\n{}".format(candidates))
        candidates=[]
        
        #Todo logic for setting publisher and producer
        # candidate_companies=list(Company.objects.filter(name__name__icontains=cname))
        # if len(candidate_companies)>1:
        #     candidate_companies=list(Company.objects.filter(name__name__icontains=cname))
        # elif len(candidate_companies)==0:
        #     input('No candidate companies')


        with transaction.atomic():
            candidate_companies=list(Company.objects.filter(name__name__icontains=cname))
            if len(candidate_companies)>1:
                print("multiple companies returned, not currently supported")
                exit(-1)

            if should_create:
                ser=Series(name=sname)
                ser.save()
                if len(candidate_companies)>0:
                    ser.published_by.add(candidate_companies)
            
            else:
                candidates=list(Series.search(sname))
                
                if len(candidates)==0:
                    print('Series disappears before db lock')
                    exit(-1)
                elif len(candidates)>1:
                    print('Multiple series candidates appeared')
                    exit(-1)
                ser=candidates[0]
            

            Episode.WEBSERIES

            ename = input("Episode pattern, use {} to replace number\n\t")
            N= int(input("Count?: "))
            ##HACK Just doing webseries since that's most entries
            for i in range(1,N+1):
                e=Episode(name=ename.format(i),part_of=ser,order_in_series=i,medium=Episode.WEBSERIES)
                e.save()
                print('Created\n{}'.format(e))
            
            print('Created\n{}'.format(ser))
            yn=input('Confirm?(y/n)')
            if yn != 'y':
                print('Operation aborted')
                transaction.set_rollback(True)
                return


