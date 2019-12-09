#!/usr/local/bin/python3
# encoding: utf-8
# author: www.n0tr00t.com
# maintainer: ciaranchen

import sys
import glob
import json
import requests
import urllib.parse
import argparse
import multiprocessing
from lxml import html
from common.color import *
from common.output import *
from collections import OrderedDict


class Sreg():
    def __init__(self, plugin, passport, passport_type):
        """
        plugin: plugins/*.json
        passport: user, email, phone
        passport_type: passport type
        """
        self.plugin = plugin
        self.passport = passport
        self.passport_type = passport_type
        self.session = requests.Session()
        self.headers = OrderedDict({
            'Connection': 'closed',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6',
            'Accept-Encoding': 'gzip, deflate',
            'Accept': '*/*'
        })
        self.format_data = {
            'passport': passport,
            passport_type+"_passport": passport
        }
        self.cookies = {}
        # load plugin file
        with open(plugin) as f:
            try:
                self.content = json.load(f)
            except Exception as e:
                print(e, plugin)

    def do_get(self, url, headers={}):
        headers.update(self.headers)
        return self.session.get(url, headers=headers, timeout=8, cookies=self.cookies)

    def do_post(self, url, data={}, headers={}):
        headers.update(self.headers)
        return self.session.post(url, data=data, headers=headers, timeout=8, cookies=self.cookies)

    def check(self):
        # By default, Sreg do not check `not sure` or `error` status plugins.
        if "status" in self.content and (self.content["status"] == 'error' or self.content["status"] == 'not sure'):
            return
        if "type" in self.content and self.passport_type not in self.content["type"]:
            return
        if "before_check" in self.content:
            for req_block in self.content["before_check"]:
                self.before_check(req_block)
        return self._check()

    def before_check(self, block):
        method = block['method']
        url = block["{0}_url".format(self.passport_type)]
        if method == 'GET':
            res = self.do_get(url)
            self.cookies = res.cookies
        elif method == 'POST':
            res = self.do_post(url)
            self.cookies = res.cookies
        else:
            pass

        if 'export' in block:
            tree = html.fromstring(res.text)
            for ex in block['export']:
                self.format_data[ex] = tree.xpath(block['export'][ex])
        return res

    def _check(self):
        url = self.content["request"]["{0}_url".format(self.passport_type)]
        url = url.replace('{}', self.passport)
        url = url.format(**self.format_data)

        self.headers['Host'] = urllib.parse.urlparse(url).netloc
        self.headers['Referer'] = url
        if "headers" in self.content:
            for header_key in list(self.content['headers'].keys()):
                self.headers[header_key] = self.content['headers'][header_key]

        if self.content['request']['method'] == "GET":
            try:
                content = self.do_get(url).text
            except Exception as e:
                err = '\n[-] %s Error: %s\n' % (url, str(e))
                print(inRed(err))
                return
        elif self.content['request']['method'] == "POST":
            post_data = self.content['request']['post_fields']
            for k in post_data:
                post_data[k] = post_data[k].format(**self.format_data)
            try:
                content = self.do_post(url, data=post_data).text
            except Exception as e:
                err = '\n[-] %s Error: %s\n' % (url, str(e))
                print(inRed(err))
                return
        # print(content)

        if self.judge(content):
            app_name = self.content['information']['name']
            category = self.content["information"]["category"]
            website = self.content["information"]["website"]
            icon = self.content['information']['icon']
            desc = self.content['information']['desc']
            output_add(category, app_name, website,
                       self.passport, self.passport_type, icon, desc)
            print("[{0}] {1}".format(
                category, ('%s (%s)' % (app_name, website))))

    def judge(self, content):
        status = self.content['judge']
        if 'judge_yes_keyword' in status and status['judge_yes_keyword'] in content:
            return True
        if 'judge_no_keyword' in status and status['judge_no_keyword'] in content:
            return False
        return False


def main(Sreg=Sreg):
    parser = argparse.ArgumentParser(
        description="Check how many Platforms the User registered.")
    parser.add_argument("-u", action="store", dest="user")
    parser.add_argument("-e", action="store", dest="email")
    parser.add_argument("-c", action="store", dest="cellphone")
    parser_argument = parser.parse_args()
    banner = '''
     .d8888b.
    d88P  Y88b
    Y88b.
     "Y888b.  888d888 .d88b.  .d88b.
        "Y88b.888P"  d8P  Y8bd88P"88b
          "888888    88888888888  888
    Y88b  d88P888    Y8b.    Y88b 888
     "Y8888P" 888     "Y8888  "Y88888
                                  888
                             Y8b d88P
                              "Y88P"
    '''
    all_argument = [parser_argument.cellphone,
                    parser_argument.user, parser_argument.email]
    plugins = glob.glob("./plugins/*.json")
    print(inGreen(banner))
    print('[*] App: Search Registration')
    print('[*] Version: V1.2(20191209)')
    print('[*] Website: www.n0tr00t.com')
    print('[*] Maintainer: ciaranchen')
    file_name = ""
    if all_argument.count(None) != 2:
        print('\nInput "-h" view the help information.')
        sys.exit(0)
    if parser_argument.cellphone:
        print(inYellow('\n[+] Phone Checking: %s\n') %
              parser_argument.cellphone)
        file_name = "cellphone_" + str(parser_argument.cellphone)
        output_init(file_name, "Phone: ", str(parser_argument.cellphone))
    elif parser_argument.user:
        print(inYellow('\n[+] Username Checking: %s\n') % parser_argument.user)
        file_name = "user_" + str(parser_argument.user)
        output_init(file_name, "UserName: ", str(parser_argument.user))
    elif parser_argument.email:
        print(inYellow('\n[+] Email Checking: %s\n') % parser_argument.email)
        file_name = "email_" + str(parser_argument.email)
        output_init(file_name, "E-mail: ", str(parser_argument.email))
    jobs = []
    for plugin in plugins:
        if parser_argument.cellphone:
            obj = Sreg(plugin, str(parser_argument.cellphone), "phone")
        elif parser_argument.user:
            obj = Sreg(plugin, str(parser_argument.user), "user")
        elif parser_argument.email:
            obj = Sreg(plugin, str(parser_argument.email), "email")
        p = multiprocessing.Process(target=obj.check)
        p.start()
        jobs.append(p)
    while sum([i.is_alive() for i in jobs]) != 0:
        pass
    for i in jobs:
        i.join()
    output_finished(file_name)


if __name__ == '__main__':
    main()
