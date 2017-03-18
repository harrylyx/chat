# coding=utf-8

import urllib

false = 0
url = "http://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US"
pic_req = urllib2.Request(url)
pic_eval = urllib2.urlopen(pic_req).read()
pic_url = eval(pic_eval)['images'][0]['url']
url = 'http://s.cn.bing.net'+pic_url
local="../images/bg-main.jpg"
urllib.urlretrieve(url,local)