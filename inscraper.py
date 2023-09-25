from modules.scraper import Scraper
from modules import stats
from modules import file_io

username = "<your_username>"
password = "<your_password>"

def main():
    scraper = Scraper()

    if not scraper.authenticate(username, password):
        exit()
    users = scraper.get_users()
    scraper.close()

    print("🔎 Almost done! Doing some maths...")

    #Stats
    diff = stats.diff(users)

    #Save results
    file_io.save(username, users, diff)

    print("\n✅ Done, thanks for using Inscraper!")
    print("🌟 Star the project on GitHub", "\n- https://github.com/alefranzoni/inscraper")

if __name__ == "__main__":
    main()