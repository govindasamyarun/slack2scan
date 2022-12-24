from threading import Thread
from flask import request, send_file
from config import S2SConfig
from libs.slack2scan import S2S

def scan():
    print('Execute scan API controller')
    Thread(target=S2S(request.get_data().decode("utf-8"), request.headers['X-Slack-Request-Timestamp'], request.headers['X-Slack-Signature']).scan_engine).start()
    return ''

def download(fileId):
    print('Execute download API controller')
    return send_file(S2SConfig.scanner_results_directory_path+'scanner_results_{}.csv'.format(fileId), mimetype='text/csv', as_attachment=True)

def interactive():
    print('Execute interactive API controller')
    return ''