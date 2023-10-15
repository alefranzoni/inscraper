from modules.scraper import Scraper
from modules.argument_manager import ArgumentManager, ArgumentOptions
from modules import stats
from modules import file_io
from getpass import getpass

username = "<your_username>"
password = "<your_password>"

def main():
    global username
    global password
    args = ArgumentManager()
    scraper = Scraper(arguments=args)

    # Login
    if args.get(ArgumentOptions.ASK_LOGIN):
        print("🔐 Account credentials is required")
        username = input("🔑 Enter username: ")
        print("🔑 ", end="", flush=True)
        password = getpass("Enter password: ")

    if not scraper.authenticate(username, password):
        exit()

    # Get data
    users = scraper.get_users()
    scraper.close()

    print("🔎 Almost done! Doing some maths...")

    # Stats
    diff = stats.diff(users)

    # Save results
    file_io.save(username, users, diff)

    print("\n✅ Done, thanks for using Inscraper!")
    print("🌟 Star the project on GitHub", "\n- https://github.com/alefranzoni/inscraper")

if __name__ == "__main__":
    main()