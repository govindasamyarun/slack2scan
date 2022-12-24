import os
import hmac
import hashlib
import requests
import json
import csv
import uuid
from datetime import datetime
from libs.downloadRepository import DownloadRepository
from libs.gitleaks import Gitleaks
from urllib.parse import parse_qs
from config import S2SConfig
from zoneinfo import ZoneInfo

class S2S():
    def __init__(self, req_data, req_timestamp, req_signature):
        self.raw_data = req_data
        self.parsed_data = parse_qs(self.raw_data)
        self.slack_request_timestamp = req_timestamp
        self.slack_signature = req_signature
        self.slack_signing_secret = os.environ['SLACK_SIGNING_SECRET']
        self.received_timestamp = datetime.now().strftime('%s')
        self.received_timestamp_tz = datetime.now(tz=ZoneInfo('Asia/Kolkata')).strftime('%s')
        self.uuid = uuid.uuid4().hex
        self.scanner_results_directory_path = S2SConfig.scanner_results_directory_path
        self.s2s_host_name = os.environ['S2S_HOST_NAME']
        self.s2s_reports_url = 'http://{}/s2s/download/'.format(
            self.s2s_host_name)

    def scan_engine(self):
        print('Execute scan_engine lib')
        # Verify requests from Slack
        verify = self.verify()
        if verify['status']:
            self.scan()
        else:
            return verify['message']

    def verify(self):
        print('Execute verify lib')
        sig_basestring = 'v0:' + self.slack_request_timestamp + ':' + self.raw_data
        signature = 'v0=' + hmac.new(self.slack_signing_secret.encode(
            'utf-8'), msg=sig_basestring.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
        scan_args = self.parsed_data['text'][0].split(' ')
        print('INFO - verify - received_time: {}, header_timestamp: {}, sig_basestring: {}, signature: {}, text: {}, response_url: {}'.format(
            self.received_timestamp, self.slack_request_timestamp, sig_basestring, signature, self.parsed_data['text'][0], self.parsed_data['response_url'][0]))
        if (int(self.received_timestamp) - int(self.slack_request_timestamp)) < (60 * 5) and self.slack_signature == signature and (len(scan_args) == 1 or len(scan_args) == 2):
            print('INFO - verify - Verification successful')
            return {'status': True, 'message': 'Verification successful'}
        else:
            print('INFO - verify - Not authorized')
            return {'status': False, 'message': 'Not authorized'}

    def scan(self):
        print('Execute scan lib')
        response_url = self.parsed_data['response_url'][0]
        scan_args = self.parsed_data['text'][0].split(' ')
        # scan_args[0] -> git url, scan_args[1] -> branch (optional, defaults to master)
        print('INFO - scan - scan_args: {}'.format(scan_args))
        if len(scan_args) == 2:
            git_url = scan_args[0]
            branch = scan_args[1]
        else:
            git_url = scan_args[0]
            branch = S2SConfig.default_branch
        print('INFO - scan - git_url: {}, branch: {}'.format(git_url, branch))
        download = DownloadRepository(git_url, branch, self.uuid).github()
        if download['downloadRepoComplete']:
            scanresults = Gitleaks(branch, download['repo_dir']).scan()
            print('INFO - scan - response_url: {}, scancount: {}'.format(response_url,
                  scanresults['length']))
            self.write_to_csv(
                scanresults['length'], scanresults['values'], git_url, branch)
            _date = datetime.fromtimestamp(
                int(self.received_timestamp_tz)).strftime("%d-%b-%Y %H:%M:%S")
            _repository = git_url
            _secretcount = scanresults['length']
            _downloadLink = self.s2s_reports_url+self.uuid
            if _secretcount > 0:
                slack_message_text = '*Date*: {}\n*Repository*: {}\n*Branch*: {}\n*No of secrets*: {} :alert:'.format(
                _date, _repository, branch, _secretcount)
                slack_message = {
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": slack_message_text
                            }
                        },
                        {
                            "type": "actions",
                            "elements": [
                                {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Download",
                                        "emoji": True
                                    },
                                    "style": "primary",
                                    "url": _downloadLink
                                }
                            ]
                        }
                    ]
                }
            else:
                slack_message_text = '*Date*: {}\n*Repository*: {}\n*Branch*: {}\n*No of secrets*: {} :white_check_mark:'.format(
                _date, _repository, branch, _secretcount)
                slack_message = {
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": slack_message_text
                        }
                    }
                ]
            }
        else:
            print('INFO - scan - Failed to download repositorey - {}'.format(download["message"]))
            _date = datetime.fromtimestamp(
                int(self.received_timestamp_tz)).strftime("%d-%b-%Y %H:%M:%S")
            _repository = git_url
            slack_message_text = '*Date*: {}\n*Repository*: {}\n*Branch*: {}\n*Error*: {}'.format(
                _date, _repository, branch, download["message"])
            slack_message = {
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": slack_message_text
                        }
                    }
                ]
            }
        self.notify(response_url, slack_message)
        return

    def notify(self, response_url, slack_message):
        print('Execute notify lib')
        headers = {'Content-type': 'application/json'}
        # data = {'text': message, 'response_type': 'in_channel'}
        data = slack_message
        print('INFO - notify - response_url: {}, {}'.format(response_url, slack_message))
        notifyResponse = requests.post(
            response_url, headers=headers, data=json.dumps(data))
        if notifyResponse.status_code == 200:
            print('INFO - notify - Data has been successfully posted to Slack')
        else:
            print('INFO - notify - Error: Failed to post data. {}'.format(notifyResponse.text))
        return

    def write_to_csv(self, scan_count, scan_results, repository, branch):
        print('Execute write_to_csv lib')
        # Write the scan results
        with open(self.scanner_results_directory_path+'scanner_results_{}.csv'.format(self.uuid), 'w+') as f:
            w = csv.writer(f)
            scan_results_dict = {"eventtime": "", "repository": "", "branch": "", "noOfSecrets": "", "StartLine": "",
                                 "EndLine": "", "StartColumn": "", "EndColumn": "", "File": "", "Author": "", "Email": "", "Date": "", "Message": ""}
            w.writerow(scan_results_dict.keys())
            if int(scan_count) != 0:
                for result in scan_results:
                    scanner_results_dict = {"eventtime": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], "repository": repository, "branch": branch, "noOfSecrets": scan_count, "StartLine": result["StartLine"], "EndLine": result[
                        "EndLine"], "StartColumn": result["StartColumn"], "EndColumn": result["EndColumn"], "File": result["File"], "Author": result["Author"], "Email": result["Email"], "Date": result["Date"], "Message": result["Message"][:25]}
                    w.writerow(scanner_results_dict.values())
                    print("DEBUG - write_to_csv - date={}, repository={}, branch={}, noOfSecrets={}, StartLine={}, EndLine={}, StartColumn={}, EndColumn={}, File={}, Author={}, Email={}, Date={}, Message={}".format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
                          [:-3], repository, branch, scan_count, result["StartLine"], result["EndLine"], result["StartColumn"], result["EndColumn"], result["File"], result["Author"], result["Email"], result["Date"], result["Message"][:25]))
            else:
                scanner_results_dict = {"eventtime": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], "repository": repository, "branch": branch, "noOfSecrets": "0",
                                        "StartLine": "", "EndLine": "", "StartColumn": "", "EndColumn": "", "File": "", "Author": "", "Email": "", "Date": "", "Message": ""}
                w.writerow(scanner_results_dict.values())
        return