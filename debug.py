from sreg import Sreg, main
import json
from lxml import html



def single_test():
    filename = "./plugins/email_github_com.json"
    sreg1 = Sreg(filename, "760218327@qq.com", "email")
    sreg1.check()
    # sreg2 = Sreg(filename, "ciaranchen@qq.com", "email")
    # sreg2.check()


def xpath_github():
    # filename = "./plugins/username_github_com.json"
    # sreg1 = Sreg(filename, "ciaranchen", "user")
    # r = sreg1.check()
    # print(r.text)
    # tree = html.fromstring(r.text)
    with open('temp.html') as fp:
        tree = html.fromstring(fp.read())
    a = tree.xpath('//auto-check[@src][1][not(@class)]/@csrf')
    print(a)

class Sreg_debug(Sreg):
    def check(self):
        # By default, Sreg do not check `not sure` or `error` status plugins.
        if "status" in self.content and self.content["status"] != 'debug':
            return
        if "type" in self.content and self.passport_type not in self.content["type"]:
            return
        if "before_check" in self.content:
            for req_block in self.content["before_check"]:
                self.before_check(req_block)
        print(self.content['information']['name'])
        content = self._check()
        print(content)
        with open('temp.html', 'w') as fp:
            fp.write(content)
        return content


if __name__ == '__main__':
    main(Sreg_debug)
    # parse_github()
