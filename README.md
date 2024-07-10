[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![Donate][donate-shield]][donate-url]

# Inscraper
**Inscraper** is a simple Instagram tool built with Python that it's able to log in, obtain the followers and followings and get information like who does not follow you and more.

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
As mentioned above, this tool uses Python to do its job. Therefore, you need to have `Python3` ([How to install](https://www.python.org/downloads/)) and `PIP` installed. Additionally, you will also need to have installed a few more libraries.

Finally, as the list of followers/following cannot be obtained or viewed anonymously, i.e. without being logged in to Instagram, you will need to have valid credentials to log in.

## Installation
Download this project manually or clone the repo with git

```bash
git clone https://github.com/alefranzoni/inscraper.git
```

Then install the required dependencies

```bash
pip install cryptography
pip install requests
pip install json
```

## First time: What do I need to know?
As the tool stores cookies locally to save session data, thus avoiding having to log in to your account at each run, it is imperative that this data is protected from prying eyes. To achieve this, the data is encrypted with a unique, personal key. We only need to generate it for the **first and only time** and then save it, either in the default directory or in a secure location.

### How do we generate a new security key?
To generate a new security key, it is as simple as running the script including the `-gk` parameter. This will automatically generate your personal key and store it in the `./data` folder.

```bash
# example - generate new passkey
python3 inscraper.py -gk
```

### Considerations
- If we move the security key to another place, before each execution we must place it in the `./data` folder.
- If we lose the key, we can always generate a new one, but the session data previously protected with the old key will be lost.

## Usage
Just go to the project directory and run `inscraper.py` with Python3. Yeah, piece of cake, right?
 
```bash
cd inscraper
python3 inscraper.py
```
### Options
You also are able to execute the script with some of the following options.

| Command     | Type  | Mandatory | Description                                                                 |
|-------------|-------|-----------|-----------------------------------------------------------------------------|
|`-gk`        |Boolean| -         |Generate a new passkey to protect PII data                                   |
|`-sr`        |String | -         |Show the last report generated for a given user                              |
|`-h`         | -     | -         |Show the help message                                                        |

### Running considerations
- If your account has two-factor auth protection enabled, you'll be asked to input the code.

### Examples
```bash
# Simple execution
python3 inscraper.py

# Run the script, generating a new password key beforehand (only needed once)
python3 inscraper.py -gk

# Show the last report for 'your_username'
python3 inscraper.py -sr "your_username"

```

## Disclaimer
It is important to note that this type of usage carries a risk of your IP or account being blocked for making too many requests in a short period of time. To avoid this type of inconvenience and to protect your account, a limit of **one query per hour** has been set. Therefore, if you use the tool correctly, the probability is very low (if not zero) and you will not have any problems.

Anyway, always remember to use it at **your own risk**. The creator of this script is not responsible for any losses or problems resulting from its use.

## Donate
You can support me through [**Cafecito**](https://cafecito.app/alefranzoni) (🇦🇷) or [**PayPal**](https://www.paypal.com/donate/?hosted_button_id=9LR86UDHEKM3Q) (Worldwide). Thank you ❤️

[stars-shield]: https://img.shields.io/github/stars/alefranzoni/inscraper
[stars-url]: https://github.com/alefranzoni/inscraper/stargazers
[issues-shield]: https://img.shields.io/github/issues/alefranzoni/inscraper
[issues-url]: https://github.com/alefranzoni/inscraper/issues
[donate-shield]: https://img.shields.io/badge/$-donate-ff69b4.svg?maxAge=2592000&amp;style=flat
[donate-url]: https://github.com/alefranzoni/inscraper#donate
