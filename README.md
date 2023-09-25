[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![Donate][donate-shield]][donate-url]

# Inscraper
**Inscraper** is a simple Instagram web scraper built with Python and Playwright. It's able to log in, scrape the followers and followings and get information like who does not follow you and more. 

## Contents
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Disclaimer](#disclaimer)
- [Donate](#donate)

## Requirements
As mentioned above, this tool uses Python and Playwright to do its job. Therefore, you need to have `Python3` and `PIP` installed.  Additionally, you will also need to have `Playwright` installed.

Finally, as the list of followers/following cannot be opened or viewed anonymously, i.e. without being logged in to Instagram, you will need to have valid credentials to log in.

## Installation
Download this project manually or clone the repo with git

```bash
git clone git@github.com:alefranzoni/inscraper.git
```

Then install the required dependencies

```bash
pip install playwright
playwright install
```

## Usage
After installing the dependencies, you'll to edit the `inscraper.py` file putting your Instagram credentials

```py
username = "<your_username>"
password = "<your_password>"
```

Now, go to the project directory and run the `inscraper.py` with Python3

```bash
cd inscraper
python3 inscraper.py
```

#### Considerations
- If your account has two-factor auth protection enabled, you'll be asked to input the code.
- The full report generated with your data will be stored in the `reports` folder. 

## Disclaimer
This tool will not jeopardize your account at all, but you should know that if you use it too many times in a short period of time, Instagram will proceed to perform a "soft block" of the list of followers of your account and, therefore, you will not be able to view it. 

This blocking is always temporary, usually lasting from a few hours to a maximum of 24 hours. If you use this tool correctly, there will be no problem with your account, but use it at **your own risk**.

## Donate
You can support me through [**Cafecito**](https://cafecito.app/alefranzoni) (🇦🇷) or [**PayPal**](https://www.paypal.com/donate/?hosted_button_id=9LR86UDHEKM3Q) (Worldwide). Thank you ❤️

[stars-shield]: https://img.shields.io/github/stars/alefranzoni/inscraper
[stars-url]: https://github.com/alefranzoni/inscraper/stargazers
[issues-shield]: https://img.shields.io/github/issues/alefranzoni/inscraper
[issues-url]: https://github.com/alefranzoni/inscraper/issues
[donate-shield]: https://img.shields.io/badge/$-donate-ff69b4.svg?maxAge=2592000&amp;style=flat
[donate-url]: https://github.com/alefranzoni/inscraper#donate
