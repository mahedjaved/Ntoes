import time
import json
import gevent
import requests
from locust import HttpUser, task, events

class MySSEUser(HttpUser):
    @task
    def my_task(self):
        self.my_value = None
        
        # SSE URL for the server
        url = "https://example.com/sse"

        # Connect to the SSE stream using requests with stream=True
        try:
            response = requests.get(url, stream=True)
            
            # Ensure the connection was successful
            if response.status_code != 200:
                print(f"Error: Unable to connect to SSE stream (status code: {response.status_code})")
                return

            print(f"Connected to SSE stream at {url}")
            
            # Listen for incoming events from the SSE stream
            for line in response.iter_lines():
                if line:
                    # Each line represents an event, decode it and handle it
                    try:
                        message = json.loads(line.decode('utf-8'))
                        print(f"Received message: {message}")

                        # Check if the event contains the value you're interested in
                        if "my_value" in message:
                            self.my_value = message["my_value"]
                            print(f"Updated my_value: {self.my_value}")
                            break  # Exit the loop when the desired value is received
                    except Exception as e:
                        print(f"Error processing message: {e}")

                # Simulate heartbeat or keep-alive mechanism by sleeping
                gevent.sleep(1)  # This prevents blocking and keeps the greenlet running

            # Optionally, wait for more messages or send a dummy heartbeat if necessary
            while not self.my_value:
                gevent.sleep(1)  # Continue waiting for an update from the SSE stream

            print("Task completed, my_value received.")

        except requests.exceptions.RequestException as e:
            # Handle connection failure
            print(f"Error while connecting to SSE: {e}")
            events.request.fire(
                request_type="GET",
                name="SSE Connection",
                response_time=0,
                response_length=0,
                exception=str(e),
                context={"status": "failure"}
            )

        # Simulate some idle time after the task is complete (optional)
        gevent.sleep(2)

    def on_start(self):
        """ Called when a Locust user starts """
        print("SSE test started.")

if __name__ == "__main__":
    host = "http://example.com"
