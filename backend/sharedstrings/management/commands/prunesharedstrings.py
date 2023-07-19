from django.core.management.base import BaseCommand, CommandError
from sharedstrings.models import Language
from django.conf.locale import LANG_INFO


class Command(BaseCommand):
    help = 'Imports language codes and names from django.conf.locale.LANG_INFO'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        cnt = 0
        for lang in LANG_INFO:
            #we only care about the 2 letter iso codes
            #self.stdout.write(lang + ' ' + LANG_INFO[lang]['name'] + ' ' + LANG_INFO[lang]['name_local'])
            try:
                l = Language(isocode=lang,
                                name=LANG_INFO[lang]['name'],
                                name_local=LANG_INFO[lang]['name_local'])
                l.save()
                cnt += 1
            except Exception as e:
                self.stdout.write('Error adding language %s' % lang)
        self.stdout.write('Added %d languages to dcollect' % cnt)