import shutil, re, json
from subprocess import Popen, PIPE
from config import S2SConfig

class Gitleaks():
    def __init__(self, branch, repo_dir):
        self.gitleaks_path = S2SConfig.gitleaks_path
        self.branch = branch
        self.repo_download_directory_path = S2SConfig.repo_download_directory_path
        self.repo_dir = repo_dir

    def scan(self):
        print('Execute scan lib')
        scanner = Popen([self.gitleaks_path, 'detect', '--source', self.repo_dir, '-v', '--log-opts='+self.branch], stdout=PIPE, stderr=PIPE)
        scanner_stdout, scanner_stderr = scanner.communicate()
        scanner_stdout = scanner_stdout.decode('UTF-8')
        scanner_stdout = scanner_stdout.replace('\n', '')
        scanner_stdout = scanner_stdout.replace('\t', '')
        scanner_parsed_data = re.findall(r'(.*?)\"\}', scanner_stdout)
        scanner_output = []
        # Removes the temp directory and its contents 
        shutil.rmtree(self.repo_download_directory_path+self.repo_dir, ignore_errors=True)
        if len(scanner_parsed_data) != 0:
            for j in range(len(scanner_parsed_data)):
                try:
                    scanner_output.append(json.loads(scanner_parsed_data[j] + '"}'))
                except:
                    continue

        # Execute process_scanner_output function 
        return {"length": len(scanner_parsed_data), "branch": self.branch, "values": scanner_output}