[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![Donate][donate-shield]][donate-url]

# Inscraper
**Inscraper** is a simple Instagram web scraper built with Python and [Playwright](https://github.com/microsoft/playwright). It's able to log in, scrape the followers and followings and get information like who does not follow you and more. 

## Contents
- [Requirements](#requirements)
- [Installation](#installation)
- [First time: What do I need to know?](#first-time-what-do-i-need-to-know)
  - [How do we generate a new security key?](#how-do-we-generate-a-new-security-key)
  - [Considerations](#considerations)
- [Usage](#usage)
  - [Options](#options)
  - [Running considerations](#running-considerations)
  - [Examples](#examples)
- [Disclaimer](#disclaimer)
- [Donate](#donate)

## Requirements
As mentioned above, this tool uses Python and Playwright to do its job. Therefore, you need to have `Python3` ([How to install](https://www.python.org/downloads/)) and `PIP` installed. Additionally, you will also need to have `Playwright` installed and a few more libraries.

Finally, as the list of followers/following cannot be opened or viewed anonymously, i.e. without being logged in to Instagram, you will need to have valid credentials to log in.

## Installation
Download this project manually or clone the repo with git

```bash
git clone https://github.com/alefranzoni/inscraper.git
```

Then install the required dependencies

```bash
pip install playwright
playwright install
pip install cryptography
pip install requests
pip install json
```

## First time: What do I need to know?
As the tool stores cookies locally to save session data, thus avoiding having to log in to your account at each run, it is imperative that this data is protected from prying eyes. To achieve this, the data is encrypted with a unique, personal key. We only need to generate it for the **first and only time** and then save it, either in the default directory or in a secure location.

### How do we generate a new security key?
To generate a new security key, it is as simple as running the script with the desired options and including the `-gk` argument. This will automatically generate your personal key and store it in the `./data` folder.

```bash
# example - generate new passkey
python3 inscraper.py -gk
```

### Considerations
- If we move the security key to another place, before each execution we must place it in the `./data` folder.
- If we lose the key, we can always generate a new one, but the session data previously protected with the old key will be lost.

## Usage
After installing the dependencies and generating the security key, go to the project directory and run the `inscraper.py` with Python3
 
```bash
cd inscraper
python3 inscraper.py [OPTIONS]
```
### Options
You can also customize the script execution by adding any (or all) of the following available commands.

| Command     | Type  | Mandatory | Description                                                         |
|-------------|-------|-----------|---------------------------------------------------------------------|
|`-al`        |Boolean| -         |Ask for user credentials, ignoring the default ones. Default: False  |
|`-sd`        |Float  | -         |Adds a delay (in seconds) to the scrolling process. Default: 0.5     |
|`-sr`        |Int    | -         |Adds attempts to the scrolling process. Default: 5                   |
|`-gk`        |Boolean| -         |Generate a new passkey to protect PII data                           |
|`-h`         | -     | -         |Show the help message                                                |

> Note that the delay or retries options are similar and **do not** replace the default values, but are added to them. In slow connections, we can increase one or both of these values. Remember that setting very high values for either of these two options will cause the required processing times to be longer.

### Running considerations
- If you run `inscraper.py` without passing it any arguments, remember that you'll need to edit the credentials within the file in order to successful login.
- If your account has two-factor auth protection enabled, you'll be asked to input the code.

### Examples
```bash
# Without passing it any args
python3 inscraper.py
# Just asking for credentials to login
python3 inscraper.py -al
# Passing it all the args
python3 inscraper.py -al -sd 0.3 -sd 1

```

## Disclaimer
It is important to note that this type of usage carries a risk of your IP or account being blocked for making too many requests in a short period of time. To avoid this type of inconvenience and to protect your account, a limit of one query per hour has been set. Therefore, if you use the tool correctly, the probability is very low and you will not have any problems.

Anyway, always remember to use it at **your own risk**. The creator of this script is not responsible for any losses or problems resulting from its use.

## Donate
You can support me through [**Cafecito**](https://cafecito.app/alefranzoni) (🇦🇷) or [**PayPal**](https://www.paypal.com/donate/?hosted_button_id=9LR86UDHEKM3Q) (Worldwide). Thank you ❤️

[stars-shield]: https://img.shields.io/github/stars/alefranzoni/inscraper
[stars-url]: https://github.com/alefranzoni/inscraper/stargazers
[issues-shield]: https://img.shields.io/github/issues/alefranzoni/inscraper
[issues-url]: https://github.com/alefranzoni/inscraper/issues
[donate-shield]: https://img.shields.io/badge/$-donate-ff69b4.svg?maxAge=2592000&amp;style=flat
[donate-url]: https://github.com/alefranzoni/inscraper#donate
