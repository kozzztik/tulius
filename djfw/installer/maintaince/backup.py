import importlib
import logging
import os
import platform
import subprocess
import tarfile

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger('installer')


def run_subprocess(command, message_cmd=''):
    is_windows = platform.system() == 'Windows'
    try:
        proc = subprocess.Popen(
            command, shell=True, cwd=settings.BASE_DIR, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stdout_buf = []
        stderr_buf = []
        (stdout, stderr) = proc.communicate()
        if stdout is not None:
            stdout_buf.append(
                stdout.decode('cp866' if is_windows else 'utf-8'))
        stdout = "\n".join(stdout_buf)
        if stderr is not None:
            stderr_buf.append(
                stderr.decode('cp866' if is_windows else 'utf-8'))
        stderr = "\n".join(stderr_buf)
        if stdout is not None:
            stdout = stdout.rstrip()
        if proc.returncode != 0:
            message = "Command failed: %s\n errcode: %s\n" % (
                message_cmd or command, proc.returncode)
            message += stderr or stdout or ''
            logger.error(message)
        else:
            logger.info(stdout)
        return proc.returncode
    except OSError as ose:
        message = "Command failed with OSError. '%s':\n%s" % (
            message_cmd or command, ose)
        logger.error(message)
        raise


def backupmysql(category):
    database = settings.DATABASES['default']
    if database['ENGINE'] != 'django.db.backends.mysql':
        return []
    logger.info('Backup mysql...')
    print('Backup mysql...')
    filename = os.path.join(settings.BASE_DIR, 'mysql.sql')

    if os.path.exists(filename):
        os.remove(filename)
    run_subprocess(
        'mysqldump -u%s -p%s -h%s %s > %s' % (
            database['USER'], database['PASSWORD'], database['HOST'],
            database['NAME'], filename), 'Backup mysql')
    logger.info('Mysql backup finished.')
    print('Mysql backup finished.')
    return [filename]


def log(s):
    logger.info(s)
    print(s)


def add__to_backup(backup_file, file_path):
    log("Backuping " + file_path)
    arch_name = file_path.replace(settings.BASE_DIR, '')
    try:
        file_path = str(file_path)
        arch_name = str(arch_name)
    except:
        log("Failed unicode path " + file_path)
        raise
    try:
        backup_file.add(file_path, arch_name)
    except:
        log("Failed to add " + file_path + " as " + arch_name)
        raise


def do_backup(category_name):
    log("Starting backup...")
    try:
        from django.core.management import call_command
        call_command('clearance')
        from djfw.installer.models import Backup, BackupCategory
        categories = BackupCategory.objects.filter(name=category_name)
        if categories:
            category = categories[0]
        else:
            category = BackupCategory(
                name=category_name, verbose_name=category_name,
                enabled=True, saved_backups=2)
            category.save()
        if not category.enabled:
            log("Category disabled.")
            return
        backup = Backup(category=category)
        backups_dir = backup.backups_dir()
        media_root = settings.MEDIA_ROOT
        if backups_dir.count(media_root):
            raise ImproperlyConfigured(
                'Backup directory cant be in MEDIA directory.')
        if not os.path.exists(backups_dir):
            os.makedirs(backups_dir)
        backup.save()
        path = backup.path()
        if os.path.exists(path):
            os.remove(path)
        try:
            backupfile = tarfile.open(path, 'w:gz', encoding='utf-8')
            import sys
            log(
                "Filesystem %s , system %s" % (
                    sys.getfilesystemencoding(), sys.getdefaultencoding()))
        except:
            log("Failed to create tarfile.")
            raise
        installers = []
        for app_name in settings.INSTALLED_APPS:
            try:
                try:
                    installers += [
                        (
                            app_name,
                            importlib.import_module('.installer', app_name))]
                except ImportError as exc:
                    msg = exc.args[0]
                    if not msg.startswith(
                            'No module named') or 'installer' not in msg:
                        raise
            except:
                log("Failed to import application " + app_name)
                raise
        for installer in installers:
            proc = getattr(installer[1], 'backup_list', None)
            if proc:
                log("Backup %s" % installer[0])
                proc_val = proc(category)
                if isinstance(proc_val, list):
                    files_list = proc_val
                else:
                    files_list = [proc_val]
                for file_obj in files_list:
                    add__to_backup(backupfile, file_obj)
        files_list = getattr(settings, 'INSTALLER_BACKUP_FILES', None)
        if not files_list:
            files_list = [settings.MEDIA_ROOT, backupmysql]
            for file_obj in files_list:
                if callable(file_obj):
                    sublist = file_obj(category)
                    if isinstance(sublist, list):
                        for sub_obj in sublist:
                            add__to_backup(backupfile, sub_obj)
                    else:
                        add__to_backup(backupfile, sublist)
                else:
                    add__to_backup(backupfile, file_obj)
        backupfile.close()
        backup.size = os.path.getsize(path)
        backup.save()
        log("Backup finished ID=%s, size=%s" % (backup.id, backup.size))
        category.clear_backups()
        log("Backups cleared. Finished.")
        return backup
    except Exception as e:
        logger.error(e)
        raise e
