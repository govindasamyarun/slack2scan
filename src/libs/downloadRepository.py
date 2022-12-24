from email import message
import os, re, glob
from subprocess import Popen, PIPE
from random import randint, randrange
from config import S2SConfig

class DownloadRepository():
    def __init__(self, url, branch, uuid):
        self.downloadRepo = True
        self.downloadRepoComplete = False
        self.git_url = url
        self.branch = branch
        self.repo_download_directory_path = S2SConfig.repo_download_directory_path
        self.dirContent = []
        # The temp directory creation is to handle the repositories with the same name 
        self.temp_dir = uuid

    def github(self):
        print('Execute github lib')
        os.chdir(self.repo_download_directory_path)
        while self.downloadRepo:
            git_clone = Popen(['git', 'clone', '--single-branch', '--branch', self.branch, self.git_url, self.temp_dir], stdout=PIPE, stderr=PIPE)
            git_clone_stdout, git_clone_stderr = git_clone.communicate()
            # Temp directory gets created if the path exists -> set the downloadRepoComplete to true to move on 
            # If not, failed to download the repository -> set the downloadRepoComplete to false
            # queueCheck keeps track of the failed jobs 
            if os.path.exists(self.repo_download_directory_path+self.temp_dir):
                self.downloadRepo = False
                self.downloadRepoComplete = True
                self.dirContent = glob.glob(self.repo_download_directory_path+self.temp_dir+'/*')
                message = 'Success'
                #print("DEBUG - scanner - repository: {}, branch: {}, output: {}, console_output: {}, downloadRepo: {}, scanRepo: {}, dirFileCount: {}".format(repository, branch, str(git_clone_stdout), str(git_clone_stderr), downloadRepo, scanRepo, len(dirContent)))
            elif 'Could not find remote branch' in git_clone_stderr.decode('utf-8'):
                print("INFO - github - repository: {}, branch: {}, output: {}, console_output: {}, message: Repo or branch not found".format(self.git_url, self.branch, str(git_clone_stdout), str(git_clone_stderr)))
                self.downloadRepo = False
                self.downloadRepoComplete = False
                self.dirContent = []
                message = git_clone_stderr.decode('utf-8')
            else:
                self.downloadRepo = True
                self.downloadRepoComplete = False
                self.dirContent = []
                message = 'NA'

        return {'downloadRepoComplete': self.downloadRepoComplete, 'no_of_directories': len(self.dirContent), 'repo_dir': self.temp_dir, 'message': message}