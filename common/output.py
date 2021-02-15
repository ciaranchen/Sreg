# encoding: utf-8
import os, datetime, json
from mako.template import Template


class JsonEncoder():
    def __init__(self):
        self.path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'reports'))
        os.makedirs(self.path, exist_ok=True)
        self.now_time = datetime.datetime.now()


    def add_passport(self, passport_type, passport, apps):
        filename = os.path.join(self.path, passport_type + '_' + passport) + '.json'
        output = {
            "passport_type": passport_type, 
            "passport": passport,
            "datetime": self.now_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        output['results'] = [{
            "name": app.meta_info.name,
            "website": app.meta_info.website,
            "judge": r
        } for app, _, _, r in apps]

        with open(filename, 'w', encoding='utf-8') as fp:
            json.dump(output, fp, ensure_ascii=False)
        print('\n[+] Results the save path: %s' % filename)


class HtmlEncoder(JsonEncoder):
    def add_passport(self, passport_type, passport, apps):
        filename = os.path.join(self.path, passport_type + '_' + passport) + '.html'
        data = [{
            "name": app.meta_info.name,
            "website": app.meta_info.website,
            "description": app.meta_info.desc,
            "icon": app.meta_info.icon,
            "judge": r
        } for app, _, _, r in apps]
        data.sort(key=lambda x: x['judge'], reverse=True)
        output = Template(filename=os.path.join(os.path.dirname(__file__), 'template.html')).render(o_type=passport_type, o_passport=passport, apps=data, now=self.now_time.strftime("%Y-%m-%d %H:%M:%S"))
        # print(output)
        with open(filename, 'w', encoding='utf-8') as fp:
            fp.write(output)
        print('\n[+] Results the save path: %s' % filename)
