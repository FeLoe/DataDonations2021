#!/usr/bin/env python3
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import WebDriverException 
import time
import dateparser
import re
from langdetect import detect
import json
import datetime
from sys import argv

from urllib.parse import urlparse
from urllib.parse import parse_qs



class Whatsapp():
    '''A WhatsApp scraper without a proper docstring'''
    def __init__(self, geckopath=None):
        if geckopath:
            self.browser = webdriver.Firefox(executable_path = geckopath)
        else:
            try:
                self.browser = webdriver.Firefox()
            except WebDriverException:
                print("Geckodriver not found. Either copy the geckodriver to your path or specify its location")
                raise
        self.browser.get("https://web.whatsapp.com/")

    
    def scrape_links(self):
        '''Yields the *links* per chat that are shared in the Whatsapp scraper instance'''

        #Get all the chats, sort them by date to know which one is first/last and save it into a list
        chats = []
        names = []
        n = 0
        maintext = self.browser.find_element_by_xpath('//h1').text
        language = detect(maintext)
        while True:
            #Get language
            #Get names of chats
            a = self.browser.find_elements_by_xpath("//div[@id='pane-side']//span[@title and @dir='auto']")
            new_chats = []
            for item in a:
                try: 
                    #Get date of chat (two different options depending on whether it is a date/time)
                    try: 
                        x = item.find_element_by_xpath('../following-sibling::div')
                    except:
                        x = item.find_element_by_xpath('../../following-sibling::div')
                except:
                    pass
                #Parse the date (is done automatically)
                try:
                    parsed_date = dateparser.parse(x.text, settings={'DATE_ORDER': 'DMY'})
                except:
                    parsed_date = ""
                #Put all the info (xpath element, name of chat, date) in one list
                try:    
                    new_chats.append((item, item.text, parsed_date))
                except:
                    pass
            #Sort by date, only keep the new chats
            new_chats.sort(key = lambda x: x[2], reverse = True)
            new_chats = [x for x in new_chats if x not in chats]
            new_chats.sort(key = lambda x: x[2], reverse = True)
            new_names = [x[1] for x in new_chats]

            #For every chat get all the links (including who sent them when)

            for c in new_chats: 
                links = []
                c[0].click()
                try: 
                    x = self.browser.find_element_by_xpath("//div[@id = 'main']/header/div/div/img")
                except:
                    x = self.browser.find_element_by_xpath("//div[@id = 'main']/header//*[@dir = 'auto']")
                x.click()
                time.sleep(2)
                if language == 'de':
                    linktext = self.browser.find_element_by_xpath("//*[text() = 'Medien, Links und Dokumente']")
                elif language == 'nl':
                    linktext = self.browser.find_element_by_xpath("//*[text() = 'Media, links en documenten']")  # was "en docs", maar dat klopt iig bij mij niet
                elif language == 'en':
                    linktext = self.browser.find_element_by_xpath("//*[text() = 'Media, Links and Docs']")
                else: 
                    print('language not supported')
                    self.browser.quit()
                linktext.click()
                time.sleep(2)
                linktext2 = self.browser.find_element_by_xpath("//*[text() = 'Links']")
                linktext2.click()
                time.sleep(5)
                #Get all of the links, difference between inlinks (other people writing) and outlinks (own messages)
                while True: 
                    inlinks = self.browser.find_elements_by_xpath("//*[@data-list-scroll-container = 'true']//*[contains(@class,'message-in')]//a")
                    outlinks = self.browser.find_elements_by_xpath("//*[@data-list-scroll-container = 'true']//*[contains(@class,'message-out')]//a")
                    #Scroll to get all the links
                    if not inlinks:
                        newlinks_in = []
                    else: 
                        last_link_in = inlinks[-1]
                        self.browser.execute_script("arguments[0].scrollIntoView();", last_link_in)
                        time.sleep(2)
                        newlinks_in = self.browser.find_elements_by_xpath("//*[@data-list-scroll-container = 'true']//*[contains(@class,'message-in')]//a")
                    if not outlinks:
                        newlinks_out = []
                    else:
                        last_link_out = outlinks[-1]
                        self.browser.execute_script("arguments[0].scrollIntoView();", last_link_out)
                        time.sleep(2)
                        newlinks_out = self.browser.find_elements_by_xpath("//*[@data-list-scroll-container = 'true']//*[contains(@class,'message-out')]//a")
                    if (set(newlinks_in).issubset(inlinks)) and (set(newlinks_out).issubset(outlinks)):
                            break
                time.sleep(2)
                #Get message around link and sender (if from group)
                messages_in = []
                messages_out = []
                for link in inlinks: 
                    link_final = link.get_attribute('href')
                    link_final = anonymize_url(link_final, origin = 'in')
                    text = link.find_elements_by_xpath('..')
                    text = [re.sub(r'@\d+', '', t.text) for t in text]
                    sender = link.find_elements_by_xpath('../../../../preceding-sibling::div/span[@dir = "auto"]|../preceding-sibling::div/div/span[@dir = "auto"]')
                    sender = [hash(s.text) for s in sender]
                    message = {"link":link_final, "text":text, "sender":sender}
                    messages_in.append(message)
                for link in outlinks:
                    link_final = link.get_attribute('href')
                    link_final = anonymize_url(link_final, origin = 'out')
                    text = link.find_elements_by_xpath('..')
                    text = [re.sub(r'@\d+', '', t.text) for t in text]
                    message = {"link":link_final, "text":text}
                    messages_out.append(message)
                yield {'chatname':hash(c[1]), "date":c[2], "messages_in":messages_in, "messages_out":messages_out}

            #Scroll down to get the next group of chats
            if n == 0:
                chats = new_chats
                names = new_names
                for i in range(-1, (-len(new_chats)-1), -1):
                    try:
                        self.browser.execute_script("arguments[0].scrollIntoView();", new_chats[i][0])
                        time.sleep(2)
                        break
                    except:
                        pass
            else:
                if set(new_names).issubset(names):
                    break
                else:
                    chats.extend(x for x in new_chats if x not in chats)
                    chats.sort(key = lambda x: x[2], reverse = True)
                    names = [x[1] for x in chats]
                    for i in range(-1, (-len(new_chats)-1), -1):
                        try:
                            self.browser.execute_script("arguments[0].scrollIntoView();", new_chats[i][0])
                            time.sleep(2)
                            break
                        except:
                            pass
            n += 1
            if n == 1:
                break
        self.browser.quit()



def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

def anonymize_url(link, origin):
    base = urlparse(link)
    stripped_link = base.scheme + '://' + base.netloc + base.path
    queries = parse_qs(base.query)
    #Get search queries from search engines (Google, Bing, Yahoo, DuckDuckGo, Ecosia), Youtube and large Dutch media providers
    queries_keep = {k: v for k, v in queries.items() if k in ['v', 'q', 'p', 's', 'query', 'keyword', 'term']}
    return({"link":stripped_link, "query":queries_keep})

    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--geckopath", help="Path to your gecko driver (necessary if not in $PATH)")
    parser.add_argument("--output", help="File to store the output")
    args = parser.parse_args()

    #Get website, allow 15 seconds to scan the QR code
    myscraper = Whatsapp(geckopath=args.geckopath)
    time.sleep(15)
    #then blur the page
    self.browser.execute_script("document.getElementsByTagName('body')[0].style.filter = 'blur(30px)';")


        
    if args.output:
        filename = args.output
    else:
        filename = "output.json"

    with open(filename, 'w') as fout:
        for i, chatlinks in enumerate(myscraper.scrape_links()):
            print(f"Scraped links from chat number {i}...")
            fout.write(json.dumps(chatlinks, default = myconverter))
            fout.write('\n')


    print(f"Done. All links saved to {filename}")

    


