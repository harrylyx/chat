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
    online_ip_agent = []

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
        try:
            user_agent = self.request.headers['user-agent'].replace("\'","|")
        except:
            user_agent = 'Null'
        ip = self.request.headers.get("X-Real-IP")
        cx = MySQLdb.connect("localhost", "chat", "chat123", "chat")
        cursor = cx.cursor()
        try:
            cursor.execute('select ip from blacklist')
            values = cursor.fetchall()  # 获取查询的值
        except:
            values=()
        ip_c = tuple("'"+str(ip)+"'"+',')
        timenow = time.strftime("%H:%M:%S", time.localtime())
        if ip_c in values:
            self.write_message(json.dumps({
                'type': 'bot',
                'time':timenow,
                'id':id(self)+12138,
                'name': 'Master robot',
                'messageType':3,
                'message': '''欢迎你成功进入黑名单!
                           <br>喊你乱搞，你已经被禁止进入了,哼!''',
            }))
            cursor.close()
            cx.commit()
            cx.close()
            super(self).on_close()
        else:
            cursor.execute("insert into online (id,ip,user_agent,time) values (%d,'%s','%s','%s')"%(id(self),ip,user_agent,timenow))
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
                'time':timenow,
                'id':id(self)+12138,
                'name': 'Master robot',
                'messageType':3,
                'message': '''欢迎你,%s!
                           <br>我是这里的机器人,管理着这个聊天室
                           <br>如果你是第一次来到这里，可以发送<strong>/help</strong>获取使用帮助
                           <br>不要乱搞哦，我会看着你的.
                           <br>如果有什么建议，欢迎使用<strong>/feedback 内容</strong>给我反馈,我会帮你转告的.^_^'''%(mname),
            }))
            SocketHandler.send_to_all(self,{
                'type': 'sys',
                'person':len(SocketHandler.clients),
                'message': mname + ' has joined',
            })

    def on_close(self):
        user_agent = self.request.headers['user-agent'].replace("\'","|")
        ip = self.request.headers.get("X-Real-IP")
        cx = MySQLdb.connect("localhost", "chat", "chat123", "chat")
        cursor = cx.cursor()
        timenow = time.strftime("%H:%M:%S", time.localtime())
        try:
            cursor.execute("delete from online where id = %d"%(id(self)))
        except:
            pass
        cursor.execute("insert into offline (id,ip,user_agent,time) values (%d,'%s','%s','%s')"%(id(self),ip,user_agent,timenow))
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
            message=markdown.markdown(message,extensions=['markdown.extensions.extra','markdown.extensions.codehilite'])
            message_json=SocketHandler.get_json(self,'user',id(self),0,mname,1,message)
            SocketHandler.send_to_all(self,message_json)
        elif re.search('^\$\$.*\$\$',str(message).encode('utf-8'),re.S):
            message = message.strip()
            message = '<img src="https://latex.codecogs.com/gif.latex?{0}" style="border:none;">'.format(message[2:-2])
            message_json=SocketHandler.get_json(self,'user',id(self),0,mname,2,message)
            SocketHandler.send_to_all(self,message_json)
        elif re.search('^/weather',str(message).encode('utf-8'),re.S):
            try:
                local = message[message.index(' ')+1:]
            except:
                local='beijing'
            message_bot = "%s's weather：<br>"%(local)+weather.getweather(local).replace('\n','<br>')
            message_json=SocketHandler.get_json(self,'user',id(self),1,mname,3,message)
            SocketHandler.send_to_all(self,message_json)
            message_json=SocketHandler.get_json(self,'bot',id(self)+12138,0,'Weather robot',3,message_bot)
            SocketHandler.send_to_all(self,message_json)
        elif re.search('^/news',str(message).encode('utf-8'),re.S):
            message_bot = 'Today News：<br>'+news.getnews().replace('\n','<br>')
            message_json=SocketHandler.get_json(self,'user',id(self),1,mname,3,message)
            SocketHandler.send_to_all(self,message_json)
            message_json=SocketHandler.get_json(self,'bot',id(self)+12138,0,'News robot',3,message_bot)
            SocketHandler.send_to_all(self,message_json)
        elif re.search('^/help',str(message).encode('utf-8'),re.S):
            message_json=SocketHandler.get_json(self,'user',id(self),1,mname,3,message)
            self.write_message(json.dumps(message_json))
            message='''使用帮助:<br>本聊天室规定使用Enter换行,Ctrl+Enter发送
                                <br>支持markdown语法发送<strong>代码</strong><br>Example:
                                <br>```python<br>print('Hello world!')<br>```
                                <br>支持使用LaTeX语法发送<strong>公式</strong><br>Example:<br>$$h = \\frac{1}{2}gt^2$$
                                <br>支持使用<strong>/weather 地点(拼音)</strong>查看天气
                                <br>支持使用<strong>/news</strong>查看新闻
                                <br>如果有什么建议，欢迎使用<strong>/feedback 内容</strong>给我们反馈'''
            message_json=SocketHandler.get_json(self,'bot',id(self)+12138,0,'Master robot',3,message)
            self.write_message(json.dumps(message_json))
        elif re.search('^/feedback',str(message).encode('utf-8'),re.S):
            cleaner = lxml.html.clean.Cleaner(style=True, scripts=True, frames = True,
                                              forms = True,page_structure=False, safe_attrs_only=False)
            message = cleaner.clean_html(message)
            feedback = message[13:-4]
            user_agent = self.request.headers['user-agent'].replace("\'","|")
            ip = self.request.headers.get("X-Real-IP")
            cx = MySQLdb.connect("localhost", "chat", "chat123", "chat",charset='utf8')
            cx.set_character_set('utf8')
            cursor = cx.cursor()
            cursor.execute("insert into feedback (id,ip,user_agent,time,message) values (%d,'%s','%s','%s','%s')"%(id(self),ip,user_agent,time.strftime("%H:%M:%S", time.localtime()),feedback))
            cursor.close()
            cx.commit()
            cx.close()
            message_json=SocketHandler.get_json(self,'user',id(self),1,mname,3,message)
            self.write_message(json.dumps(message_json))
            message='我们已经收到你的反馈了，谢谢你!'
            message_json=SocketHandler.get_json(self,'bot',id(self)+12138,0,'Master robot',3,message)
            self.write_message(json.dumps(message_json))
        elif message == 'c93c60882b37254bb13e80183f291af3':
            pass
        else:
            message = message.replace('\n','<br>')
            cleaner = lxml.html.clean.Cleaner(style=True, scripts=True, frames = True,
                                              forms = True,page_structure=False, safe_attrs_only=False)
            message = cleaner.clean_html(message)
            message_json=SocketHandler.get_json(self,'user',id(self),0,mname,3,message)
            SocketHandler.send_to_all(self,message_json)

    def get_json(self,type,realid,itisme,mname,messageType,message):
        jsonmessage={
                'type': type,
                'time':time.strftime("%H:%M:%S", time.localtime()),
                'id':realid,
                'itisme':itisme,
                'name': mname,
                'messageType':messageType,
                'message': message,
            }
        return jsonmessage

    def check_ip(self):
        user_agent = self.request.headers['user-agent'].replace("\'","|")
        ip = self.request.headers.get("X-Real-IP")
        cx = MySQLdb.connect("localhost", "chat", "chat123", "chat")
        cursor = cx.cursor()
        cursor.execute('select ip from offline')
        values_ip = cursor.fetchall()  # 获取查询ip
        cursor.execute('select ip from time')
        values_time = cursor.fetchall()  # 获取查询time
        ip = tuple("'"+str(ip)+"'"+',')
        black = 0
        for i in range(len(values_ip)-1,len(values_ip)-11,-1):
            fisrt = time.mktime(time.strptime('2016-01-01 '+values_time[i],'%Y-%m-%d %H:%M:%S'))
            second = time.mktime(time.strptime('2016-01-01 '+values_time[i-1],'%Y-%m-%d %H:%M:%S'))
            if ip == values_ip[i] and fisrt - second < 5:
                black += 1
        if black == 10:
            cursor.execute("insert into online (id,ip,user_agent,time) values (%d,'%s','%s',%s)"
                           %(id(self),ip,user_agent,time.strftime("%H:%M:%S", time.localtime())))
        cursor.close()
        cx.commit()
        cx.close()

DIR = "/upload/"
class UploadHandle(tornado.web.RequestHandler):
     def post(self, *args, **kwargs):
         fileinfo = self.request.files["file"][0]
         fname = fileinfo['filename']
         cname = DIR+time.strftime("%Y%m%d%H%M%S", time.localtime())+"."+fname.split(".")[-1]
         fh = open(cname, 'w')
         fh.write(fileinfo['body'])
         self.finish("success")
         fh.close()
         self.write(cname)


class Weather(tornado.web.RequestHandler):
    def get(self, input_city):
        try:
            if re.match('^[a-zA-Z]+$', input_city):
                local = input_city
            else:
                local='beijing'
        except:
            local = 'beijing'
        text = weather.getweather(local).split('\n')
        today = text[0][0:text[0].index(' ')]
        today_situation = text[1]
        today_temperature = text[2]
        tomorrow = text[4][0:text[4].index(' ')]
        tomorrow_situation = text[5]
        tomorrow_temperature = text[6]
        self.write(json.dumps({'today': today,
                               'today_situation': today_situation,
                               'today_temperature': today_temperature,
                               'tomorrow': tomorrow,
                               'tomorrow_situation': tomorrow_situation,
                               'tomorrow_temperature': tomorrow_temperature}, ensure_ascii=False))




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
        ('/upload', UploadHandle),
        (r"/weather/(\w+)", Weather),
    ],**settings
    )
    app.listen(7000,address='0.0.0.0')
    tornado.ioloop.IOLoop.instance().start()
