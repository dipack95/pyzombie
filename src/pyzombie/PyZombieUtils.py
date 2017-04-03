import requests
import random
import time
import logging
import loremipsum as loi
import validators
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup as bs

import src.pyzombie.PersonalConfig as pc

logger = logging.getLogger(__name__)


class Categories:
    Mail = 'mail'
    News = 'news'
    Education = 'education'
    MessageBoard = 'message-board'
    Entertainment = 'entertainment'
    Corporate = 'corporate'
    Software = 'software'


class Websites:
    websites = [
        {
            'name': 'New York Times',
            'url': 'https://nytimes.com',
            'categories': [Categories.News, Categories.Education]
        },
        {
            'name': 'Gmail',
            'url': 'https://gmail.com',
            'categories': [Categories.Mail]
        },
        {
            'name': 'Yahoo! Answers',
            'url': 'https://answers.yahoo.com/',
            'categories': [Categories.Education, Categories.MessageBoard]
        },
        {
            'name': 'Reddit',
            'url': 'https://www.reddit.com/',
            'categories': [Categories.MessageBoard, Categories.News]
        },
        {
            'name': 'YouTube',
            'url': 'https://www.youtube.com/',
            'categories': [Categories.Entertainment]
        },
        {
            'name': 'Rakuten',
            'url': 'https://global.rakuten.com/corp/worldwide/',
            'categories': [Categories.Corporate]
        },
        {
            'name': 'Zhihu',
            'url': 'https://www.zhihu.com/',
            'categories': [Categories.MessageBoard]
        },
        {
            'name': 'FC2',
            'url': 'https://fc2.com/',
            'categories': [Categories.Entertainment]
        }
    ]


class PyZombieUtils:
    LoiGen = None

    def __init__(self):
        logging.basicConfig(format='[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p',
                            level=logging.INFO)
        with open('../../resources/words/words2.txt') as dictionary_text:
            dictionary = dictionary_text.read().split()
        self.LoiGen = loi.Generator(sample="The quick brown fox jumps over the lazy dog", dictionary=dictionary)

    @staticmethod
    def check_internet_connection():
        response = requests.get("http://www.google.com")
        return (response.status_code == 200)

    def check_if_url_is_relative(self, url):
        return bool(urlparse(url).netloc)

    def get_all_links(self, url):
        if not self.check_internet_connection():
            logger.error("No internet connection!")
            return []
        response = requests.get(url)
        links = bs(response.content, 'lxml').find_all('a')
        actualLinks = []
        for link in links:
            href = link.get('href')
            if not self.check_if_url_is_relative(url=href):
                href = urljoin(url, href)
            if validators.url(href):
                actualLinks.append(href)
        return actualLinks

    def visit_links_on_site(self, url, linksToVisit=10, timeToLinger=1):
        if not self.check_internet_connection():
            logger.error("No internet connection!")
            return
        actualLinks = self.get_all_links(url=url)
        try:
            for _ in range(linksToVisit):
                choice = random.choice(actualLinks)
                logger.info("Visiting: %s" % choice)
                response = requests.get(choice)
                if response.status_code == 200:
                    logger.debug("Successfully visited %s" % choice)
                else:
                    logger.warning("Could not hit %s" % choice)
                if not self.roll_dice_to_continue():
                    logger.info("Aborting the rest of our journey on these seas!")
                    return
                time.sleep(timeToLinger)
        except IndexError:
            logger.error("No links found at %s" % url)
            return
        return

    def send_email(self, user, pwd, recipient, subject, body):
        import smtplib

        gmail_user = user
        gmail_pwd = pwd
        FROM = user
        TO = recipient if type(recipient) is list else [recipient]
        SUBJECT = subject
        TEXT = body

        # Prepare actual message
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s
        """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.ehlo()
            server.starttls()
            server.login(gmail_user, gmail_pwd)
            server.sendmail(FROM, TO, message)
            server.close()
            logger.info('Successfully sent the mail')
        except:
            logger.error("Failed to send mail")
        return

    def random_action_generator(self, seed=100):
        actions = [self.send_email, self.visit_links_on_site]
        random.seed(seed)
        choice = random.choice(actions)
        logger.info("Running %s" % choice)
        choice()
        return

    def random_sentence_generator(self, amount=1, generate_paragraphs=False):
        if not generate_paragraphs:
            generated = self.LoiGen.generate_sentences(amount=amount)
        else:
            generated = self.LoiGen.generate_paragraphs(amount=amount)
        generatedData = generated.__next__()[2]
        logger.info("Generated %s" % generatedData)
        return

    def roll_dice_to_continue(self, numberOfDice=10):
        shallWeContinue = (abs(random.randrange(numberOfDice) - random.randrange(numberOfDice)) % 2)
        logger.info("Rolled a %s" % shallWeContinue)
        return shallWeContinue

    def real_action(self):
        site = random.choice(Websites.websites)
        logger.info("Where are we going next? To %s" % site)
        if Categories.Mail in site['categories']:
            logger.info("Will send email!")
            # self.send_email(pc.PersonalConfig.Email, pc.PersonalConfig.Password, pc.PersonalConfig.ToEmail, "Test subject",
            #                 "Test body")
        else:
            self.visit_links_on_site(url=site['url'], linksToVisit=random.randrange(10))


if __name__ == '__main__':
    pyz = PyZombieUtils()
    while 1:
        pyz.real_action()
