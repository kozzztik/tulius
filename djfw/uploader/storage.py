from django.core.files.storage import FileSystemStorage
from django.core.files.move import file_move_safe
from django.core.files import locks
from django.conf import settings
import os
import errno

class SimpleFileStorage(FileSystemStorage):
    def save(self, name, content):
        full_path = self.path(name)
        # if os.makedirs fails with EEXIST, the directory was created
        # concurrently, and we can continue normally. Refs #16082.
        directory = os.path.dirname(full_path)
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
        if not os.path.isdir(directory):
            raise IOError("%s exists and is not a directory." % directory)
        # This file has a file path that we can move.
        if hasattr(content, 'temporary_file_path'):
            file_move_safe(content.temporary_file_path(), full_path)
            content.close()
        # This is a normal uploadedfile that we can stream.
        else:
            flags = (os.O_WRONLY | os.O_CREAT | getattr(os, 'O_BINARY', 0))
            # The current umask value is masked out by os.open!
            fd = os.open(full_path, flags, 0o666)
            try:
                locks.lock(fd, locks.LOCK_EX)
                _file = None
                for chunk in content.chunks():
                    if _file is None:
                        mode = 'wb' if isinstance(chunk, bytes) else 'wt'
                        _file = os.fdopen(fd, mode)
                    _file.write(chunk)
            finally:
                locks.unlock(fd)
                if _file is not None:
                    _file.close()
                else:
                    os.close(fd)
                    
        if settings.FILE_UPLOAD_PERMISSIONS is not None:
            os.chmod(full_path, settings.FILE_UPLOAD_PERMISSIONS)
        return name