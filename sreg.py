#!/usr/local/bin/python3
# encoding: utf-8
# author: blog.ciaran.cn
# maintainer: ciaranchen

import sys, os
import argparse
import threading
from common.passport import PassportEncoder, PassportType
from common.plugin import JsonPlugin2 as JsonPlugin, PluginStatus
from common.color import *
from common.output import HtmlEncoder as OutputEncoder


# Sreg 应该是所有plugin组合后的类
class Sreg(object):
    def welcome_message(self):
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

        print(inGreen(banner))
        print('[*] App: Search Registration')
        print('[*] Version: V1.2(20191209)')
        print('[*] Maintainer: ciaranchen\n')


    def __init__(self, silence=False):
        if not silence:
            self.welcome_message()
        self.base_dir = os.path.dirname(__file__)
        self.plugin_path = os.path.join(self.base_dir, "plugins")
        self.res = []


    def set_passports(self, passports):
        self.passports = passports
        self.plugins = self.load_plugins(self.plugin_path, self.passports.get_types())


    def load_plugins(self, paths, types, allow_status = [PluginStatus.OK]):
        plugins = []
        for path, subdirs, filenames in os.walk(paths):
            for filename in filenames:
                if filename.endswith('.json'):
                    plug = JsonPlugin(os.path.join(path, filename))
                    inter = set(plug.get_types()).intersection(set(types))
                    if len(inter) > 0 and plug.status in allow_status:
                        plugins.append(plug)
                elif filename.endswith('.py'):
                    pass
                else:
                    pass
        return plugins


    def select_plugins(self, _type):
        return [p for p in self.plugins if _type in p.get_types()]


    def run_checks(self):
        res = {}
        for t, p in self.passports:
            key = p
            res[key] = []
            plugs = self.select_plugins(t)
            for plug in plugs:
                try:
                    judge_result = plug.check(t, p)
                    res[key].append((plug, judge_result))
                except Exception as e:
                    err = '\n[-] %s(%s) Error: %s\n' % (plug, p, str(e))
                    print(inRed(err))
        return res


    def single_check(self, plug, t, p):
        try:
            res = plug.check(t, p)
            if res:
                print(inGreen('[+] %s: %s Registered' % (plug.meta_info.name, p)))
            else:
                print('[+] %s: %s ' % (plug, p) + inYellow('Not') + ' Registered')
            self.res.append((plug, t, p, res))
            return res
        except Exception as e:
            err = '[-] %s(%s) Error: %s\n' % (plug, p, str(e))
            print(inRed(err))
            return None


    def check_parallel(self):
        threads = []
        for t, p in self.passports:
            key = p
            plugs = self.select_plugins(t)
            for plug in plugs:
                threads.append(threading.Thread(target=self.single_check, args=(plug, t, p)))
        for t in threads:
            t.start()
        for t in threads:
            t.join() # 等待所有线程执行到此处再继续往下执行


    @staticmethod
    def list_by_categories(with_status=False):
        sreg = Sreg(silence=True)
        plugins = sreg.load_plugins(sreg.plugin_path, types=PassportType.get_all_types(), allow_status=PluginStatus.get_all_state())
        all_categories = set([p.meta_info.category for p in plugins])
        for c in all_categories:
            print('\n' + c + ':')
            for p in [p for p in plugins if p.meta_info.category == c]:
                print(p)
        # print(all_categories)


    def output(self):
        encoder = OutputEncoder()
        for t, p in self.passports:
            res = [r for r in self.res if r[1] == t and r[2] == p]
            encoder.add_passport(PassportType.get_string(t), p, res)


def main(Sreg=Sreg):
    parser = argparse.ArgumentParser(
        description="Check how many Platforms the User registered.")
    parser.add_argument("-u", action="store", dest="user")
    parser.add_argument("-e", action="store", dest="email")
    parser.add_argument("-c", action="store", dest="cellphone")
    parser.add_argument("-l", "--list", action="store_true", dest="list_data")
    parser.add_argument('--list-all', action="store_true", dest="list_all")
    parser.add_argument('--no-html', action="store_true", dest="nohtml")
    parser_argument = parser.parse_args()

    if parser_argument.list_all:
        Sreg.list_by_categories()
        sys.exit(0)

    all_argument = [parser_argument.cellphone,
                    parser_argument.user, parser_argument.email]
    if all_argument.count(None) != 2:
        print('\nInput "-h" view the help information.')
        sys.exit(0)

    sreg = Sreg()

    passports = PassportEncoder()
    passports.add_passport(PassportType.USER, parser_argument.user)
    passports.add_passport(PassportType.PHONE, parser_argument.cellphone)
    passports.add_passport(PassportType.EMAIL, parser_argument.email)
    print(inYellow(passports.get_output()))
    sreg.set_passports(passports)

    if parser_argument.list_data:
        for p in sreg.plugins:
            print('- ' + str(p))
        sys.exit(0)

    # print(sreg.run_checks())
    sreg.check_parallel()
    if not parser_argument.nohtml:
        sreg.output()


if __name__ == '__main__':
    main()
