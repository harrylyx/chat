# coding=utf-8
import tornado.web
import tornado.ioloop
import tornado.websocket
import json
import re
import os
import random

class Index(tornado.web.RequestHandler):
    def get(self):
        self.render('templates/index.html')


class SocketHandler(tornado.websocket.WebSocketHandler):
    clients = set()

    @staticmethod
    def send_to_all(message):
        for c in SocketHandler.clients:
            c.write_message(json.dumps(message))

    def open(self):
        self.write_message(json.dumps({
            'type': 'sys',
            'message': 'Welcome to WebSocket',
        }))
        SocketHandler.send_to_all({
            'type': 'sys',
            'message': str(id(self)) + ' has joined',
        })
        SocketHandler.clients.add(self)

    def on_close(self):
        SocketHandler.clients.remove(self)
        SocketHandler.send_to_all({
            'type': 'sys',
            'message': str(id(self)) + ' has left',
        })
    def on_message(self, message):
        mname_n = {'1':'虎','2':'狼','3':'鼠','4':'鹿','5':'貂','6':'猴',
                   '7':'树懒','8':'斑马','9':'狗','10':'狐','11':'熊',
                   '12':'象','13':'豹子','14':'麝牛'}
        mname_adj = {'1':'暖洋洋的','2':'醉醺醺的','3':'香喷喷的','4':'干巴巴的',
                     '5':'沉甸甸的','6':'羞答答的','7':'亮晶晶的','10':'沉甸甸的',
                     '11':'白花花的','12':'绿油油的','13':'黑黝黝的','14':'慢腾腾的',
                     '15':'阴森森的','16':'皱巴巴的'}
        SocketHandler.send_to_all({
            'type': 'user',
            'id': mname_adj[str(random.randint(1,16))]+mname_n[str(random.randint(1,14))],
            'message': message,
        })


if __name__ == '__main__':
    settings = dict(
        static_path= os.path.join(os.path.dirname(__file__), "static"),
    )
    app = tornado.web.Application([
        ('/', Index),
        ('/soc', SocketHandler),
    ],**settings
    )
    app.listen(8000,address="0.0.0.0")
    tornado.ioloop.IOLoop.instance().start()
