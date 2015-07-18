import sys
import os

def read_file(dir, file_name):
    f = open(os.path.join(path, file_name))
    try:
        return f.read()
    finally:
        f.close()
        
def write_file(dir, file_name, data):
    f = open(os.path.join(dir, file_name), 'w+')
    try:
        f.write(data)
    finally:
        f.close()
        
path = sys.path[0]
projectname = raw_input("Enter your project name: ")
root_path = os.path.dirname(path)
if os.path.basename(root_path) == 'djfw':
    root_path = os.path.dirname(root_path)
    
djfw = False
project_root = os.path.join(root_path, projectname)
if not os.path.exists(project_root):
    djfw = True
    os.mkdir(project_root)
    
buildout_cfg = read_file(path, 'buildout.cfg.template')
write_file(root_path, 'buildout.cfg', buildout_cfg.replace('%s', projectname))
        
vhost_cfg = read_file(path, 'vhost.conf.template')
write_file(root_path, 'vhost.conf.template', vhost_cfg.replace('%PWN%', projectname))
               
install_py = read_file(path, 'install.py').replace('%PWN%', projectname)
if djfw:
    install_py = install_py.replace('import installer', 'import djfw.installer')
    install_py = install_py.replace('from installer', 'from djfw.installer')
write_file(root_path, 'install.py', install_py)
    
bootstrap = read_file(path, 'bootstrap.py')
write_file(root_path, 'bootstrap.py', bootstrap)

print "Done!"