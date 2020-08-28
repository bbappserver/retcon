from django.core.management.base import BaseCommand, CommandError
from retconstorage.models import NamedFile, ManagedFile
from django.conf.locale import LANG_INFO
from django.db import transaction

import Counter
import os
import sys
import os.path
import stat
import hashlib
import progress.bar

from multiprocessing import Queue, Process
from queue import Empty, Full


class SlowBar(progress.bar.Bar):
    suffix = '%(percent)d%% - %(eta_str)s - %(remaining)d'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._previous_eta = None

    @property
    def remaining_hours(self):
        return self.eta // 3600

    @property
    def remaining_minutes(self):
        return (self.eta - (self.remaining_hours*3600))//60

    @property
    def long_avg(self):
        return self.elapsed/self.index

    @property
    def eta(self):
        new_eta = self.long_avg*self.remaining
        if self._previous_eta:
            mix = (self._previous_eta+new_eta)/2

            if mix > .5*self._previous_eta and mix < self._previous_eta:
                # initial big jump case but don't underestimate
                self._previous_eta = mix
            elif new_eta - self._previous_eta > 1800:
                # new information has significantly increased(30m) our estimate
                self._previous_eta = mix
            elif self.elapsed > 6*60 and mix < self._previous_eta:
                # general case tick down,since we don't expect huge deviation after this many samples
                self._previous_eta = mix
            elif self.elapsed > 3*60:
                # early smaller tickdown
                error = self._previous_eta - mix
                if error > 0 and error < 90:
                    self._previous_eta = mix
        else:
            # initialize previous
            self._previous_eta = new_eta
        return 1.25*self._previous_eta

    @property
    def eta_str(self):
        if self.elapsed < 60:
            return 'calculating...'
        else:
            return '%(remaining_hours)d:%(remaining_minutes)02.0f' % self

def conform(target_file,dup_file):

        target=target_file.abspath
        newlink=dup_file.abspath

        if os.path.exists(newlink):
            try:
                os.rename(newlink,newlink+".old") #move current file out of place
                os.link(target,newlink) #recreate current file as link to target
                os.unlink(newlink+".old")
            except FileExistsError:
                # recover unremoved old
                if filecmp.cmp(target, newlink+".old", shallow=False):# check matching
                    os.unlink(newlink+".old")
                else:
                    print("WARNING:"+"FAILED to conform "+newlink+"because "+newlink+".old already exists and contents did not match")
                    return False
            except Exception as e:
                try:
                    #put old file back where it was
                    os.rename(newlink+".old",newlink)
                    print("WARNING:Something went wrong trying to manipulate "+newlink+" but we recovered and it was skipped")
                    print(e)
                    return False
                except Exception as e:
                    print("ERROR:A CRITICAL error occured trying to manipulate "+newlink)
                    print("ERROR:You should check it manually, now exiting")
                    print(e)
                    exit(-1)
        else:
            if os.path.exists(newlink+".old"):
                # recover partial rename
                if filecmp.cmp(target, newlink, shallow=False):# check matching
                    os.link(target,newlink) #recreate current file as link to target
                    os.unlink(newlink+".old")
                else:
                    print("ERROR: Found partial rename of {}->{}, and attempted recovery but contents did not match, skipping".format(newlink,target))
                    return False
            else:
                print("ERROR: Missing:"+newlink)
                return False
        
        #Update file record in database
        dup_file.inode=target_file.inode
        dup_file.save()

    def conform_items(files):
        inodes = None
        inodes = [ x.inode for x in files]
        target_inode, count = Counter(inodes).most_common(1)
        # get first item with this inode and use it as target
        target_file=None
        for f in files:
            if f.inode == target_inode:
                target_file=f
                break

        for f in files:
            if f.inode is target_inode: 
                continue
            else:
                conform(target_file,f)

class Command(BaseCommand):
    help = 'Imports language codes and names from django.conf.locale.LANG_INFO'

    def add_arguments(self, parser):
        pass
        # parser.add_argument('root', nargs=1, type=str)

    


    def handle(self, *args, **options):
        raise NotImplementedError("This isn't ready for use.")

        prefix = '/Volumes/'
        filter_root = ""
        '''
        select* from retconstorage_namedfile where identity_id in
        (select identity_id from  retconstorage_namedfile group by identity_id having count(*) > 1)
        AND name like "filter/root/%"
        '''

        inner = NamedFile.objects.group_by('identity_id').filter(
            identity_id__count__gt=1,identity.size__gt=0).columns('identity_id')
        outer = NamedFile.objects.filter(identity_id__in=list(
            inner)).filter(name__startswith=filter_root)

        identity_id = outer[0]
        l=[]
        #Collect spans with like identities
        for r in outer:
            if identity_id == r.identity_id:
                l.append(r)
            else:
                #catch prev span
                conform_items(l)
                #prepare first item of next span
                l=[r]
                identity_id=r.identity_id
        #catch the last span
        conform_items(l)


