from sreg3 import Sreg
import json
from lxml import html


def main():
    filename = "./plugins/email_github_com.json"
    sreg1 = Sreg(filename, "760218327@qq.com", "email")
    sreg1.check()
    # sreg2 = Sreg(filename, "ciaranchen@qq.com", "email")
    # sreg2.check()


def parse_github():
    with open('temp.html') as fp:
        tree = html.fromstring(fp.read())
    a = tree.xpath('//auto-check[@src="/signup_check/email"][not(@class)]/@csrf')
    print(a)


if __name__ == '__main__':
    main()
    # parse_github()
