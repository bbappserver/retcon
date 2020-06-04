from django.core.management.base import BaseCommand, CommandError
from retconstorage.models import NamedFile, ManagedFile
from django.conf.locale import LANG_INFO
from django.db import transaction
import os
import sys
import os.path
import stat
import hashlib
import progress.bar

from multiprocessing import Queue, Process
from queue import Empty, Full


def hashfile(path):
    BUF_SIZE = 536870912  # lets read stuff in 0.5GiB chunks!

    md5 = hashlib.md5()
    sha256 = hashlib.sha256()

    with open(path, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)
            sha256.update(data)
            del data  # explicitly dispose of buffer
    return (md5.digest(), sha256.digest())


def hash_worker(prefix, in_q: Queue, out_q: Queue):
    try:
        while True:
            work = in_q.get()
            if work is None:
                break
            else:
                try:
                    realpath = os.path.join(prefix, work)
                    md5, sha256 = hashfile(realpath)

                    out_q.put((work, md5, sha256))
                except FileNotFoundError:
                    out_q.put(None)
    except KeyboardInterrupt:
        pass  # Just supress keyboard interrupt vomit if the parent is killed


def collect_result(t):
    # If there was a problem processing a file it will come down as null
    if t is None:
        return
    name, md5, sha256 = t
    with transaction.atomic():
        nf = NamedFile.objects.filter(name=name)[0]

        mf = None
        mfs = ManagedFile.objects.filter(sha256=sha256)
        if mfs.count() < 1:
            mf = ManagedFile(sha256=sha256, md5=md5)
            mf.save()
        else:
            mf = mfs[0]

        nf.identity = mf
        nf.save()


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
    help = 'Imports language codes and names from django.conf.locale.LANG_INFO'

    def add_arguments(self, parser):
        pass
        # parser.add_argument('root', nargs=1, type=str)

    def handle(self, *args, **options):

        try:
            prefix = "/Volumes/"
            out_q = Queue()
            in_q = Queue()
            proc = []
            DISPATCH_SIZE = 2*os.cpu_count()
            PROBE_INTERVAL = 4

            print('Spawn workers')
            for i in range(DISPATCH_SIZE):
                p = Process(target=hash_worker, args=(
                    prefix, in_q, out_q), daemon=True)
                p.start()
                proc.append(p)
            print('Fetch names')
            nfs = NamedFile.objects.filter(identity=None)
            i = 0
            processed = 0
            print('Load names')
            bar = SlowBar('Processing', max=nfs.count())
            for nf in nfs:

                failed = True
                while failed:
                    try:
                        # Dispatch
                        in_q.put(nf.name, False)
                        i += 1
                        failed = False
                        break
                    except Full:
                        failed = True
                        # Prevents deadlock from circular wait
                        # There is hard limit to cross process queues even if you don't set one
                        # This remove elements so workers can process more so dispatch isn't full
                        for i in range(100):
                            res = out_q.get(True)
                            collect_result(res)
                            processed += 1
                            bar.next()

                # interleave nonblocking collect, ensure that there are plenty of preloaded work units
                # lets us not waste cycles while waiting for the work queue to reach capcity
                if i % PROBE_INTERVAL == 0 and i > DISPATCH_SIZE * 4:
                    #print("Collect "+str(i))
                    try:
                        for i in range(3):
                            res = out_q.get(timeout=1)
                            collect_result(res)
                            processed += 1
                            bar.next()
                    except Empty:
                        pass
            print('Done load')
            # Signal termination workers
            for p in proc:
                in_q.put(None)

            # collect outstanding
            while bar.remaining >0:
                res = out_q.get()
                collect_result(res)
                processed += 1
                bar.next()
            bar.finish()
        except KeyboardInterrupt:
            print("\nWaiting for workers to exit...")
            sys.exit()
