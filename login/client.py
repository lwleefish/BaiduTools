import requests
import time
import json
import re
from crypto.bdrsa import Encrypt
from . import DotDict
#from . import DotDict
#import pdb

class LoginJson(DotDict):

    def __init__(self, data=None):
        try:
            if not data:
                data = {"errInfo": DotDict({"no": -1, "msg": "Error"})}
            elif isinstance(data, dict):
                DotDict.__init__(self, data)
            else:
                data = json.loads(data)
        except json.decoder.JSONDecodeError as e:
            print(data)
            print(e)
            raise e
    

class BaiduClient(object):
    """百度登录所使用的信息"""

    def __init__(self):
        self.session = requests.session()
        self.server_time = ""
        self.rsaPublicKeyModulus = ""
        self.fpUID = ""
        self.traceid = ""
    
    def init_baidu(self):
        self.get_server_time()
        self.getBaiduRSAPublicKeyModulus()
        self.getTraceID()
    
    def get_server_time(self):
        rsp = self.session.get("https://wappass.baidu.com/wp/api/security/antireplaytoken")
        if not rsp:
            raise IOError("网络出现了一点异常")
        raw = json.loads(rsp.text)
        self.server_time = raw["time"]

    def getBaiduRSAPublicKeyModulus(self):
        rsp = self.session.get("https://wappass.baidu.com/static/touch/js/login_d9bffc9.js")
        if not rsp:
            raise IOError("网络出现了一点异常")
        m = re.search(r',rsa:"(.*?)",error:', rsp.text) 
        if m:
            self.rsaPublicKeyModulus = m.group(1)
            print(self.rsaPublicKeyModulus)
        else:
            self.rsaPublicKeyModulus = "B3C61EBBA4659C4CE3639287EE871F1F48F7930EA977991C7AFE3CC442FEA49643212E7D570C853F368065CC57A2014666DA8AE7D493FD47D171C0D894EEE3ED7F99F6798B7FFD7B5873227038AD23E3197631A8CB642213B9F27D4901AB0D92BFA27542AE890855396ED92775255C977F5C302F1E7ED4B1E369C12CB6B1822F"
    
    def getTraceID(self):
        rsp = self.session.get("https://wappass.baidu.com/")
        if not rsp:
            raise IOError("网络不通")
        self.traceid = rsp.headers.get('Trace-Id', '')

    def parseCookie(self, lj, cookie):
        for key, value in cookie.items():
            if "BDUSS" == key:
                lj.data.BDUSS = value
            elif "PTOKEN" == key:
                lj.data.PToken = value
            elif "STOKEN" == key:
                lj.data.SToken = value
            print(str(lj))
            return lj

    def parsePhoneOrEmail(self, lj):
        rsp = self.session.get(lj.data.gotoUrl)
        rsp.encoding = "utf-8"
        raw_phone = re.search(r'<p class="verify-type-li-tiptop">(.*?)</p>\s+<p class="verify-type-li-tipbottom">通过手机验证码验证身份</p>', rsp.text)
        raw_email = re.search(r'<p class="verify-type-li-tiptop">(.*?)</p>\s+<p class="verify-type-li-tipbottom">通过邮箱验证码验证身份</p>', rsp.text)
        raw_token = re.search(r'token=([^&]+).*?&u=([^&]+)&', lj.data.gotoUrl)
        #raw_mobile_url = re.search(r'data-location="(/passport/authwidget?.?action=send&type=mobile[^"]+)"', rsp.text)
        #raw_email_url = re.search(r'data-location="(/passport/authwidget?.?action=send&type=email[^"]+)"', rsp.text)
        lj.data.phone = raw_phone.group(1) if raw_phone else "未找到手机号"
        lj.data.email = raw_email.group(1) if raw_email else "未找到邮箱地址"
        if raw_token:
            lj.data.token = raw_token.group(1)
            lj.data.u = raw_token.group(2)
        return lj

    def Login(self, username, password, verifycode, vcodestr):
        lj = LoginJson()
        enpass = Encrypt(self.rsaPublicKeyModulus).encrypt_nopadding(password + self.server_time)        
        if not enpass:
            lj.errInfo.msg = "RSA加密失败: " + self.rsaPublicKeyModulus
            return lj
        header = {
		    "Content-Type":     "application/x-www-form-urlencoded",
		    "Accept":           "application/json",
		    "Referer":          "https://wappass.baidu.com/",
		    "X-Requested-With": "XMLHttpRequest",
		    "Connection":       "keep-alive",
	    }
        for i in range(5):
            timestampStr = str(int(time.time())) + "773_357"
            post_data = {
                "username":     username,
                "password":     enpass,
                "verifycode":   verifycode,
                "vcodestr":     vcodestr,
                "isphone":      "0",
                "loginmerge":   "1", # 加入这个, 不用判断是否手机号了
                "action":       "login",
                "uid":          timestampStr,
                "skin":         "default_v2",
                "connect":      "0",
                "dv":           "tk0.408376350146535171516806245342@oov0QqrkqfOuwaCIxUELn3oYlSOI8f51tbnGy-nk3crkqfOuwaCIxUou2iobENoYBf51tb4Gy-nk3cuv0ounk5vrkBynGyvn1QzruvN6z3drLJi6LsdFIe3rkt~4Lyz5ktfn1Qlrk5v5D5fOuwaCIxUobJWOI3~rkt~4Lyi5kBfni0vrk8~n15fOuwaCIxUobJWOI3~rkt~4Lyz5DQfn1oxrk0v5k5eruvN6z3drLneFYeVEmy-nk3c-qq6Cqw3h7CChwvi5-y-rkFizvmEufyr1By4k5bn15e5k0~n18inD0b5D8vn1Tyn1t~nD5~5T__ivmCpA~op5gr-wbFLhyFLnirYsSCIAerYnNOGcfEIlQ6I6VOYJQIvh515f51tf5DBv5-yln15f5DFy5myl5kqf5DFy5myvnktxrkT-5T__Hv0nq5myv5myv4my-nWy-4my~n-yz5myz4Gyx4myv5k0f5Dqirk0ynWyv5iTf5DB~rk0z5Gyv4kTf5DQxrkty5Gy-5iQf51B-rkt~4B__",
                "getpassUrl":   "/passport/getpass?clientfrom=&adapter=0&ssid=&from=&authsite=&bd_page_type=&uid=" + timestampStr + "&pu=&tpl=wimn&u=https://m.baidu.com/usrprofile%3Fuid%3D" + timestampStr + "%23logined&type=&bdcm=060d5ffd462309f7e5529822720e0cf3d7cad665&tn=&regist_mode=&login_share_strategy=&subpro=wimn&skin=default_v2&client=&connect=0&smsLoginLink=1&loginLink=&bindToSmsLogin=&overseas=&is_voice_sms=&subpro=wimn&hideSLogin=&forcesetpwd=&regdomestic=",
                "mobilenum":    "undefined",
                "servertime":   self.server_time, 
                "gid":          "DA7C3AE-AF1F-48C0-AF9C-F1882CA37CD5",
                "logLoginType": "wap_loginTouch",
                "FP_UID":       "0b58c206c9faa8349576163341ef1321",
                "traceid":      self.traceid,
            }
            rsp = self.session.post("https://wappass.baidu.com/wp/api/login", data=post_data, headers=header)
            if not rsp:
                lj.errInfo.msg = "网络请求失败: "
                return lj
            #print(rsp.json())
            lj = LoginJson(rsp.json())
            if lj.errInfo.no == "0":
                cookie = requests.utils.dict_from_cookiejar(rsp.cookies)
                print(cookie)
                return self.parseCookie(cookie)
            elif "400010" == lj.errInfo.no:
                print(lj.errInfo.msg)
                return lj
            elif lj.errInfo.no == "400023" or lj.errInfo.no == "400101":
                if not lj.data.gotoUrl:
                    print(str(lj))
                    return
                lj = self.parsePhoneOrEmail(lj)
                vt = self.get_verify_type(lj)
                self.send_code_to_user(vt, lj.data.token)
                vcode = input("输入收到的验证码:")
                lj = self.verify_code(vt, lj.data.token, vcode, lj.data.u)               
                pdb.set_trace()
                return lj
            elif lj.errInfo.no == "400408":
                print("该账号需进行身份信息验证。")
                return lj
            else:
                print("https://wappass.baidu.com/cgi-bin/genimage?" + lj.data.codeString)
                vcodestr = lj.data.codeString
                verifycode = input("输入验证码:")
            time.sleep(2)

    def get_verify_type(self, lj):
        while True:
            print("需要身份验证：1 手机验证码验证(%s)   2 邮箱验证码验证(%s)" % (lj.data.phone, lj.data.email))
            v = input("请选择验证方式：" )
            if v != "1" and v != "2":
                print("输入有误, 请输入1或者2")
            else:
                return "mobile" if "1" == v else "email"

    def send_code_to_user(self, verifyType, token):
        url = "https://wappass.baidu.com/passport/authwidget?action=send&tpl=&type=%s&token=%s&from=&skin=&clientfrom=&adapter=2&updatessn=&bindToSmsLogin=&upsms=&finance=" % (verifyType, token)
        rsp = self.session.get(url)
        if not rsp:
            return "发送验证码失败"
        raw_msg = re.search(r'<p class="mod-tipinfo-subtitle">\s+(.*?)\s+</p>', rsp.text)
        return raw_msg.group(1) if raw_msg else "发送验证异常"
    
    def verify_code(self, verifyType, token, vcode, u):
        header = {
            "Connection":                "keep-alive",
            "Host":                      "wappass.baidu.com",
            "Pragma":                    "no-cache",
            "Upgrade-Insecure-Requests": "1",
        }
        timestampStr = str(int(time.time())) + "773_357994"
        url = "https://wappass.baidu.com/passport/authwidget?v=%s&vcode=%s&token=%s&u=%s&action=check&type=%s&tpl=&skin=&clientfrom=&adapter=2&updatessn=&bindToSmsLogin=&isnew=&card_no=&finance=&callback=%s" % (timestampStr, vcode, token, u, verifyType, "jsonp1")
        rsp = self.session.get(url, headers=header)
        if not rsp:
            raise IOError("验证失败")
        #pdb.set_trace()
        body = rsp.text[len("jsonp1("):-1].strip()
        data = json.loads(body)
        lj = LoginJson(data)
        #url = "%s&authsid=%s&fromtype=%s&bindToSmsLogin=" % (u, lj.data.authsid, verifyType)
        rsp = self.session.get(lj.data.u)
        return self.parseCookie(lj, requests.utils.dict_from_cookiejar(self.session.cookies))
