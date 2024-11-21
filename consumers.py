"""
    This class responsible for receiving data from django application youtools.
"""

import json
import os
import pika
from pika.exceptions import AMQPConnectionError
from api import user

class RabbitMQConsumer:
    """Required parameters/arguments"""
    def __init__(self):
        self.rabbitmq_url = os.environ.get('RABBITMQ_URL')

    def connect_consumer(self):
        """This function will get user data from django application youtools and save on the mongoDB database"""
        try:
            params = pika.URLParameters(self.rabbitmq_url)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            channel.queue_declare(queue='sent_user_data-queue_sentiment_analysis_flask')

            def callback(ch, method, properties, body):
                try:
                    print("message receiving....")
                    if properties.type == 'user_is_created':
                        print("Task executing, please wait....")
                        data = json.loads(body)
                        user.insert_one({'_id': data['id'], 'username': data['username'], 'email': data['email']})
                        print("User inserted successfully")
                    
                except Exception as e:
                        # Log or handle errors during message processing
                        print(f"Error processing message: {e}")
                # Start consuming messages from 'django_app' queue
            channel.basic_consume(queue='sent_user_data-queue_sentiment_analysis_flask', on_message_callback=callback, auto_ack=True)
            print('Waiting for messages....')
            channel.start_consuming()

        except AMQPConnectionError as e:
            print(f"Failed to connect to RabbitMQ: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

        finally:
            # Ensure the channel and connection are closed if they were opened
            if 'channel' in locals() and channel.is_open:
                channel.close()
            if 'connection' in locals() and connection.is_open:
                connection.close()


if __name__ == '__main__':
    rabbitmq_consumer = RabbitMQConsumer()
    rabbitmq_consumer.connect_consumer()