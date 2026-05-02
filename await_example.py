import asyncio
from async_kukulu import Kukulu

async def main():
    async with Kukulu(proxy=None) as kukulu:
        new_account = await kukulu.new_account()
        csrf_token = new_account.csrf_token
        sessionhash = new_account.sessionhash
        print(f"CSRF Token: {csrf_token}")
        print(f"Session Hash: {sessionhash}")
        new_email = await kukulu.create_mailaddress()
        top_mail = await kukulu.check_top_mail(new_email)
        print(f"Title: {top_mail.title}")
        print(f"Text: {top_mail.text}")
        specific_mail = await kukulu.specify_address("@から下")

asyncio.run(main())      