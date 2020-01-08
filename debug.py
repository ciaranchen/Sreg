from sreg import Sreg, main
import json
from lxml import html


def xpath_test():
    # filename = "./plugins/user_github_com.json"
    with open('temp.html') as fp:
        tree = html.fromstring(fp.read())
    a = tree.xpath('//auto-check[@src][1][not(@class)]/@csrf')
    print(a)


class Sreg_Debug(Sreg):
    def is_ok(self):
        return "status" in self.content and self.content["status"] == 'debug'
    
    def check(self):
        content = super().check()
        print(content)
        with open('temp.html', 'w') as fp:
            fp.write(content)


if __name__ == '__main__':
    main(Sreg_Debug)
    # xpath_test()
