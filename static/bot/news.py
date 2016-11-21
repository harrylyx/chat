#coding=utf-8

import urllib2
from bs4 import BeautifulSoup
import sys


def getnews():
    reload(sys)
    sys.setdefaultencoding('utf8')
    content = urllib2.urlopen('http://www.news.cn/world/index.htm').read()
    soup = BeautifulSoup(content,"lxml")
    a = 0
    result = ''
    for child in soup.find_all('h3'):
        if a >= 5 and a <= 15:
            result += str(child)+'\n'
        a+=1
    result = result.replace('<h3>','')
    return result.replace('</h3>','')

if __name__ == "__main__":
    getnews()
