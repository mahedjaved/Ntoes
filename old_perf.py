import logging
import time
import gevent
import traceback
from locust import HttpUser, task, events
from gevent import monkey
import requests
from exception import StopUser, RescheduleTask, RescheduleTaskImmediately, InterruptTaskSet

# Patch standard library to make it compatible with Gevent
monkey.patch_all()

class SSEClient:
    def __init__(self, url):
        self.url = url

    def connect(self):
        """Connect to the SSE stream using requests with stream=True."""
        session = requests.Session()
        try:
            response = session.get(self.url, stream=True)
            # Listen to incoming events
            for line in response.iter_lines():
                if line:
                    print(f"Received event: {line.decode('utf-8')}")
            return response
        except requests.exceptions.RequestException as e:
            # Handle connection error
            print(f"Error while connecting to SSE stream: {e}")
            raise  # Raise the exception to trigger failure event
        finally:
            session.close()


class SSEUser(HttpUser):
    @task
    def test_sse(self):
        # Connect to the SSE service and listen for events
        sse_client = SSEClient("http://localhost:5000/sse")

        try:
            # Attempt to connect to the SSE stream
            connection = sse_client.connect()
            
            # Fire success event using `events.request.fire` (updated for Locust 2.x)
            events.request.fire(
                request_type="GET",
                name="SSE Connection",
                response_time=0,  # Set to 0 or calculate response time
                response_length=len(connection.content),  # Length of the SSE response content
                context={'status': 'success'}  # Custom context can be passed
            )

            # Keep the connection alive (simulate a long-running request)
            time.sleep(10)  # Adjust sleep to simulate duration of connection

        except Exception as e:
            # Fire failure event on connection failure
            events.request.fire(
                request_type="GET",
                name="SSE Connection",
                response_time=0,  # Could calculate time until failure
                response_length=0,
                exception=str(e),  # Exception message
                context={'status': 'failure'}
            )
            logging.error(f"SSE Connection failed: {e}")
            raise e  # Optionally raise the error to stop the user

