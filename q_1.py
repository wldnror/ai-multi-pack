import pika

# RabbitMQ 서버에 연결
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# 큐를 선언(이미 존재하지 않는 경우 생성)
channel.queue_declare(queue='hello')

# 'hello' 큐에 메시지 보내기
channel.basic_publish(exchange='',
                      routing_key='hello',
                      body='Hello World!')

print(" [x] Sent 'Hello World!'")
connection.close()
