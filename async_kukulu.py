import aiohttp
#from bs4 import BeautifulSoup
import re
from typing import NamedTuple

class KukuluError(Exception):
    pass
class Kukulu():
    def __init__(self, csrf_token:str=None, sessionhash:str=None, proxy:str=None):
        self.csrf_token = csrf_token
        self.sessionhash = sessionhash
        self.proxy = proxy
        self.session = aiohttp.ClientSession()
        self.initialized = False
        if csrf_token and sessionhash:
            self.session.cookie_jar.update_cookies({"cookie_csrf_token": csrf_token})
            self.session.cookie_jar.update_cookies({"cookie_sessionhash": sessionhash})
            self.initialized = True
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def initialize(self):
        if self.initialized:
            return
        
        async with self.session.post("https://m.kuku.lu", proxy=self.proxy) as response:
            pass

        kukulu_cookies = self.session.cookie_jar.filter_cookies("https://m.kuku.lu")
        self.csrf_token = kukulu_cookies.get("cookie_csrf_token").value
        self.sessionhash = kukulu_cookies.get("cookie_sessionhash").value
        self.initialized = True

    async def new_account(self):
        if not self.initialized:
            await self.initialize()

        kukulu_cookies = self.session.cookie_jar.filter_cookies("https://m.kuku.lu")
        cookie_csrf_token = kukulu_cookies.get("cookie_csrf_token")
        cookie_sessionhash = kukulu_cookies.get("cookie_sessionhash")
        class Account(NamedTuple):
            csrf_token: str
            sessionhash: str
        
        return Account(csrf_token=cookie_csrf_token.value, sessionhash=cookie_sessionhash.value)
    
    async def create_mailaddress(self):
        if not self.initialized:
            await self.initialize()

        async with self.session.get("https://m.kuku.lu/index.php?action=addMailAddrByAuto&nopost=1&by_system=1", proxy=self.proxy) as response:
            response_text = await response.text()
            
        if "最大数" in response_text or "Forbidden" in response_text:
            raise KukuluError(response_text)
        
        return response_text[3:]

    async def specify_address(self,address:str):
        if not self.initialized:
            await self.initialize()

        async with self.session.get(f"https://m.kuku.lu/index.php?action=addMailAddrByManual&nopost=1&by_system=1&t=1716696234&csrf_token_check={self.csrf_token}&newdomain={address}",proxy=self.proxy) as response:
            response_text = await response.text()
        return response_text[3:]
    
    async def check_top_mail(self, mail_address:str):
        if not self.initialized:
            raise KukuluError("Kukulu client is not initialized")

        class Mail(NamedTuple):
            title: str
            text: str

        mail_address = mail_address.replace("@","%40")
        async with self.session.get(f"https://m.kuku.lu/recv._ajax.php?&q={mail_address}&&nopost=1&csrf_token_check={self.csrf_token}",proxy=self.proxy) as response:
            mails_text = await response.text()

        if "NG:CSRF Security Error!" in mails_text:
            raise KukuluError("CSRF Token is invalid or expired.")

        match = re.search(r"openMailData\(['\"]?(\d+)['\"]?,\s*['\"]?([a-f0-9]+)['\"]?", mails_text)

        if match:
            mail_num = match.group(1)
            mail_key = match.group(2)
        else:
            return Mail(title="No Mail", text="")

        async with self.session.post(
            "https://m.kuku.lu/smphone.app.recv.view.php",
            data={"num": mail_num, "key": mail_key, "noscroll": "1"},
            proxy=self.proxy
        ) as response:
            mail_text = await response.text()

        match = re.search(r'class="full"[^>]*>(.*?)<', mail_text, re.DOTALL)
        if match:
            title = match.group(1).strip()
        else:
            title = ""

        #--------------------------------------------
        #ここの部分は届くメールによってよく変わるから注意
        match = re.search(r'dir="ltr"[^>]*>(.*?)<', mail_text, re.DOTALL)

        if match:
            text = match.group(1).strip()
        else:
            text = ""
        #m.kuku.luは便利だけど自動化するにあたっては他のプラットフォームの方がいい可能性アリ
        #----------------------------------------------------------------------------
        
        return Mail(title=title, text=text)