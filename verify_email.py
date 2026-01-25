import asyncio
from Site.backend.auth.email import send_email

async def main():
    print("Sending test email...")
    success = await send_email("hj@holy-coder.ru", "123456")
    if success:
        print("Test email sent successfully!")
    else:
        print("Failed to send test email.")

if __name__ == "__main__":
    asyncio.run(main())
