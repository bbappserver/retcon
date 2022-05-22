from django.core.management.base import BaseCommand, CommandError
from retconstorage.models import ManagedFile
from django.db import transaction
from django.db.models import Q
from retcon import settings
import os
import sys
import os.path
import stat
import progress.bar


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
                #new information has significantly increased(30m) our estimate
                self._previous_eta = mix
            elif self.elapsed >6*60 and mix < self._previous_eta:
                #general case tick down,since we don't expect huge deviation after this many samples
                self._previous_eta = mix
            elif self.elapsed > 3*60:
                #early smaller tickdown
                error = self._previous_eta - mix
                if error > 0 and error < 90:
                    self._previous_eta = mix
        else:
            #initialize previous
            self._previous_eta = new_eta
        return 1.25*self._previous_eta

    @property
    def eta_str(self):
        if self.elapsed < 60:
            return 'calculating...'
        else:
            return '%(remaining_hours)d:%(remaining_minutes)02.0f' % self


class Command(BaseCommand):
    help = 'Remove hashes which do not represent a tracked file or a file on disk (likely created by a programming error)'

    def add_arguments(self, parser):
        # parser.add_argument('root', nargs=1, type=str)
        parser.add_argument('prefix', nargs='?', type=str,default=settings.NAMED_FILE_PREFIX)

    def handle(self, *args, **options):

        prefix = options['prefix'][0]
        skip_hidden_dir = True

        l=ManagedFile.objects.all()
        bar = SlowBar(max=l.count())
        for file in l:
            bar.next()
            try:
                if not file.isTracked and file.names.count()<1:
                    file.delete()
            except:
                print("Skipped file id={}, names=".format(file.id, list(file.names.all())))
        bar.finish()
