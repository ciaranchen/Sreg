### Sreg(Search Registration) V2.0

本项目Forked自 [https://github.com/n0tr00t/sreg](https://github.com/n0tr00t/sreg)，原项目已不再维护。

但是在使用时发现，输出中有很多我不想要的东西，另外也有不少希望添加的功能没有加上去，所以想着稍微做一些修改。从Fork以来对项目的大部分内容经过了重构，除了借鉴与继承原项目的众多Plugins，基本已经可以算是一个新的东西了。

Sreg可对使用者通过输入`email`、`phone`、`username`的返回用户注册的所有互联网凭证信息，例如：

```
❯ python .\sreg.py -h
usage: sreg.py [-h] [-u USER] [-e EMAIL] [-c CELLPHONE] [-l] [--list-all] [--no-html]

Check how many Platforms the User registered.

optional arguments:
  -h, --help    show this help message and exit
  -u USER
  -e EMAIL
  -c CELLPHONE
  -l, --list    列出对应凭证会检查的插件
  --list-all    显示所有插件
  --no-html     不输出html文件
```

```
❯ python sreg.py -e test@test.com

        .d8888b.
        d88P  Y88b
        Y88b.
            "Y88b.888P"  d8P  Y8bd88P"88b
            "888888    88888888888  888
        "Y8888P" 888     "Y8888  "Y88888
                                    888
                                Y8b d88P
                                "Y88P"

[*] App: Search Registration
[*] Version: V2.0(2021-02-15)
[*] Maintainer: ciaranchen


[+] Email Checking: test@test.com

[+] 58同城(http://www.58.com/): test@test.com Registered
[+] 91wan(http://www.91wan.com/): test@test.com Not Registered
[+] 人人网(http://www.renren.com/): test@test.com Registered
[+] 前程无忧(http://www.51job.com/): test@test.com Registered
[+] 果壳网(http://www.guokr.com/): test@test.com Registered
[+] 微博(http://www.weibo.com/): test@test.com Registered
[+] 当当网(http://www.dangdang.com/): test@test.com Not Registered
[+] Github(https://www.github.com/): test@test.com Registered

[+] Results the save path: D:\Desktop\Projects\Sreg\reports\email_test@test.com.html
```

Sreg一共有三种查询方式：

- 用户名
- 手机
- 邮箱

查询完成后，Sreg会返回给使用者一个精致的html页面供以查看。

### Plugin (V2)

编写网站注册查询插件非常简单，首先将想要进行编写的网站在```/plugins/```建立对应```website.json```文件。

```json
{
    "status": "ok",
    "information": {
        "author": "ciaranchen",
        "create_date": "2015/03/12",
        "update_date": "2019/12/09",
        "name": "Github",
        "website": "https://www.github.com/",
        "category": "IT",
        "icon": "http://a.36krcnd.com/photo/a462f1f368e67d9ebece977eaabe5b32.png",
        "desc": "作为开源代码库以及版本控制系统，Github拥有140多万开发者用户。随着越来越多的应用程序转移到了云上，Github已经成为了管理软件开发以及发现已有代码的首选方法"
    },
    "email": {
        "url": "https://github.com/signup_check/email",
        "method": "POST",
        "post_fields": {
            "value": "{email_passport}",
            "authenticity_token": "{csrf_token[0]}"
        },
        "before_check": [
            {
                "method": "GET",
                "url": "https://github.com/join/",
                "cookie": true,
                "export": {
                    "csrf_token": "//*[@id=\"signup-form\"]/auto-check[2]/input/@value"
                }
            }
        ],
        "judge": {
            "judge_yes_keyword": "Email is invalid or already taken"
        }
    }
}
```


- information: 插件编写者及网站所需信息；
- status: 插件当前状态；一般为ok；
- [phone, email, user]: 核心接口定义，分别对应手机注册、邮箱注册、用户名注册查询接口。主要包括：
    - before_check: 用于在请求查询接口前，获得csrf token或者cookie的请求。其中url、method、post_fields的定义参见核心接口的三者定义。
        - export: 需要导出的变量。其值应为导出的变量在返回结果的位置，以xpath表示。
    - url: 接口请求的url。
    - method: 接口请求的方法，仅支持GET与POST。如果接口为POST方法，则应定义post_fields为参数字段
    - post_fields: POST请求的body参数。
    - judge: 返回结果判断。`judge_yes_keyword`为用户已经注册此网站时，接口返回的字符串中应当包含的子串。`judge_no_keyword`为用户未注册此网站时，接口返回的字符串中应当包含的子串。

在url和post_fields中可以使用`{passport}`指定凭证，或者使用`before_check`中导出的新变量。
