import json
import requests
from lxml import etree
from urllib import parse

class DailyReportBot:
    URL_LOGIN = 'https://passport.ustc.edu.cn/login?service=https%3A%2F%2Fweixine.ustc.edu.cn%2F2020%2Fcaslogin'
    URL_LOGIN_POST = 'https://passport.ustc.edu.cn/login'
    URL_REPORT = 'https://weixine.ustc.edu.cn/2020/daliy_report'

    def __init__(self, config, write_log=False):
        self.write_log = write_log
        self.config = config
        self.parse()

        #creat session
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36"
        })

    def run(self):
        login_resp = self.login()

        self.report(login_resp)

    def login(self):
        #Get CAS
        resp = self.session.get(url=self.URL_LOGIN)
        if resp.status_code != 200:
            print('[ERROR]: Get login page failed, Please check network connecting')
            exit(1)
        html = etree.HTML(resp.text)
        CAS_LT = html.xpath('//*[@id="CAS_LT"]')[0].attrib['value']
        self.login_dict['CAS_LT'] = CAS_LT

        #post login
        resp = self.session.post(url=self.URL_LOGIN_POST, data=self.login_dict)
        if resp.status_code != 200:
            print('[ERROR]: Login failed, make sure using campus network(no CAPTCHA)')
            exit(1)
        
        return resp
    
    def report(self, login_resp):
        #get secret token
        html = etree.HTML(login_resp.text)
        _token = html.xpath('//*[@id="daliy-report"]/form/input')[0].attrib['value']
        self.report_dict['_token'] = _token

        #post report
        resp = self.session.post(url=self.URL_REPORT, data=self.report_dict)
        if resp.status_code != 200:
            print('[ERROR]: Report failed')
            exit(1)
        
        #check result
        html = etree.HTML(resp.text)
        msg = html.xpath('//*[@id="wrapper"]/div[2]/div[1]/p')[0].text
        print(msg)
        if self.write_log:
            with open('report.log', 'w', encoding='utf-8') as f:
                f.write(msg)

    def parse(self):
        self.login_dict = {
            'model': 'uplogin.jsp',
            'service': 'https://weixine.ustc.edu.cn/2020/caslogin',
            'username': self.config['username'],
            'password': self.config['password']
        }

        self.report_dict = {}
        kv_list = parse.unquote(self.config['report_post_str']).strip().split('&')

        for kv in kv_list:
            k, v = kv.split('=')
            k, v = k.strip(), v.strip()
            self.report_dict[k] = v

        # print(self.login_dict)
        # print(self.report_dict)

if __name__ == '__main__':
    with open('config.json', encoding='utf-8') as fp:
        config = json.load(fp)
    
    bot = DailyReportBot(config, write_log=True)
    bot.run()