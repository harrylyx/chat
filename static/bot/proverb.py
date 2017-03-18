#coding=utf-8

import urllib2
from bs4 import BeautifulSoup
import sys
import random
import MySQLdb
import chardet
import time


def getContent(url,headers):  
    """ 
    此函数用于抓取返回403禁止访问的网页 
    """  
    random_header = random.choice(headers)  
  
    """ 
    对于Request中的第二个参数headers，它是字典型参数，所以在传入时 
    也可以直接将个字典传入，字典中就是下面元组的键值对应 
    """  
    req =urllib2.Request(url)  
    req.add_header("User-Agent", random_header)  
    req.add_header("GET",url)  
    req.add_header("Host","www.juzimi.com")  
  
    content=urllib2.urlopen(req).read()
    mychar = chardet.detect(content)  
    bianma = mychar['encoding']  
    if bianma == 'utf-8' or bianma == 'UTF-8':  
        html = content
    else :  
        html = content.decode('gb2312','ignore').encode('utf-8')  
    return html

def proverb(url,mid):
    cx = MySQLdb.connect(host="localhost", user = "root", passwd = "lyx15&lyx", db = "chat", charset = "utf8")
    cx.set_character_set('utf8')
    cursor = cx.cursor()
    reload(sys)
    sys.setdefaultencoding('utf8')
    header = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
    content = getContent(url, header)
    soup = BeautifulSoup(content,"lxml")
    result = ''
    r = ''
    for child in soup.find_all('a'):
        if child.attrs.get("class") == ['xlistju']:
            content = child.get_text().encode('utf-8')
        elif child.attrs.get("class") == ['views-field-field-oriwriter-value']:
            author = child.get_text().encode('utf-8')
            cursor.execute("insert into proverb (id, content, author) values (%d,'%s','%s')"%(mid,content.encode('utf-8'),author.encode('utf-8')))
            mid += 1
    cursor.close()
    cx.commit()
    cx.close()
    
    
if __name__ == "__main__":
    mid = 0
    for i in range(1,27,1):
        url = 'http://www.juzimi.com/album/118685?page='
        url = url + str(i)
        print url
        proverb(url,mid)
        mid += 12
        #time.sleep(5)

