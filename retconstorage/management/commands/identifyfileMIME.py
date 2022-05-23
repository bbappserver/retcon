from django.core.management.base import BaseCommand, CommandError
from retconstorage.models import NamedFile, ManagedFile,Filetype
from retcon import settings
from django.db import transaction
import os
import sys
import os.path
import stat
import hashlib
import progress.bar
import filetype

from multiprocessing import Queue, Process
from queue import Empty, Full


def identifyFile(prefix,work):
    realpath = os.path.join(prefix, work)
    kind = filetype.guess(realpath)
    MIME='application/octet-stream'
    if kind is not None:
        MIME=kind.mime
    if 'application/octet-stream' == MIME:
        from mimetypes import guess_type
        t=guess_type(realpath)
        if not(t is None):
            MIME=t.join("/")

    return MIME

def hash_worker(prefix, in_q: Queue, out_q: Queue):
    try:
        while True:
            work = in_q.get()
            if work is None:
                break
            else:
                try:
                    MIME=identifyFile(prefix,work)
                    out_q.put((work, MIME))
                except FileNotFoundError:
                    out_q.put(None)
    except KeyboardInterrupt:
        pass  # Just supress keyboard interrupt vomit if the parent is killed

# c=models.Filetype.objects.get(MIME='application/octet-stream')
# b=models.ManagedFile.objects.filter(filetype__MIME='application/octet-stream"')
# b.update(filetype=c)
# models.Filetype.objects.get(MIME='application/octet-stream"').delete()
def collect_result(t):
    # If there was a problem processing a file it will come down as null
    if t is None:
        return
    name, MIME = t
    with transaction.atomic():
        nf = NamedFile.objects.filter(name=name)[0]
        mf=nf.identity
        if mf is not None :
            ft,created= Filetype.objects.get_or_create(MIME=MIME)
            mf.filetype=ft
            if created:
                ft.save()
            mf.save()



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
    help = 'Identify files with MIME type'

    def add_arguments(self, parser):
        pass
        # parser.add_argument('root', nargs=1, type=str)

    def handle(self, *args, **options):
        try:
            prefix = settings.NAMED_FILE_PREFIX
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
            mfs = ManagedFile.objects.filter(filetype=None)
            i = 0
            processed = 0
            print('Load names')
            bar = SlowBar('Processing', max=mfs.count())
            for mf in mfs:
                try:
                    nf=NamedFile.objects.filter(identity=mf)[0]
                except:
                    bar.next()
                    continue
        #UNcomment for single proc veriosn (debug)
        #         MIME= identifyFile(prefix,nf.name)
        #         collect_result((nf.name,MIME))
        #         bar.next()
        #     bar.finish()
        # except KeyboardInterrupt:
        #     pass
        #BEGIN multiproc version
                #print("Dispatch{}".format(nf.name))
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
