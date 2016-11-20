# coding=utf-8
import tornado.web
import tornado.ioloop
import tornado.websocket
import json
import re
import os
import random
import time
import markdown
import MySQLdb
import lxml.html.clean
import sys
sys.path.append("static/bot")
import weather
import news




class Index(tornado.web.RequestHandler):
    def get(self):
        self.set_cookie('foo', 'bar', httponly=True, secure=True)
        self.set_secure_cookie('foo', 'bar', httponly=True, secure=True)
        self.render('templates/index.html')



class SocketHandler(tornado.websocket.WebSocketHandler):
    clients = set()
    mdict = dict()

    def send_to_all(self,message):
        for c in SocketHandler.clients:
            if id(c) == id(self):
                itisme = {'itisme':1}
                message.update(itisme)
                c.write_message(json.dumps(message))
            else:
                try:
                    del message['itisme']
                except:
                    pass
                c.write_message(json.dumps(message))

    def get_name(self):
        mname_n = {'1':'老虎','2':'狼','3':'仓鼠','4':'麋鹿','5':'猫','6':'猴子',
                '7':'树懒','8':'斑马','9':'哈士奇','10':'狐狸','11':'白熊',
                '12':'大象','13':'豹子','14':'牦牛'}
        mname_adj = {'1':'暖洋洋的','2':'醉醺醺的','3':'香喷喷的','4':'软绵绵的',
                    '5':'沉甸甸的','6':'羞答答的','7':'亮晶晶的','8':'沉甸甸的',
                    '9':'白花花的','10':'绿油油的','11':'黑黝黝的','12':'慢腾腾的',
                    '13':'阴森森的','14':'皱巴巴的'}
        mname = mname_adj[str(random.randint(1,14))]+mname_n[str(random.randint(1,14))]
        if str(id(self)) in SocketHandler.mdict:
            return SocketHandler.mdict[str(id(self))]
        SocketHandler.mdict[str(id(self))]=mname
        return SocketHandler.mdict[str(id(self))]

    def open(self):
        cx = MySQLdb.connect("localhost", "root", "lyx15&lyx", "chat")
        cursor = cx.cursor()
        user_agent = self.request.headers['user-agent'].replace("\'","|")
        ip = self.request.headers.get("X-Real-IP")
        cursor.execute("insert into online (id,ip,user_agent) values (%d,'%s','%s')"%(id(self),ip,user_agent))
        cursor.close()
        cx.commit()
        cx.close()
        mname = SocketHandler.get_name(self)
        SocketHandler.clients.add(self)
        self.write_message(json.dumps({
            'type': 'sys',
            'id':id(self),
            'person':len(SocketHandler.clients),
            'message': 'Welcome to WebSocket',
        }))
        self.write_message(json.dumps({
            'type': 'bot',
            'time':time.strftime("%H:%M:%S", time.localtime()),
            'id':id(self)+12138,
            'name': 'Master robot',
            'messageType':3,
            'message': "欢迎!我是这里的机器人,管理着这个聊天室<br>如果你是第一次来到这里，发送\\help获取使用帮助",
        }))
        SocketHandler.send_to_all(self,{
            'type': 'sys',
            'person':len(SocketHandler.clients),
            'message': mname + ' has joined',
        })


    def on_close(self):
        cx = MySQLdb.connect("localhost", "root", "lyx15&lyx", "chat")
        cursor = cx.cursor()
        user_agent = self.request.headers['user-agent'].replace("\'","|")
        ip = self.request.headers.get("X-Real-IP")
        try:
            cursor.execute("delete from online where id = %d"%(id(self)))
        except:
            pass
        cursor.execute("insert into offline (id,ip,user_agent) values (%d,'%s','%s')"%(id(self),ip,user_agent))
        cursor.close()
        cx.commit()
        cx.close()
        mname = SocketHandler.get_name(self)
        SocketHandler.clients.remove(self)
        SocketHandler.send_to_all(self,{
            'type': 'sys',
            'person':len(SocketHandler.clients),
            'message': mname + ' has left',
        })

    def on_message(self, message):
        mname = SocketHandler.get_name(self)
        if re.search('^```.*```', str(message).encode('utf-8'),re.S):
            SocketHandler.send_to_all(self,{
                'type': 'user',
                'time':time.strftime("%H:%M:%S", time.localtime()),
                'id':id(self),
                'name': mname,
                'messageType':1,
                'message': markdown.markdown(message,
                                             extensions=['markdown.extensions.extra',
                                                         'markdown.extensions.codehilite']),
            })
        elif re.search('^\$\$.*\$\$$',str(message).encode('utf-8'),re.S):

            message = '<img src="https://l.wordpress.com/latex.php?bg=ffffff&fg=000000&s=0&latex={0}" style="border:none;">'.format(message[2:-2])
            SocketHandler.send_to_all(self,{
                'type': 'user',
                'time':time.strftime("%H:%M:%S", time.localtime()),
                'id':id(self),
                'name': mname,
                'messageType':2,
                'message': message,
            })
        elif re.search('^\\\weather',str(message).encode('utf-8'),re.S):
            try:
                local = message[message.index(' ')+1:]
            except:
                local='chongqing'
            message_bot = weather.getweather(local).replace('\n','<br>')
            SocketHandler.send_to_all(self,{
                'type': 'user',
                'time':time.strftime("%H:%M:%S", time.localtime()),
                'id':id(self),
                'name': mname,
                'messageType':3,
                'message': message,
            })
            SocketHandler.send_to_all(self,{
                'type': 'bot',
                'time':time.strftime("%H:%M:%S", time.localtime()),
                'id':id(self)+12138,
                'name': 'Weather robot',
                'messageType':3,
                'message': "%s's weather：<br>"%(local)+message_bot,
            })
        elif re.search('^\\\\news',str(message).encode('utf-8'),re.S):
            message_bot = news.getnews().replace('\n','<br>')
            SocketHandler.send_to_all(self,{
                'type': 'user',
                'time':time.strftime("%H:%M:%S", time.localtime()),
                'id':id(self),
                'name': mname,
                'messageType':3,
                'message': message,
            })
            SocketHandler.send_to_all(self,{
                'type': 'bot',
                'time':time.strftime("%H:%M:%S", time.localtime()),
                'id':id(self)+12138,
                'name': 'News robot',
                'messageType':3,
                'message': 'Today News：<br>'+message_bot,
            })
        elif re.search('^\\\help',str(message).encode('utf-8'),re.S):
            self.write_message(json.dumps({
                'type': 'user',
                'time':time.strftime("%H:%M:%S", time.localtime()),
                'id':id(self),
                'itisme':1,
                'name': mname,
                'messageType':3,
                'message': message,
            }))
            self.write_message(json.dumps({
                'type': 'bot',
                'time':time.strftime("%H:%M:%S", time.localtime()),
                'id':id(self)+12138,
                'name': 'Master robot',
                'messageType':3,
                'message': '''使用帮助:<br>本聊天室支持markdown语法发送代码<br>example:
                                <br>```python<br>print('Hello world!')<br>```
                                <br>支持使用LaTeX语法发送公式<br>example:<br>$$h = \\frac{1}{2}gt^2$$
                                <br>支持使用\\weather 地点(拼音)查看天气<br>支持使用\\news查看新闻''',
            }))
        elif message == 'c93c60882b37254bb13e80183f291af3':
            pass
        else:
            message = message.replace('\n','<br>')
            cleaner = lxml.html.clean.Cleaner(style=True, scripts=True, page_structure=False, safe_attrs_only=False)
            message = cleaner.clean_html(message)
            SocketHandler.send_to_all(self,{
                'type': 'user',
                'time':time.strftime("%H:%M:%S", time.localtime()),
                'id':id(self),
                'name': mname,
                'messageType':3,
                'message': message,
            })


if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf8')
    settings = dict(
        static_path = os.path.join(os.path.dirname(__file__), "static"),
    )
    settings = {
        "cookie_secret": "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
        "xsrf_cookies": True,
    }
    app = tornado.web.Application([
        ('/', Index),
        ('/soc', SocketHandler),
    ],**settings
    )
    app.listen(7001,address='0.0.0.0')
    tornado.ioloop.IOLoop.instance().start()
