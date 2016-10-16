# coding=utf-8
import tornado.web
import tornado.ioloop
import tornado.websocket
import json
import re
import os
import random
import time



class Index(tornado.web.RequestHandler):
    def get(self):
        self.render('templates/index.html')


class SocketHandler(tornado.websocket.WebSocketHandler):
    clients = set()

    mname_n = {'1':'老虎','2':'狼','3':'仓鼠','4':'麋鹿','5':'猫','6':'猴子',
                '7':'树懒','8':'斑马','9':'哈士奇','10':'狐狸','11':'白熊',
                '12':'大象','13':'豹子','14':'牦牛'}
    mname_adj = {'1':'暖洋洋的','2':'醉醺醺的','3':'香喷喷的','4':'干巴巴的',
                    '5':'沉甸甸的','6':'羞答答的','7':'亮晶晶的','8':'沉甸甸的',
                    '9':'白花花的','10':'绿油油的','11':'黑黝黝的','12':'慢腾腾的',
                    '13':'阴森森的','14':'皱巴巴的'}
    mname = mname_adj[str(random.randint(1,14))]+mname_n[str(random.randint(1,14))]

    @staticmethod
    def send_to_all(message):
        for c in SocketHandler.clients:
            c.write_message(json.dumps(message))

    def open(self):
        self.write_message(json.dumps({
            'type': 'sys',
            'id':id(self),
            'message': 'Welcome to WebSocket',
        }))
        SocketHandler.send_to_all({
            'type': 'sys',
            'message': SocketHandler.mname + ' has joined',
        })
        SocketHandler.clients.add(self)

    def on_close(self):
        SocketHandler.clients.remove(self)
        SocketHandler.send_to_all({
            'type': 'sys',
            'message': SocketHandler.mname + ' has left',
        })

    def on_message(self, message):
        SocketHandler.send_to_all({
            'type': 'user',
            'time':time.time(),
            'id':id(self),
            'name': SocketHandler.mname,
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
    app.listen(8000,address="0.0.0.0")
    tornado.ioloop.IOLoop.instance().start()
