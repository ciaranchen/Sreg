from sreg import *
import json
from lxml import html
from itertools import combinations


def xpath_test():
    # filename = "./plugins/user_github_com.json"
    with open('temp.html', encoding='utf-8') as fp:
        tree = html.fromstring(fp.read())
        
    a = tree.xpath('//*[@id="signup-form"]/auto-check[2]/input')
    print(a)


class Sreg_Debug(Sreg):
    def transfer(self):
        plug_path = os.path.join(self.base_dir, "plugs")
        os.makedirs(plug_path, exist_ok=True)
        plugins = self.load_plugins(self.plugin_path, types=PassportType.get_all_types(), allow_status=PluginStatus.get_all_state())
        plugs = {}
        not_trans = []
        repeat = []
        for p in plugins:
            if 'request' not in p.content:
                continue
            if p.meta_info.name in not_trans:
                continue
            if p.meta_info.name not in plugs:
                plugs[p.meta_info.name] = {}
                plugs[p.meta_info.name]['status'] = PluginStatus.get_str(p.status)
                plugs[p.meta_info.name]['information'] = p.meta_info.__dict__
            else:
                repeat.append(p.meta_info.name)
                if plugs[p.meta_info.name]['status'] != PluginStatus.get_str(p.status):
                    plugs.pop(p.meta_info.name)
                    not_trans.append(p.meta_info.name)
                    continue

            for t in (p.content['type'] if 'type' in p.content else [t.split('_')[0] for t in p.content['request'] if t.endswith('url')]):
                type_req = {
                    'url': p.content['request'][t + '_url'],
                    'method': p.content['request']['method']
                }
                if 'post_fields' in p.content['request']:
                    type_req['post_fields'] = p.content['request']['post_fields']
                if 'headers' in p.content:
                    type_req['headers'] = p.content['headers']
                if 'before_check' in p.content:
                    type_req['before_check'] = p.content['before_check']
                type_req['judge'] = p.content['judge']
                plugs[p.meta_info.name][t] = type_req

            # print(plugs[p.meta_info.name])

        for p in plugs:
            filename = plugs[p]['information']['website'].strip('http://').strip('https://').strip('/').replace('.', '_') + '.json'
            p_obj = [pi for pi in plugins if pi.meta_info.name == p][0]
            print(os.path.basename(p_obj.filename))
            # continue
            if os.path.basename(p_obj.filename) == filename:
                continue
            filepath = os.path.join(plug_path, filename)
            with open(filepath, 'w', encoding='utf8') as fp:
                json.dump(plugs[p], fp, indent=4, ensure_ascii=False)
        print(not_trans)


    def single_check(self, plug, t, p): 
        res = plug.check(t, p)
        if res:
            print(inGreen('[+] %s: %s Registered' % (plug.meta_info.name, p)))
        else:
            print('[+] %s: %s ' % (plug, p) + inYellow('Not') + ' Registered')
        self.res.append((plug, t, p, res))
        return res


    def set_passports(self, passports):
        self.passports = passports
        plug_path = os.path.join(self.base_dir, "plugs")
        # self.plugins = self.load_plugins(plug_path, self.passports.get_types(), allow_status=[PluginStatus.DEBUG])
        self.plugins = self.load_plugins(self.plugin_path, self.passports.get_types(), allow_status=[PluginStatus.DEBUG])


    def check_parallel(self):
        return super().check_parallel()


if __name__ == '__main__':
    sreg = Sreg_Debug(silence=True)
    sreg.transfer()

    # main(Sreg=Sreg_Debug)

    # xpath_test()
