import pika
import json
import psycopg2
from fastapi import FastAPI

app = FastAPI()


@app.post('/postgres')
def send_data(name, last_name, patronymic, number, text):
    connet = psycopg2.connect(host='postgres', port=5432, database='db1', user='postgres', password='postgres',)
    curs = connet.cursor()

    curs.execute(f"INSERT INTO user_data (name, last_name, patronymic, number, text) \
    VALUES ('{name}','{last_name}', '{patronymic}', '{number}', '{text}');")

    connet.commit()
    connet.close()
    curs.close()


credentials = pika.PlainCredentials(username='rabbit', password='rabbit')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq',
                                                               port=5672,
                                                               credentials=credentials,
                                                               virtual_host='host1'))

channel = connection.channel()
channel.queue_bind(exchange='ex1', queue='que1', routing_key='rout1')


def callback(ch, method, properties, body):
    data = json.loads(body)
    send_data(data['data'][0]['name'],
              data['data'][1]['last_name'],
              data['data'][2]['patronymic'],
              data['data'][3]['number'],
              data['data'][4]['text']
              )
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_consume(on_message_callback=callback, queue='que1')

channel.start_consuming()
