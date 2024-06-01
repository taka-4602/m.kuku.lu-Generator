from kukulu import Kukulu

kukulu=Kukulu()
token=kukulu.new_account()#dictで "csrf_token" と "sessionhash" だけが返ってくる
kukulu=Kukulu(token["csrf_token"],token["sessionhash"])
newmail=kukulu.create_mailaddress()
print(newmail)
print(kukulu.check_top_mail(newmail))
print(kukulu.specify_address("@から下"))