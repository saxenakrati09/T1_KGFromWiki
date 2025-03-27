#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 18:06:25 2021

@author: kratisaxena
"""
'''
import subprocess

status, output = subprocess.getstatusoutput("curl -d \"&pages=Main_Page&offset=1&action=submit\" https://en.wikipedia.org/wiki/Leo_Tolstoy -o \"leo_tolstoy.xml\"")

'''

'''
import webbrowser

webbrowser.open("https://en.wikipedia.org/w/index.php?title=Leo_Tolstoy&pages=XXXX&offset=1&limit=5&action=submit")
'''

import requests
from bs4 import BeautifulSoup
import os



import time
start_time = time.time()



def create_xml(article_):
    url = "https://en.wikipedia.org/w/index.php?title=" + article_ + "&pages=XXXX&offset=1&limit=5&action=submit"

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    xml_ = soup.textarea
    xml_text = str(xml_)

    with open(os.path.join(article_, article_ + ".xml"), "w") as f:
        f.write(xml_text)
    print("saving article's xml")
    ## Template
    link_list = []
    for link in soup.find_all('a', href=True):
        if "/wiki/Template:" in link['href']:
            link_list.append(link['href'])

    for links in link_list:
        template_ = links.split("/")[-1]

        url = "https://en.wikipedia.org/w/index.php?title=" + template_ + "&pages=XXXX&offset=1&limit=5&action=submit"

        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        xml_ = soup.textarea
        xml_text = str(xml_)
        if "Template:" in template_:
            if "aria-label=\"Wikitext source editor\"" in xml_text and "*" in xml_text:
                print(template_)
                with open(os.path.join(article_, template_ + ".xml"), "w") as f:
                    f.write(xml_text)
    print("saved template xmls")



if __name__=="__main__":
    article_ = "Tesla,_Inc."
    print(article_)
    if not os.path.exists(article_):
        os.makedirs(article_)
    print("Created folder")

    create_xml(article_)
    print("Runtime: --- %s seconds ---" % (time.time() - start_time))
