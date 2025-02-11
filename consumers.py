"""
    This class responsible for receiving data from django application youtools.
"""
import uuid
import json
import os
import pika
from pika.exceptions import AMQPConnectionError
from bson import ObjectId
from api import user, sentiment_analysis_db, category_db

class RabbitMQConsumer:
    """Required parameters/arguments"""
    def __init__(self):
        self.rabbitmq_url = os.environ.get('RABBITMQ_URL')

    def connect_consumer(self):
        """This function will Connect to the RabbitMQ Queue
            and then will get messages from the youtools
            producer. Tasks will get executed based on events
            and result will save on the mongoDB database.
        """
        try:
            params = pika.URLParameters(self.rabbitmq_url)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            channel.queue_declare(queue='sent_user_data-queue_sentiment_analysis_flask')

            def callback(ch, method, properties, body):
                """Responsible for getting properties type and
                    json data from producer and execute it in current consumer. 

                Args:
                    ch (Parameter): Not used but needed.
                    method (Parameter): Not used but needed.
                    properties (Parameter): for getting properties type so can execute.
                    specific task needed from producer to consumer.
                    body (Parameter): json data from the producer.
                """
                try:
                    print("message receiving....")
                    if properties.type == 'user_is_created':
                        print("Task executing, please wait....")
                        try:
                            data = json.loads(body)
                            user.insert_one({'_id': uuid.UUID(data['id']), 'username': data['username'], 'email': data['email']})
                            print("User inserted successfully")
                        except Exception as e:
                            print(f"Something is wrong, data insertion failed on user: {e}")

                    if properties.type == 'delete_sentiment_analysis_data_from_flask':
                        print("Task executing, please wait....")
                        try:
                            data = json.loads(body)
                            sentiment_analysis_db.delete_one({"_id": ObjectId(data)})
                            print("Data from sentiment analysis deleted successfully.")
                        except Exception as e:
                            print(f"Sothing is wrong, data from sentiment analysis failed to delete: {e}")
       
                    if properties.type == 'delete_sentiment_analysis_category_data_from_flask':
                        print("Task executing, please wait....")
                        try:
                            data = json.loads(body)
                            category_db.delete_one({"_id": ObjectId(data)})
                            sentiment_analysis_db.delete_many({"category": ObjectId(data)})
                            print("Data from category and sentiment analysis deleted successfully.")
                        except Exception as e:
                            print(f"Sothing is wrong, data from sentiment analysis failed to delete: {e}")

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