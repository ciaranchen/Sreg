from common.passport import PassportType
from enum import Enum
import requests, json
from collections import OrderedDict
from lxml import html
import urllib.parse


class PluginStatus(Enum):
    OK = 1
    ERROR = 2
    NOTSURE = 3
    DEBUG = 4


    @staticmethod
    def get_state(x: str):
        return {'ok': PluginStatus.OK, 'error': PluginStatus.ERROR, 'not_sure': PluginStatus.NOTSURE, 'debug': PluginStatus.DEBUG}[x]


    @staticmethod
    def get_str(x):
        return ['ok', 'error', 'not_sure', 'debug'][x.value - 1]


class MetaPlugin(object):
    """
    Plugin 应有的元数据
    """
    pass


class Plugin(object):
    def __init__(self):
        self.meta_info = MetaPlugin()
        self.status = PluginStatus.DEBUG
        self.session = requests.Session()
        self.headers = OrderedDict({
            'Connection': 'closed',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6',
            'Accept-Encoding': 'gzip, deflate',
            'Accept': '*/*'
        })
        self.cookies = {}


    def get_types(self):
        """返回检查什么类型
        Returns:
            List: 插件检查的凭证类型
        """
        return []


    def check(self, _type, passport):
        if _type == PassportType.USER:
            pass
        elif _type == PassportType.PHONE:
            pass
        elif _type == PassportType.EMAIL:
            pass
        else:
            pass


    def do_get(self, url, headers={}):
        headers.update(self.headers)
        return self.session.get(url, headers=headers, timeout=8, cookies=self.cookies)


    def do_post(self, url, data={}, headers={}):
        headers.update(self.headers)
        return self.session.post(url, data=data, headers=headers, timeout=8, cookies=self.cookies)


    def __repr__(self):
        string = self.meta_info.name
        return string


class JsonPlugin(Plugin):
    def __init__(self, filename):
        super(JsonPlugin, self).__init__()
        self.filename = filename
        # load plugin file
        with open(filename, encoding='utf-8') as f:
            self.content = json.load(f)
        self.meta_info.__dict__ = self.content['information']
        self.status = PluginStatus.get_state(self.content['status'])


    def get_types(self):
        res = super().get_types()
        # check type
        if 'user_url' in self.content['request']:
            res.append(PassportType.USER)
        if 'phone_url' in self.content['request']:
            res.append(PassportType.PHONE)
        if 'email_url' in self.content['request']:
            res.append(PassportType.EMAIL)
        return res


    def before_check(self, passport_type, json_config):
        for block in json_config:
            method = block['method']
            url = block["{0}_url".format(passport_type)]
            if method == 'GET':
                res = self.do_get(url)
                self.cookies = res.cookies
            elif method == 'POST':
                res = self.do_post(url)
                self.cookies = res.cookies

            if 'export' in block:
                tree = html.fromstring(res.text)
                for ex in block['export']:
                    self.format_data[ex] = tree.xpath(block['export'][ex])


    def check(self, _type, passport):
        passport_type = PassportType.get_string(_type)
        format_data = {
            'passport': passport,
            passport_type+"_passport": passport
        }
        if "before_check" in self.content:
            self.before_check(passport_type, self.content['before_check'])
            for req_block in self.content["before_check"]:
                self.before_check(req_block)

        
        url = self.content["request"]["{0}_url".format(passport_type)]
        url = url.replace('{}', passport)
        url = url.format(**format_data)

        self.headers['Host'] = urllib.parse.urlparse(url).netloc
        self.headers['Referer'] = url

        if "headers" in self.content:
            for header_key in list(self.content['headers'].keys()):
                self.headers[header_key] = self.content['headers'][header_key]

        # do a check
        if self.content['request']['method'] == "GET":
            resp = self.do_get(url).text
        elif self.content['request']['method'] == "POST":
            post_data = self.content['request']['post_fields']
            for k in post_data:
                if isinstance(post_data[k], str):
                    post_data[k] = post_data[k].format(**format_data)
            resp = self.do_post(url, data=post_data).text

        judge = self.judge(resp)
        return judge


    def judge(self, content):
        status = self.content['judge']
        if 'judge_yes_keyword' in status and status['judge_yes_keyword'] in content:
            return True
        if 'judge_no_keyword' in status and status['judge_no_keyword'] in content:
            return False
        return False
