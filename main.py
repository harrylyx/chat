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



class Index(tornado.web.RequestHandler):
    def get(self):
        self.render('templates/index.html')
        user_agent = self.request.headers['user-agent']
        ip = self.request.remote_ip


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
        mname = SocketHandler.get_name(self)
        SocketHandler.clients.add(self)
        self.write_message(json.dumps({
            'type': 'sys',
            'id':id(self),
            'person':len(SocketHandler.clients),
            'message': 'Welcome to WebSocket',
        }))
        SocketHandler.send_to_all(self,{
            'type': 'sys',
            'person':len(SocketHandler.clients),
            'message': mname + ' has joined',
        })


    def on_close(self):
        mname = SocketHandler.get_name(self)
        SocketHandler.clients.remove(self)
        SocketHandler.send_to_all(self,{
            'type': 'sys',
            'person':len(SocketHandler.clients),
            'message': mname + ' has left',
        })

    def on_message(self, message):
        mname = SocketHandler.get_name(self)
        if re.match('```.```',message):
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
        elif re.match('$$.$$',message):
            message = '<img src="http://chart.googleapis.com/chart?cht=tx&chl= {0}" style="border:none;">'.format(message)
            SocketHandler.send_to_all(self,{
                'type': 'user',
                'time':time.strftime("%H:%M:%S", time.localtime()),
                'id':id(self),
                'name': mname,
                'messageType':2,
                'message': message,
            })
        else:
            SocketHandler.send_to_all(self,{
                'type': 'user',
                'time':time.strftime("%H:%M:%S", time.localtime()),
                'id':id(self),
                'name': mname,
                'messageType':3,
                'message': message,
            })


if __name__ == '__main__':
    settings = dict(
        static_path = os.path.join(os.path.dirname(__file__), "static"),
    )
    app = tornado.web.Application([
        ('/', Index),
        ('/soc', SocketHandler),
    ],**settings
    )
    app.listen(7000,address='0.0.0.0')
    tornado.ioloop.IOLoop.instance().start()
