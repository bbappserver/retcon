from django.core.management.base import BaseCommand, CommandError
from retconstorage.models import NamedFile
from django.db import transaction
import os,sys
import os.path
import stat
import progress.spinner

class Command(BaseCommand):
    help = 'Scan files at the specified path and add them as path relative to prefix'

    def add_arguments(self, parser):
        parser.add_argument('root', nargs=1, type=str)
        parser.add_argument('prefix', nargs=1, type=str)

    def handle(self, *args, **options):

        rootpath = options['root'][0]
        prefix = options['prefix'][0]
        skip_hidden_dir=True
        spin=progress.spinner.Spinner()
        for root, dirs, files in os.walk(rootpath, followlinks=False):
            # skip extended attibuted directories
            if "@eaDir" in root:
                continue
            
            #skip hidden directories "path/to/normaldir/.dirname/more/dirs"
            if skip_hidden_dir and "/." in root:
                continue

            aroot = os.path.abspath(root)
            eroot = aroot.replace(prefix, "")
            with transaction.atomic():
                for file in files:
                    spin.next()
                    if file[0] == '.':  # skip hidden
                        continue

                    epath = os.path.join(eroot, file)

                    f = NamedFile.objects.filter(name=epath)
                    # Intentionally using filter since get raises exception
                    # and shouldn't do exceptions in atomic
                    if(not f.exists()):
                        path = os.path.join(root, file)
                        ino = os.lstat(path)[stat.ST_INO]
                        nf = NamedFile(name=epath, inode=ino)
                        nf.save()
        spin.finish()
