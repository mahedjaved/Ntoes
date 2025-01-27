# import time
# import json
# import gevent
# import logging
# import requests
# from locust import HttpUser, task, events
# from gevent import monkey

# # Patch standard library to make it compatible with Gevent
# monkey.patch_all()

# class SSEClient:
#     def __init__(self, url):
#         self.url = url

#     def connect(self):
#         """Connect to the SSE stream using requests with stream=True."""
#         session = requests.Session()
#         try:
#             response = session.get(self.url, stream=True)  # Keeps the connection open for SSE

#             # Ensure the connection was successful
#             if response.status_code != 200:
#                 logging.error(f"Failed to connect to SSE: {response.status_code}")
#                 return None

#             # Listen to incoming events from the SSE stream
#             for line in response.iter_lines():
#                 if line:
#                     try:
#                         message = line.decode('utf-8')
#                         print(f"Received SSE message: {message}")
#                         # Fire event when data is received
#                         events.request.fire(
#                             request_type="GET",
#                             name="SSE Connection",
#                             response_time=0,
#                             response_length=len(line),
#                             context={'status': 'success', 'data': message}
#                         )
#                     except Exception as e:
#                         logging.error(f"Error processing SSE message: {e}")

#                 # Simulate some delay or work
#                 gevent.sleep(1)  # Non-blocking sleep for gevent greenlet

#             return response

#         except requests.exceptions.RequestException as e:
#             # Handle failure by firing an event
#             events.request.fire(
#                 request_type="GET",
#                 name="SSE Connection",
#                 response_time=0,
#                 response_length=0,
#                 exception=str(e),
#                 context={'status': 'failure'}
#             )
#             logging.error(f"SSE Connection failed: {e}")
#             raise e
#         finally:
#             session.close()

# class SSEUser(HttpUser):
#     @task
#     def test_sse(self):
#         """Test task for SSE connection"""
#         sse_client = SSEClient("http://localhost:8080/sse")

#         try:
#             # Start the SSE connection (long-lived connection)
#             connection = sse_client.connect()
#             if connection:
#                 print("SSE connection established.")
#         except Exception as e:
#             logging.error(f"SSE Test failed: {e}")
#             raise e

#         # Simulate a task being executed while keeping the SSE connection open
#         while True:
#             gevent.sleep(1)  # Keep the greenlet running to simulate continuous tasks

# # Optional: If you want to print when requests succeed or fail
# def on_request_success(request_type, name, response_time, response_length, context, **kwargs):
#     if context.get('status') == 'success':
#         print(f"Success: {name} | {request_type} | Response Time: {response_time}ms | Response Length: {response_length} bytes | Data: {context.get('data')}")
#     elif context.get('status') == 'failure':
#         print(f"Failure: {name} | {request_type} | Error: {kwargs.get('exception')}")

# # Register the listener for request events
# events.request.add_listener(on_request_success)

# if __name__ == "__main__":
#     host = "http://localhost:8080"
#     # To run the Locust test from the command line
#     # locust -f this_script.py

import time
import json
import gevent
import logging
import requests
from locust import HttpUser, task, events
from gevent import monkey

# Patch standard library to make it compatible with Gevent
monkey.patch_all()

class SSEClient:
    def __init__(self, url):
        self.url = url

    def connect(self):
        """Connect to the SSE stream using requests with stream=True."""
        session = requests.Session()
        try:
            response = session.get(self.url, stream=True)  # Keeps the connection open for SSE

            # Ensure the connection was successful
            if response.status_code != 200:
                logging.error(f"Failed to connect to SSE: {response.status_code}")
                return None

            # Listen to incoming events from the SSE stream
            for line in response.iter_lines():
                if line:
                    try:
                        message = line.decode('utf-8')
                        print(f"Received SSE message: {message}")
                        # Fire event when data is received
                        events.request.fire(
                            request_type="GET",
                            name="SSE Connection",
                            response_time=0,
                            response_length=len(line),
                            context={'status': 'success', 'data': message}
                        )
                    except Exception as e:
                        logging.error(f"Error processing SSE message: {e}")

                # Simulate some delay or work
                gevent.sleep(1)  # Non-blocking sleep for gevent greenlet

            return response

        except requests.exceptions.RequestException as e:
            # Handle failure by firing an event
            events.request.fire(
                request_type="GET",
                name="SSE Connection",
                response_time=0,
                response_length=0,
                exception=str(e),
                context={'status': 'failure'}
            )
            logging.error(f"SSE Connection failed: {e}")
            raise e
        finally:
            session.close()

class SSEUser(HttpUser):
    @task
    def test_sse(self):
        """Test task for SSE connection"""
        sse_client = SSEClient("http://localhost:8080/sse")

        try:
            # Start the SSE connection (long-lived connection)
            connection = sse_client.connect()
            if connection:
                print("SSE connection established.")
        except Exception as e:
            logging.error(f"SSE Test failed: {e}")
            raise e

        # Simulate a task being executed while keeping the SSE connection open
        for _ in range(20):  # Keep making dummy requests periodically to simulate activity
            gevent.sleep(2)  # Keep the greenlet running, every 2 seconds
            events.request.fire(
                request_type="GET",
                name="Heartbeat",
                response_time=0,
                response_length=0,
                context={'status': 'success', 'data': "heartbeat"}
            )

# Optional: If you want to print when requests succeed or fail
# def on_request_success(request_type, name, response_time, response_length, context, **kwargs):
#     if context.get('status') == 'success':
#         print(f"Success: {name} | {request_type} | Response Time: {response_time}ms | Response Length: {response_length} bytes | Data: {context.get('data')}")
#     elif context.get('status') == 'failure':
#         print(f"Failure: {name} | {request_type} | Error: {kwargs.get('exception')}")

# Register the listener for request events
# events.request.add_listener(on_request_success)

if __name__ == "__main__":
    host = "http://localhost:8080"
    # To run the Locust test from the command line
    # locust -f this_script.py
