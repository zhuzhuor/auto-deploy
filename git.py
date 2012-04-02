#!/usr/bin/env python

import subprocess
import os

GIT_LOCAL_BASE = 'repos'
if not os.path.exists(GIT_LOCAL_BASE):
    os.mkdir(GIT_LOCAL_BASE)


def command_output(args):
    # learnt from http://goo.gl/CgTnQ
    output = subprocess.Popen(args,
            stdout=subprocess.PIPE).communicate()[0]
    return output


class GitRepo:
    def __init__(self, remote_url, local_folder):
        self.remote_url = remote_url
        self.local_path = GIT_LOCAL_BASE + '/' + local_folder
        if not os.path.exists(self.local_path):
            self.clone()
        else:
            self.pull()

    def clone(self):
        subprocess.call(['git', 'clone', self.remote_url, self.local_path])

    def pull(self):
        saved_cwd = os.getcwd()
        os.chdir(self.local_path)
        subprocess.call(['git', 'pull'])
        os.chdir(saved_cwd)

    def changed_files(self, hash1, hash2='HEAD'):
        """
        return dict/list of updated and deleted files seperately
        """
        set_deleted = set(command_output(['git',
            '--git-dir', self.local_path + '/.git',
            'diff', '--name-only', '--diff-filter=D',
            hash1, hash2]
        ).strip().split())

        set_changed = set(command_output(['git',
            '--git-dir', self.local_path + '/.git',
            'diff', '--name-only',
            hash1, hash2]
        ).strip().split())

        set_updated = set_changed - set_deleted
        dict_updated = dict()
        for f in set_updated:
            dict_updated[f] = self.local_path + '/' + f

        return dict_updated, set_deleted

    def head_hash(self):
        return command_output(['git',
            '--git-dir', self.local_path + '/.git',
            'rev-parse', 'HEAD']
        ).strip()

    def all_files(self):
        list_files = command_output(['git',
            '--git-dir', self.local_path + '/.git',
            'ls-tree', '-r', '--name-only', 'HEAD']
        ).strip().split()

        dict_files = dict()
        for f in list_files:
            dict_files[f] = self.local_path + '/' + f

        return dict_files


if __name__ == '__main__':
    from config import settings
    remote_url = settings[0]['repo_url']
    local_folder = settings[0]['repo_name']

    my_repo = GitRepo(remote_url, local_folder)
    print my_repo.changed_files('HEAD~2')

    print my_repo.head_hash()
    print my_repo.all_files()
