# coding=utf-8
import tornado.web
import tornado.ioloop
import sys
import os
import urllib
import urllib2
import MySQLdb
import json

class Index(tornado.web.RequestHandler):
    def get(self):
        self.set_cookie('foo', 'bar', httponly=True, secure=True)
        self.set_secure_cookie('foo', 'bar', httponly=True, secure=True)
        self.render('templates/kaoyan.html')


class Pic(tornado.web.RequestHandler):
    def get(self):
        false = 0
        url = "http://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US"
        pic_req = urllib2.Request(url)
        pic_eval = urllib2.urlopen(pic_req).read()
        pic_url = eval(pic_eval)['images'][0]['url']
        self.write('http://s.cn.bing.net'+pic_url)


class Proverb(tornado.web.RequestHandler):
    def get(self, num):
        values = ''
        cx = MySQLdb.connect(host="localhost", user = "root", passwd = "lyx15&lyx", db = "chat", charset = "utf8")
        cx.set_character_set('utf8')
        cursor = cx.cursor()
        cursor.execute('select * from proverb where id = %d'%(int(num))
        values = cursor.fetchall()
        values = values.decode('raw_unicode_escape')
        self.write(json.dumps({'today': values}, ensure_ascii=False))


if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf8')
    # settings = dict(
    #     static_path = os.path.join(os.path.dirname(__file__), "static"),
    # )
    settings = {
        # "static_path": os.path.join(os.path.dirname(__file__), "static"),
        "cookie_secret": "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
        "xsrf_cookies": True,
    }
    app = tornado.web.Application([
        ('/', Index),
        ('/pic', Pic),
        (r"/proverb/(\w+)", Proverb),
    ],**settings
    )
    app.listen(6666,address='0.0.0.0')
    tornado.ioloop.IOLoop.instance().start()