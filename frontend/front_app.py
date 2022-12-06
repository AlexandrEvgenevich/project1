import asyncio
import json
import pika
import tornado.web


def rabbit_connect(user_data):
    credentials = pika.PlainCredentials(username='rabbit', password='rabbit')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq',
                                                                   port=5672,
                                                                   credentials=credentials,
                                                                   virtual_host='host1'))

    channel = connection.channel()

    channel.basic_publish(exchange='ex1', routing_key='rout1', body=user_data.encode())

    connection.close()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')

    def post(self):
        name = str(self.request.arguments.get('name'))
        name = name.replace("'", '').replace('b', '').replace('[', '').replace(']', '')
        if len(name) > 30:
            self.render('input_error.html')
            return None

        last_name = str(self.request.arguments.get('last name'))
        last_name = last_name.replace("'", '').replace('b', '').replace('[', '').replace(']', '')
        if len(last_name) > 30:
            self.render('input_error.html')
            return None

        patronymic = str(self.request.arguments.get('patronymic'))
        patronymic = patronymic.replace("'", '').replace('b', '').replace('[', '').replace(']', '')
        if len(patronymic) > 30:
            self.render('input_error.html')
            return None

        number = str(self.request.arguments.get('number'))
        number = number.replace("'", '').replace('b', '').replace('[', '').replace(']', '')
        if len(number) > 30:
            self.render('input_error.html')
            return None

        text = str(self.request.arguments.get('text'))
        text = text.replace("'", '').replace('b', '').replace('[', '').replace(']', '')
        if len(text) > 790:
            self.render('input_error.html')
            return None

        user_data = {'data': [{'name': name},
                              {'last_name': last_name},
                              {'patronymic': patronymic},
                              {'number': number},
                              {'text': text}
                              ]
                     }

        if name == '' or last_name == '' or patronymic == '' or number == '' or text == '':
            self.render('fields_error.html')
        else:
            user_data = json.dumps(user_data, indent=2)

            try:
                rabbit_connect(user_data=user_data)
                self.render('success.html')
            except:
                self.render('rabbit_error.html')


def make_app():
    return tornado.web.Application([
        (r'/', MainHandler),
    ])


async def main():
    app = make_app()
    app.listen(port=80)
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())
