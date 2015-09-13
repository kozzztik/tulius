# -*- coding: utf-8 -*-
from __future__ import print_function

from django.core.management.base import BaseCommand

class Command(BaseCommand):
        
    def handle(self, category_name, **options):
        try:
            from djfw.installer.maintaince.backup import do_backup
        except:
            from installer.maintaince.backup import do_backup
        do_backup(category_name)
            