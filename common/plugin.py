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


    @staticmethod
    def get_all_state():
        return [PluginStatus.OK, PluginStatus.ERROR, PluginStatus.DEBUG, PluginStatus.NOTSURE]


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


    def check(self, _type, passport):
        passport_type = PassportType.get_string(_type)
        format_data = {
            'passport': passport,
            passport_type+"_passport": passport
        }
        if "before_check" in self.content:
            export = self.before_check(self.content['before_check'], passport_type, passport)
            if export:
                format_data.update(export)
        resp = self.do_check(url=self.content['request'][passport_type + '_url'].format(**format_data), request=self.content['request'], headers=self.content.get('headers', None), data=format_data)
        # print(resp)
        return self.judge(resp, self.content['judge'])


    def before_check(self, json_config, passport_type, passport):
        for block in json_config:
            method = block['method']
            url = block["url"]
            if method == 'GET':
                res = self.do_get(url)
                self.cookies = res.cookies
            elif method == 'POST':
                res = self.do_post(url)
                self.cookies = res.cookies

            if 'export' in block:
                tree = html.fromstring(res.text)
                return {ex: tree.xpath(block['export'][ex]) for ex in block['export']}


    def do_check(self, url, headers, request, data):
        req_headers = self.headers.copy()
        req_headers.update({
            'Host': urllib.parse.urlparse(url).netloc,
            'Referer': url
        })

        if headers:
            req_headers.update(headers)

        # do a check
        if request['method'] == "GET":
            resp = self.do_get(url).text
        elif request['method'] == "POST":
            post_data = request['post_fields']
            for k in post_data:
                if isinstance(post_data[k], str):
                    post_data[k] = post_data[k].format(**data)
            resp = self.do_post(url, data=post_data).text
        return resp


    def judge(self, resp, judge_block):
        if 'judge_yes_keyword' in judge_block and judge_block['judge_yes_keyword'] in resp:
            return True
        if 'judge_no_keyword' in judge_block and judge_block['judge_no_keyword'] in resp:
            return False
        if 'judge_yes_keyword' in judge_block and 'judge_no_keyword' in judge_block:
            raise RuntimeError('Plugin check failed.')
        return False


class JsonPlugin2(JsonPlugin):
    def get_types(self):
        if 'request' in self.content:
            assert 'request' in self.content
            assert 'judge' in self.content
            return super().get_types()
        else:
            return [PassportType.get_passport_type(k) for k in self.content if PassportType.get_passport_type(k) in PassportType.get_all_types()]


    def check(self, _type, passport):
        if 'request' in self.content:
            return super().check(_type, passport)
        else:
            passport_type = PassportType.get_string(_type)
            format_data = {
                'passport': passport,
                passport_type+"_passport": passport
            }
            assert passport_type in self.content

            if "before_check" in self.content[passport_type]:
                export = self.before_check(self.content[passport_type]['before_check'], passport_type, passport)
                if export:
                    format_data.update(export)
            resp = self.do_check(url=self.content[passport_type]['url'].format(**format_data), request=self.content[passport_type], headers=self.content[passport_type].get('headers', None), data=format_data)
            return self.judge(resp, self.content[passport_type]['judge'])
