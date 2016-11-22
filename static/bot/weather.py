#coding=utf-8

import urllib2
from bs4 import BeautifulSoup
import sys


def getweather(local):
    reload(sys)
    sys.setdefaultencoding('utf8')
    try:
        content = urllib2.urlopen('http://m.cncn.com/tianqi/%s'%(local)).read()
    except:
        content = urllib2.urlopen('http://m.cncn.com/tianqi/%s'%('bj')).read()
    soup = BeautifulSoup(content,"lxml")
    r = ''
    for child in soup.find_all('ul'):
        if child.attrs.get("class") == ['w_list']:
            s = child.get_text()
            r = r + s.encode('utf-8')
    r = r.replace('\n\n','')
    r = r.replace('℃\n','℃\n\n')
    a = r.index('℃',r.index('℃')+4)
    return r[0:a+4]


if __name__ == "__main__":
    getweather('chongqing')
