# m.kuku.lu-Generator
m.kuku.luという捨てメアド作成サイトの自動化コード  
捨てメアドジェネレーター  
https://m.kuku.lu/
## 必須モジュール
- requests
- bs4
## コード本文
#### kukulu.py
```py
import requests
from bs4 import BeautifulSoup
import re

class Kukulu():
    def __init__(self,csrf_token:str=None,sessionhash:str=None,proxy:dict=None):
        self.csrf_token=csrf_token
        self.sessionhash=sessionhash
        self.proxy=proxy
        self.session=requests.Session()
        if csrf_token!=None and sessionhash!=None:
            self.session.cookies.set("cookie_csrf_token",csrf_token)
            self.session.cookies.set("cookie_sessionhash",sessionhash)
            self.session.post("https://m.kuku.lu",proxies=proxy)
        else:
            self.session.post("https://m.kuku.lu",proxies=proxy)
    
    def new_account(self):
        return {"csrf_token":self.session.cookies["cookie_csrf_token"],"sessionhash":self.session.cookies["cookie_sessionhash"]}
    
    def create_mailaddress(self):
        return self.session.get("https://m.kuku.lu/index.php?action=addMailAddrByAuto&nopost=1&by_system=1",proxies=self.proxy).text[3:]
    
    def specify_address(self,address:str):
        return self.session.get(f"https://m.kuku.lu/index.php?action=addMailAddrByManual&nopost=1&by_system=1&t=1716696234&csrf_token_check={self.csrf_token}&newdomain={address}",proxies=self.proxy).text[3:]
    
    def check_top_mail(self,mailaddress:str):
        mailaddress=mailaddress.replace("@","%40")
        mails=self.session.get(f"https://m.kuku.lu/recv._ajax.php?&q={mailaddress}&&nopost=1&csrf_token_check={self.csrf_token}",proxies=self.proxy)
        soup=BeautifulSoup(mails.text,"html.parser")
        script=soup.find_all("script")
        match = re.search("(openMailData[^ ]+)", str(script))
        openMailData=match.group()
        openMailData=openMailData.replace("openMailData(","")
        match2=re.findall(f"{openMailData} [^ ]+", str(script))
        maildata=match2[1].split("'")
        mail=self.session.post("https://m.kuku.lu/smphone.app.recv.view.php",data={"num":maildata[1],"key":maildata[3],"noscroll": "1"},proxies=self.proxy)
        soup=BeautifulSoup(mail.text,"html.parser")
        title=soup.find(class_="full").text

        #--------------------------------------------
        #ここの部分は届くメールによってよく変わるから注意
        text=soup.find(dir="ltr").text
        #m.kuku.luは便利だけど自動化するにあたっては他のプラットフォームの方がいい可能性アリ
        #----------------------------------------------------------------------------

        return {"title":title[7:-4],"text":text}
```
これがコード本文  
でも使うときは同じディレクトリに置いて、モジュールのようにインポートしたらきれいでグッド  
モジュールにしない理由は```text=```の部分を改造する可能性があるからです  
## 具体的な使い方
### example.py
```py
from kukulu import Kukulu

kukulu=Kukulu()
token=kukulu.new_account()#dictで "csrf_token" と "sessionhash" だけが返ってくる
kukulu=Kukulu(token["csrf_token"],token["sessionhash"])
newmail=kukulu.create_mailaddress()
print(newmail)
print(kukulu.check_top_mail(newmail))
print(kukulu.specify_address("@から下"))
```
### new_account
m.kuku.luはクッキーの "csrf_token" と "sessionhash" の値で1つのアカウントを保持しているみたいです    
単にメールアドレスを作成するだけでは受信トレイを開けないのでこの2つの値は保存する必要があります  
メールアドレスだけではトークンエラーになって```check_top_mail```は使えないです  
### ログイン  
```Kukulu("csrf_token","sessionhash")```でログイン、といってもクッキーをつけるだけ  
### メール確認  
```check_top_mail("メールアドレス")```で1番最新のメールをdictで "title" と "text" にわけて返す  
### テキストは送られてくるメール内容によって書き換える必要がある  
というのもただのプレーンテキストだけで送ってこられる場合なにも変える必要はないけど、いろんなサービスのメールはhtmlの場合が多い  
そうなるとbs4でそのhtmlをさらにスクレイピングする必要アリ  
ここは自力で頑張るか、他の人にやってもらうか、もう本文すべてを返すしかない  
### アドレス指定でメールを作成
1度このコードのようにリクエストする前に  
https://m.kuku.lu/index.php?action=checkNewMailUser&ip=```IPv6```&nopost=1&csrf_token_check=```csrf_token```&csrf_subtoken_check=```csrf_subtoken```&newdomain=```ドメイン```&newuser=&_=```newuser```  
にリクエストする必要がある  
ただここは自動化するより実際にサイトを見て選んだ方が100倍いい ( なにが新しいドメインかがわかったりする ) ので選んで1つ作ったアカウントのクッキーを保存したらOK  
そもそもアドレス指定が必要なのは作るのは捨てメアド判定が導入されているサービスのみ  
## 余談
捨てメアド作成の自動化においてはm.kuku.luより良いサービス ( APIが使いやすいという意味で ) はいろいろある ( 1secmailやdevelopermailなど )  
どうしてもm.kuku.luが良かったり、捨てメアド判定を回避したい時にこのコードが役に立つでしょう....
## コンタクト  
Discord サーバー / https://discord.gg/aSyaAK7Ktm  
Discord ユーザー名 / .taka.  
