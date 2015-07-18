import logging
import subprocess
import os

class Operation():
    name = ''
    caption = ''
    default_run = True
    logger = logging.getLogger('installer')
    
    def __init__(self, worker):
        self.worker = worker
        self.models = worker.models
        self.path = self.worker.path
        self.log_obj = worker.log_obj
        
    def __call__(self):
        pass

    def form_valid(self, form):
        pass
    
    def get_form(self, request):
        if self.worker.log_obj.waiting_user:
            raise NotImplementedError()
    
    def log(self, text, is_err=False):
        self.worker.log(text, is_err)
        
    #@property
    def get_params(self):
        return self.worker.params[self.name] if self.name in self.worker.params else {}
    
    #@params.setter
    def set_params(self, value):
        self.log('setting params')
        self.worker.params[self.name] = value
        self.log(self.name)
        self.log(value)
        self.log(self.worker.params)
        
    params = property(get_params, set_params)
    
    def read_file(self, file_name, path=''):
        path = os.path.join(self.path, path) if path else self.path
        f = open(os.path.join(path, file_name))
        try:
            return f.read()
        finally:
            f.close()
            
    def write_file(self, file_name, data, path=''):
        path = os.path.join(self.path, path) if path else self.path
        f = open(os.path.join(path, file_name), 'w+')
        try:
            f.write(data)
        finally:
            f.close()
    
    def subprocess(self, command):
        import platform
        is_windows = platform.system() == 'Windows'
        try:
            proc = subprocess.Popen(command, shell=True, cwd=self.path, stdout=subprocess.PIPE,  stderr=subprocess.PIPE)
            stdout_buf = []
            stderr_buf = []
            (stdout, stderr) = proc.communicate()
            if stdout is not None:
                stdout_buf.append(stdout.decode('cp866' if is_windows else 'utf-8'))
            stdout = "\n".join(stdout_buf)
            if stderr is not None:
                stderr_buf.append(stderr.decode('cp866' if is_windows else 'utf-8'))
            stderr = "\n".join(stderr_buf)
            message = None
            if proc.returncode != 0 and stderr is not None and stderr != '':
                message = "Command failed: '%s'" % (command)
                message += "\n errcode: %s:\n%s" % (proc.returncode, stderr)
                self.log(message, True)
            if stdout is not None:
                stdout = stdout.rstrip()
            self.log(stdout)
        except OSError as ose:
            message = "Command failed with OSError. '%s':\n%s" % (command, ose)
            self.log(message, True)
            raise