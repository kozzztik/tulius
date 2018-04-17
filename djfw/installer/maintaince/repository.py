from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import get_default_timezone
from .operation import Operation
import datetime

class RepoPasswordRequired(Exception):
    pass

class SVNClient():
    logger = []
    
    def __init__(self, operation, reg_data):
        import pysvn
        self.no_pass = False
        self.client = pysvn.Client()
        self.path = operation.path
        self.operation = operation
        self.reg_data = reg_data
        self.client.callback_get_login = self._get_repo_login
        self.client.callback_ssl_server_trust_prompt = self._repo_ssl_server_trust_prompt
        self.client.callback_notify = self._notify
        
    def _notify(self, event_dict):
        self.log(unicode(event_dict))
    
    def log(self, text):
        for logger in self.logger:
            logger(text)
            
    def _get_repo_login(self, realm, username, may_save ):
        self.log('try svn password')
        if not self.reg_data:
            self.reg_data['realm'] = realm
            self.reg_data['username'] = username
            self.reg_data['data_provided'] = False
        if not self.reg_data['data_provided']:
            self.no_pass = True
            return False, username, '', False
            raise RepoPasswordRequired()
        username = self.reg_data['username']
        password = self.reg_data['password']
        if username and password:
            self.log("Password recieved")
        else:
            self.log("Password is empty!")
        self.log('Registration data recieved, sending...')
        return True, username, password, False
    
    def _repo_ssl_server_trust_prompt(self, trust_dict ):
        return True, 0, True

    def current_revision(self):
        info = self.client.info(self.path)
        self.revision = info.revision
        return info.revision.number

    def changelist_to_head(self):
        try:
            revisions = self.client.log(self.path, revision_end=self.revision)
        except Exception as e:
            self.log(e)
            self.log('failed')
            if not self.no_pass:
                self.log('error2')
                raise
            else:
                self.log('no pass')
                raise RepoPasswordRequired()
        revisions = [revision for revision in revisions if
                     revision.revision.number != self.revision.number]
        dict_revisions = []
        Revision = self.operation.models.Revision
        for log in revisions:
            number = log.revision.number
            try:
                obj = Revision.objects.get(number=number)
            except Revision.DoesNotExist:
                obj = Revision(number=number)
            obj.author = log.author
            obj.comment = log.message
            date = datetime.datetime.fromtimestamp(log.date, get_default_timezone())
            obj.time = date
            obj.save()
            dict_revisions += [[number, obj,  log]]
        self.revisions = dict_revisions
        choices = [(revision[0], unicode(revision[1])) for revision in self.revisions]
        return choices
    
    def revision_from_choice(self, choice):
        for revision in self.revisions:
            if str(choice) == str(revision[0]):
                return revision[1], revision[2]

    def update(self, log):
        changeset = []
        revision = log.revision
        for rev in self.revisions:
            if int(rev[0]) <= int(revision.number):
                changeset += [rev[1]]
        self.client.update(self.path, revision=revision)
        return changeset
    
class RepoUpdate(Operation):
    name = 'repo_update'
    caption = _(u'Update repository')
    
    STATUS_GET_CURRENT_REVISION = 0
    STATUS_GET_CHANGE_LIST = 1
    STATUS_CHOOSE_REVISION = 2
    STATUS_UPDATE = 3
    
    FORM_LOGIN = 0
    FORM_CHOOSE_REVISION = 1
    
    def __call__(self):
        params = self.params
        status = params['status'] if 'status' in params else self.STATUS_GET_CURRENT_REVISION
        reg_data = params['reg_data'] if 'reg_data' in params else {}
        client = SVNClient(self, reg_data)
        client.logger = [self.log]
        delete_pass = False
        try:
            try:
                try:
                    revision = client.current_revision()
                    if status == self.STATUS_GET_CURRENT_REVISION:
                        params['current_revision'] = revision
                        status = self.STATUS_GET_CHANGE_LIST
                        self.worker.update_status(_("Investigating remote repository"))
                    if status == self.STATUS_GET_CHANGE_LIST:
                        choices = client.changelist_to_head()
                        params['revisions'] = choices
                        if not choices:
                            self.log('No revisions to update, skip repo update.')
                            delete_pass = True
                            return
                        status = self.STATUS_CHOOSE_REVISION
                    if status == self.STATUS_CHOOSE_REVISION:
                        if not 'to_revision' in params:
                            self.worker.update_status(_("Waiting for revision choosing"))
                            params['form'] = self.FORM_CHOOSE_REVISION
                            return True
                        else:
                            choice = params['to_revision']
                            client.changelist_to_head()
                            rev_obj, rev_data = client.revision_from_choice(choice)
                            self.worker.update_status(_("Updating to revision %s") % rev_obj)
                            changeset = client.update(rev_data)
                            delete_pass = True
                            self.worker.log_obj.revision = rev_obj.number
                            self.worker.log_obj.save()
                            for revision in changeset:
                                self.models.MaintainceChangelist(mainteince=self.log_obj, revision=revision).save()
                            self.worker.update_status(_("Repository updated. Current revision %s" % rev_obj))
                except RepoPasswordRequired:
                    self.log('catched login error')
                    params['form'] = self.FORM_LOGIN
                    return True
            except:
                delete_pass = True
                raise
        finally:
            params['status'] = status
            params['reg_data'] = client.reg_data
            if delete_pass:
                params['reg_data']['password'] = '****'
            self.worker.params[self.name] = params
            
    def get_form(self, request):
        if not 'form' in self.params:
            return
        params = self.params
        form = params['form']
        from .forms import RepoPasswordForm, RepoRevisionForm
        if form == self.FORM_LOGIN:
            reg_data = params['reg_data']
            realm = reg_data['realm']
            username = reg_data['username']
            return RepoPasswordForm(request.POST or None, initial={'realm': realm, 'username': username})
        elif form == self.FORM_CHOOSE_REVISION:
            choices = params['revisions']
            return RepoRevisionForm(choices, request.POST or None)
    
    def form_valid(self, form):
        params = self.params
        form_type = params['form']
        if form_type == self.FORM_LOGIN:
            reg_data = params['reg_data']
            reg_data['username'] = form.cleaned_data['username']
            reg_data['password'] = form.cleaned_data['password']
            reg_data['data_provided'] = True
            params['reg_data'] = reg_data
        elif form_type == self.FORM_CHOOSE_REVISION:
            params['to_revision'] = form.cleaned_data['revision']
        self.params = params
