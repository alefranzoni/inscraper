from getpass import getpass
from modules.argument_manager import ArgumentManager, ArgumentOptions
from modules.scraper import Scraper
from modules.session_utils import handle_security_key

username = "<your_username>"
password = "<your_password>"

def main():
    global username
    global password

    args = ArgumentManager()
    handle_security_key(generate_key_arg=args.get(ArgumentOptions.GENERATE_KEY))
    scraper = Scraper(arguments=args)
    credentials_needed = username == "<your_username>" or password == "<your_password>"
    if args.get(ArgumentOptions.ASK_LOGIN) or credentials_needed:
        print("🔐 Account credentials is required")
        username = input("🔑 Enter username: ")
        print("🔑 ", end="", flush=True)
        password = getpass("Enter password: ")
    scraper.authenticate(username, password)
    scraper.get_groups()
    scraper.close()
    print("✅ Done, thanks for using Inscraper!")
    print("🌟 Star the project on GitHub", "\n- https://github.com/alefranzoni/inscraper")

if __name__ == "__main__":
    main()
