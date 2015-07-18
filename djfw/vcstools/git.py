# Software License Agreement (BSD License)
#
# Copyright (c) 2010, Willow Garage, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of Willow Garage, Inc. nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
"""
git vcs support.

refnames in git can be branchnames, hashes, partial hashes, tags. On
checkout, git will disambiguate by checking them in that order, taking
the first that applies

This class aims to provide git for linear centralized workflows.  This
means we assume that the only relevant remote is the one named
"origin", and we assume that commits once on origin remain on origin.

A challenge with git is that it has strong reasonable conventions, but
is very allowing for breaking them. E.g. it is possible to name
remotes and branches with names like "refs/heads/master", give
branches and tags the same name, or a valid SHA-ID as name, etc.
Similarly git allows plenty of ways to reference any object, in case
of ambiguities, git attempts to take the most reasonable
disambiguation, and in some cases warns.
"""


from __future__ import absolute_import, print_function, unicode_literals
import os
import gzip
import dateutil.parser  # For parsing date strings
from distutils.version import LooseVersion

from djfw.vcstools.vcs_base import VcsClientBase, VcsError
from djfw.vcstools.common import sanitized, normalized_rel_path, run_shell_command


class GitError(Exception):
    pass


def _git_diff_path_submodule_change(diff, rel_path_prefix):
    """
    Parses git diff result and changes the filename prefixes.
    """
    if diff is None:
        return None
    INIT = 0
    INDIFF = 1
    # small state machine makes sure we never touch anything inside
    # the actual diff
    state = INIT
    result = ""
    s_list = [line for line in diff.split(os.linesep)]
    subrel_path = rel_path_prefix
    for line in s_list:
        newline = line
        if line.startswith("Entering '"):
            state = INIT
            submodulepath = line.rstrip("'")[len("Entering '"):]
            subrel_path = os.path.join(rel_path_prefix, submodulepath)
            continue
        if line.startswith("diff --git "):
            state = INIT
        if state == INIT:
            if line.startswith("@@"):
                state = INDIFF
            else:
                if line.startswith("---") and not line.startswith("--- /dev/null"):
                    newline = "--- " + subrel_path + line[5:]
                if line.startswith("+++") and not line.startswith("+++ /dev/null"):
                    newline = "+++ " + subrel_path + line[5:]
                if line.startswith("diff --git"):
                    # first replacing b in case path starts with a/
                    newline = line.replace(" b/", " " + subrel_path + "/", 1)
                    newline = newline.replace(" a/", " " + subrel_path + "/", 1)
        if newline != '':
            result += newline + '\n'
    return result


def _get_git_version():
    """Looks up git version by calling git --version.

    :raises: VcsError if git is not installed or returns
    something unexpected"""
    try:
        cmd = 'git --version'
        value, version, _ = run_shell_command(cmd, shell=True)
        if value != 0:
            raise VcsError("git --version returned %s, maybe git is not installed" % (value))
        prefix = 'git version '
        if version is not None and version.startswith(prefix):
            version = version[len(prefix):].strip()
        else:
            raise VcsError("git --version returned invalid string: '%s'" % version)
    except VcsError as exc:
        raise VcsError("Could not determine whether git is installed: %s" % exc)
    return version


class GitClient(VcsClientBase):
    def __init__(self, path):
        """
        :raises: VcsError if git not detected
        """
        VcsClientBase.__init__(self, 'git', path)
        self.gitversion = _get_git_version()

    @staticmethod
    def get_environment_metadata():
        metadict = {}
        try:
            version = _get_git_version()
            resetkeep = LooseVersion(version) >= LooseVersion('1.7.1')
            submodules = LooseVersion(version) > LooseVersion('1.7')
            metadict["features"] = "'reset --keep': %s, submodules: %s" % (resetkeep, submodules)
        except VcsError:
            version = "No git installed"
        metadict["version"] = version
        return metadict

    def get_url(self):
        """
        :returns: GIT URL of the directory path (output of git info command), or None if it cannot be determined
        """
        if self.detect_presence():
            cmd = "git config --get remote.origin.url"
            _, output, _ = run_shell_command(cmd, shell=True, cwd=self._path)
            return output.rstrip()
        return None

    def detect_presence(self):
        # There is a proposed implementation of detect_presence which might be
        # more future proof, but would depend on parsing the output of git
        # See: https://github.com/vcstools/vcstools/pull/10
        return self.path_exists() and os.path.exists(os.path.join(self._path, '.git'))

    def checkout(self, url, version=None, verbose=False, shallow=False):
        """calls git clone and then, if version was given, update(version)"""
        if url is None or url.strip() == '':
            raise ValueError('Invalid empty url : "%s"' % url)

        #since we cannot know whether version names a branch, clone master initially
        cmd = 'git clone'
        if shallow:
            cmd += ' --depth 1'
            if LooseVersion(self.gitversion) >= LooseVersion('1.7.10'):
                cmd += ' --no-single-branch'
        if version is None:
            # quicker than using _do_update, but undesired when switching branches next
            cmd += ' --recursive'
        cmd += ' %s %s' % (url, self._path)
        value, _, msg = run_shell_command(cmd,
                                          shell=True,
                                          no_filter=True,
                                          show_stdout=verbose,
                                          verbose=verbose)
        if value != 0:
            if msg:
                self.logger.error('%s' % msg)
            return False

        try:
            # update to make sure we are on the right branch. Do not
            # check for "master" here, as default branch could be anything
            if version is not None:
                return self._do_update(version,
                                       verbose=verbose,
                                       fast_foward=True,
                                       update_submodules=True)
            else:
                return True
        except GitError:
            return False

    def update_submodules(self, verbose=False):

        # update and or init submodules too
        if LooseVersion(self.gitversion) > LooseVersion('1.7'):
            cmd = "git submodule update --init --recursive"
            value, _, _ = run_shell_command(cmd,
                                            shell=True,
                                            cwd=self._path,
                                            show_stdout=True,
                                            verbose=verbose)
            if value != 0:
                return False
        return True

    def update(self, version=None, verbose=False, force_fetch=False):
        """
        if version is None, attempts fast-forwarding current branch, if any.

        Else interprets version as a local branch, remote branch, tagname,
        hash, etc.

        If it is a branch, attempts to move to it unless
        already on it, and to fast-forward, unless not a tracking
        branch. Else go untracked on tag or whatever version is. Does
        not leave if current commit would become dangling.

        :return: True if already up-to-date with remote or after successful fast_foward
        """
        if not self.detect_presence():
            return False

        try:
            # fetch in any case to get updated tags even if we don't need them
            self._do_fetch()
            return self._do_update(refname=version, verbose=verbose)
        except GitError:
            return False

    def _do_update(self,
                   refname=None,
                   verbose=False,
                   fast_foward=True,
                   update_submodules=True):
        '''
        updates without fetching, thus any necessary fetching must be done before
        allows arguments to reduce unnecessary steps after checkout

        :param fast_foward: if false, does not perform fast-forward
        :param update_submodules: if false, does not attempt to update submodules
        '''
        # are we on any branch?
        current_branch = self.get_branch()
        branch_parent = None
        if current_branch:
            # local branch might be named differently from remote by user, we respect that
            same_branch = (refname == current_branch)
            if not same_branch:
                branch_parent = self.get_branch_parent(current_branch=current_branch)
                if not refname:
                    # ! changing refname to cause fast-forward
                    refname = branch_parent
                    same_branch = True
                else:
                    same_branch = (refname == branch_parent)
                if not branch_parent:
                    # avoid checking branch parent again later
                    fast_foward = False
        else:
            same_branch = False

        if not refname:
            # we are neither tracking, nor did we get any refname to update to
            return (not update_submodules) or self.update_submodules(verbose=verbose)

        if same_branch:
            if fast_foward:
                if not branch_parent and current_branch:
                    branch_parent = self.get_branch_parent(current_branch=current_branch)
                # already on correct branch, fast-forward if there is a parent
                if branch_parent:
                    if not self._do_fast_forward(branch_parent=branch_parent,
                                                 fetch=False,
                                                 verbose=verbose):
                        return False
        else:
            # refname can be a different branch or something else than a branch

            refname_is_local_branch = self.is_local_branch(refname)
            if refname_is_local_branch:
                # might also be remote branch, but we treat it as local
                refname_is_remote_branch = False
            else:
                refname_is_remote_branch = self.is_remote_branch(refname, fetch=False)
            refname_is_branch = refname_is_remote_branch or refname_is_local_branch

            current_version = None
            # shortcut if version is the same as requested
            if not refname_is_branch:
                current_version = self.get_version()
                if current_version == refname:
                    return (not update_submodules) or self.update_submodules(verbose=verbose)

            if current_branch is None:
                if not current_version:
                    current_version = self.get_version()
                # prevent commit from becoming dangling
                if self.is_commit_in_orphaned_subtree(current_version, fetch=False):
                    # commit becomes dangling unless we move to one of its descendants
                    if not self.rev_list_contains(refname, current_version, fetch=False):
                        # TODO: should raise error instead of printing message
                        print("vcstools refusing to move away from dangling commit, to protect your work.")
                        return False

            # git checkout makes all the decisions for us
            self._do_checkout(refname, verbose=verbose, fetch=False)

            if refname_is_local_branch:
                # if we just switched to a local tracking branch (not created one), we should also fast forward
                new_branch_parent = self.get_branch_parent(current_branch=refname)
                if new_branch_parent is not None:
                    if fast_foward:
                        if not self._do_fast_forward(branch_parent=new_branch_parent,
                                                     fetch=False,
                                                     verbose=verbose):
                            return False
        return (not update_submodules) or self.update_submodules(verbose=verbose)

    def get_version(self, spec=None):
        """
        :param spec: (optional) token to identify desired version. For
          git, this may be anything accepted by git log, e.g. a tagname,
          branchname, or sha-id.
        :param fetch: When spec is given, can be used to suppress git fetch call
        :returns: current SHA-ID of the repository. Or if spec is
          provided, the SHA-ID of a commit specified by some token if found, else None
        """
        if self.detect_presence():
            command = "git log -1"
            if spec is not None:
                command += " %s" % sanitized(spec)
            command += " --format='%H'"
            output = ''
            #we repeat the call once after fetching if necessary
            for _ in range(2):
                _, output, _ = run_shell_command(command,
                                                 shell=True,
                                                 cwd=self._path)
                if (output != '' or spec is None):
                    break
                # we try again after fetching if given spec had not been found
                try:
                    self._do_fetch()
                except GitError:
                    return None
            # On Windows the version can have single quotes around it
            output = output.strip("'")
            return output
        return None

    def get_diff(self, basepath=None):
        response = ''
        if basepath is None:
            basepath = self._path
        if self.path_exists():
            rel_path = normalized_rel_path(self._path, basepath)
            # git needs special treatment as it only works from inside
            # use HEAD to also show staged changes. Maybe should be option?
            # injection should be impossible using relpath, but to be sure, we check
            cmd = "git diff HEAD --src-prefix=%s/ --dst-prefix=%s/ ." % \
                  (sanitized(rel_path), sanitized(rel_path))
            _, response, _ = run_shell_command(cmd, shell=True, cwd=self._path)
            if LooseVersion(self.gitversion) > LooseVersion('1.7'):
                cmd = 'git submodule foreach --recursive git diff HEAD'
                _, output, _ = run_shell_command(cmd, shell=True, cwd=self._path)
                response += _git_diff_path_submodule_change(output, rel_path)
        return response

    def get_log(self, relpath=None, limit=None):
        response = []

        if relpath is None:
            relpath = ''

        if self.path_exists() and os.path.exists(os.path.join(self._path, relpath)):
            # Get the log
            limit_cmd = (("-n %d" % (int(limit))) if limit else "")

            GIT_COMMIT_FIELDS = ['id', 'author', 'email', 'date', 'message']
            GIT_LOG_FORMAT = '%x1f'.join(['%H', '%an', '%ae', '%ad', '%s']) + '%x1e'

            command = "git --work-tree=%s log --format=\"%s\" %s %s " % (self._path, GIT_LOG_FORMAT,
                                                                         limit_cmd, sanitized(relpath))
            return_code, response_str, stderr = run_shell_command(command, shell=True, cwd=self._path)

            if return_code == 0:
                # Parse response
                response = response_str.strip('\n\x1e').split("\x1e")
                response = [row.strip().split("\x1f") for row in response]
                response = [dict(zip(GIT_COMMIT_FIELDS, row)) for row in response]

                # Parse dates
                for entry in response:
                    entry['date'] = dateutil.parser.parse(entry['date'])

        return response

    def get_status(self, basepath=None, untracked=False):
        response = None
        if basepath is None:
            basepath = self._path
        if self.path_exists():
            rel_path = normalized_rel_path(self._path, basepath)
            # git command only works inside repo
            # self._path is safe against command injection, as long as we check path.exists
            command = "git status -s "
            if not untracked:
                command += " -uno"
            _, response, _ = run_shell_command(command,
                                               shell=True,
                                               cwd=self._path)
            response_processed = ""
            for line in response.split('\n'):
                if len(line.strip()) > 0:
                    # prepend relative path
                    response_processed += '%s%s/%s\n' % (line[0:3],
                                                         rel_path,
                                                         line[3:])
            if LooseVersion(self.gitversion) > LooseVersion('1.7'):
                command = "git submodule foreach --recursive git status -s"
                if not untracked:
                    command += " -uno"
                _, response2, _ = run_shell_command(command,
                                                    shell=True,
                                                    cwd=self._path)
                for line in response2.split('\n'):
                    if line.startswith("Entering"):
                        continue
                    if len(line.strip()) > 0:
                        # prepend relative path
                        response_processed += line[0:3] + rel_path + '/' + line[3:] + '\n'
            response = response_processed
        return response

    def is_remote_branch(self, branch_name, fetch=True):
        """
        checks list of remote branches for match. Set fetch to False if you just fetched already.

        :returns: True if git branch knows ref for remote "origin"
        :raises: GitError when git fetch fails
        """
        if self.path_exists():
            if fetch:
                self._do_fetch()
            _, output, _ = run_shell_command('git branch -r',
                                             shell=True,
                                             cwd=self._path)
            for l in output.splitlines():
                elem = l.split()[0]
                rem_name = elem[:elem.find('/')]
                br_name = elem[elem.find('/') + 1:]
                if rem_name == "origin" and br_name == branch_name:
                    return True
        return False

    def is_local_branch(self, branch_name):
        if self.path_exists():
            _, output, _ = run_shell_command('git branch',
                                             shell=True,
                                             cwd=self._path)
            for line in output.splitlines():
                elems = line.split()
                if len(elems) == 1:
                    if elems[0] == branch_name:
                        return True
                elif len(elems) == 2:
                    if elems[0] == '*' and elems[1] == branch_name:
                        return True
        return False

    def get_branch(self):
        if self.path_exists():
            _, output, _ = run_shell_command('git branch',
                                             shell=True,
                                             cwd=self._path)
            for line in output.splitlines():
                elems = line.split()
                if len(elems) == 2 and elems[0] == '*':
                    return elems[1]
        return None

    def get_branch_parent(self, fetch=False, current_branch=None):
        """
        return the name of the branch this branch tracks, if any

        :raises: GitError if fetch fails
        """
        if self.path_exists():
            # get name of configured merge ref.
            branchname = current_branch or self.get_branch()
            if branchname is None:
                return None
            cmd = 'git config --get %s' % sanitized('branch.%s.merge' % branchname)

            _, output, _ = run_shell_command(cmd,
                                             shell=True,
                                             cwd=self._path)
            if not output:
                return None
            lines = output.splitlines()
            if len(lines) > 1:
                print("vcstools unable to handle multiple merge references for branch %s:\n%s" % (branchname, output))
                return None
            # get name of configured remote
            cmd = 'git config --get "branch.%s.remote"' % branchname
            _, output2, _ = run_shell_command(cmd, shell=True, cwd=self._path)
            if output2 != "origin":
                print("vcstools only handles branches tracking remote 'origin'," +
                      " branch '%s' tracks remote '%s'" % (branchname, output2))
                return None
            output = lines[0]
            # output is either refname, or /refs/heads/refname, or
            # heads/refname we would like to return refname however,
            # user could also have named any branch
            # "/refs/heads/refname", for some unholy reason check all
            # known branches on remote for refname, then for the odd
            # cases, as git seems to do
            candidate = output
            if candidate.startswith('refs/'):
                candidate = candidate[len('refs/'):]
            if candidate.startswith('heads/'):
                candidate = candidate[len('heads/'):]
            elif candidate.startswith('tags/'):
                candidate = candidate[len('tags/'):]
            elif candidate.startswith('remotes/'):
                candidate = candidate[len('remotes/'):]
            if self.is_remote_branch(candidate, fetch=fetch):
                return candidate
            if output != candidate and self.is_remote_branch(output, fetch=False):
                return output
        return None

    def is_tag(self, tag_name, fetch=True):
        """
        checks list of tags for match.
        Set fetch to False if you just fetched already.

        :returns: True if tag_name among known tags
        :raises: GitError when call to git fetch fails
        """
        if fetch:
            self._do_fetch()
        if not tag_name:
            raise ValueError('is_tag requires tag_name, got: "%s"' % tag_name)
        if self.path_exists():
            cmd = 'git tag -l %s' % sanitized(tag_name)
            _, output, _ = run_shell_command(cmd, shell=True, cwd=self._path)
            lines = output.splitlines()
            if len(lines) == 1:
                return True
        return False

    def rev_list_contains(self, refname, version, fetch=True):
        """
        calls git rev-list with refname and returns True if version
        can be found in rev-list result

        :param refname: a git refname
        :param version: an SHA IDs (if partial, caller is responsible
          for mismatch)
        :returns: True if version is an ancestor commit from refname
        :raises: GitError when call to git fetch fails
        """
        # to avoid listing unnecessarily many rev-ids, we cut off all
        # those we are definitely not interested in
        # $ git rev-list foo bar ^baz ^bez
        # means "list all the commits which are reachable from foo or
        # bar, but not from baz or bez". We use --parents because
        # ^baz also excludes baz itself. We could also use git
        # show --format=%P to get all parents first and use that,
        # not sure what's more performant
        if fetch:
            self._do_fetch()
        if (refname is not None and refname != '' and
                version is not None and version != ''):

            cmd = 'git rev-list %s ^%s --parents' % (sanitized(refname), sanitized(version))
            _, output, _ = run_shell_command(cmd, shell=True, cwd=self._path)
            for line in output.splitlines():
                # can have 1, 2 or 3 elements (commit, parent1, parent2)
                for hashid in line.split(" "):
                    if hashid.startswith(version):
                        return True
        return False

    def is_commit_in_orphaned_subtree(self, version, mask_self=False, fetch=True):
        """
        checks git log --all (the list of all commits reached by
        references, meaning branches or tags) for version. If it shows
        up, that means git garbage collection will not remove the
        commit. Else it would eventually be deleted.

        :param version: SHA IDs (if partial, caller is responsible for mismatch)
        :param mask_self: whether to consider direct references to this commit
            (rather than only references on descendants) as well
        :param fetch: whether fetch should be done first for remote refs
        :returns: True if version is not recursively referenced by a branch or tag
        :raises: GitError if git fetch fails
        """
        if fetch:
            self._do_fetch()
        if version is not None and version != '':
            cmd = 'git show-ref -s'
            _, output, _ = run_shell_command(cmd, shell=True, cwd=self._path)
            refs = output.splitlines()
            # 2000 seems like a number the linux shell can cope with
            chunksize = 2000
            refchunks = [refs[x:x + chunksize] for x in range(0, len(refs), chunksize)]
            for refchunk in refchunks:
                # git log over all refs except HEAD
                cmd = 'git log ' + " ".join(refchunk)
                if mask_self:
                    # %P: parent hashes
                    cmd += " --pretty=format:%P"
                else:
                    # %H: commit hash
                    cmd += " --pretty=format:%H"
                _, output, _ = run_shell_command(cmd, shell=True, cwd=self._path)
                for line in output.splitlines():
                    if line.strip("'").startswith(version):
                        return False
            return True
        return False

    def export_repository(self, version, basepath):
        # Use the git archive function
        cmd = "git archive -o {0}.tar {1}".format(basepath, version)
        result, _, _ = run_shell_command(cmd, shell=True, cwd=self._path)
        if result:
            return False
        try:
            # Gzip the tar file
            with open(basepath + '.tar', 'rb') as tar_file:
                gzip_file = gzip.open(basepath + '.tar.gz', 'wb')
                try:
                    gzip_file.writelines(tar_file)
                finally:
                    gzip_file.close()
        finally:
            # Clean up
            os.remove(basepath + '.tar')
        return True

    def _do_fetch(self):
        """
        calls git fetch
        :raises: GitError when call fails
        """
        cmd = "git fetch"
        value1, _, _ = run_shell_command(cmd,
                                         cwd=self._path,
                                         shell=True,
                                         no_filter=True,
                                         show_stdout=True)
        ## git fetch --tags ONLY fetches new tags and commits used, no other commits!
        cmd = "git fetch --tags"
        value2, _, _ = run_shell_command(cmd,
                                         cwd=self._path,
                                         shell=True,
                                         no_filter=True,
                                         show_stdout=True)
        if value1 != 0 or value2 != 0:
            raise GitError('git fetch failed')

    def _do_fast_forward(self, fetch=True, branch_parent=None, verbose=False):
        """Execute git fetch if necessary, and if we can fast-foward,
        do so to the last fetched version using git rebase.

        :param branch_parent: name of branch we track
        :param fetch: whether fetch should be done first for remote refs
        :returns: True if up-to-date or after succesful fast-forward
        :raises: GitError when git fetch fails
        """
        assert branch_parent is not None
        current_version = self.get_version()
        parent_version = self.get_version("remotes/origin/%s" % branch_parent)
        if current_version == parent_version:
            return True
        # check if we are true ancestor of tracked branch
        if not self.rev_list_contains(parent_version,
                                      current_version,
                                      fetch=fetch):
            # if not rev_list_contains this version, we are on same
            # commit (checked before), have advanced, or have diverged.
            # Now check whether tracked branch is a true ancestor of us
            if self.rev_list_contains(current_version,
                                      parent_version,
                                      fetch=False):
                return True
            return False
        if verbose:
            print("Rebasing repository")
        # Rebase, do not pull, because somebody could have
        # commited in the meantime.
        if LooseVersion(self.gitversion) >= LooseVersion('1.7.1'):
            # --keep allows o rebase even with local changes, as long as
            # local changes are not in files that change between versions
            cmd = "git reset --keep remotes/origin/%s" % branch_parent
            value, _, _ = run_shell_command(cmd,
                                            shell=True,
                                            cwd=self._path,
                                            show_stdout=True,
                                            verbose=verbose)
            if value == 0:
                return True
        else:
            verboseflag = ''
            if verbose:
                verboseflag = '-v'
            # prior to version 1.7.1, git does not know --keep
            # Do not merge, rebase does nothing when there are local changes
            cmd = "git rebase %s remotes/origin/%s" % (verboseflag, branch_parent)
            value, _, _ = run_shell_command(cmd,
                                            shell=True,
                                            cwd=self._path,
                                            show_stdout=True,
                                            verbose=verbose)
            if value == 0:
                return True
        return False

    def _do_checkout(self, refname, fetch=True, verbose=False):
        """
        meaning git checkout, not vcstools checkout. This works
        for local branches, remote branches, tagnames, hashes, etc.
        git will create local branch of same name when no such local
        branch exists, and also setup tracking. Git decides with own
        rules whether local changes would cause conflicts, and refuses
        to checkout else.

        :raises GitError: when checkout fails
        """
        # since refname may relate to remote branch / tag we do not
        # know about yet, do fetch if not already done
        if fetch:
            self._do_fetch()
        cmd = "git checkout %s" % (refname)
        value, _, _ = run_shell_command(cmd,
                                        shell=True,
                                        cwd=self._path,
                                        show_stdout=verbose,
                                        verbose=verbose)
        if value != 0:
            raise GitError('Git Checkout failed')


#Backwards compatibility
GITClient = GitClient
