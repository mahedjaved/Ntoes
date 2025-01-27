import time
import logging
from locust import task, between, User
from sseclient import SSEClient

# Enable logging for debugging
logging.basicConfig(level=logging.DEBUG)


class MySSEUser(User):
    wait_time = between(
        5, 10
    )  # Simulate real user with a random wait time between 5 to 10 seconds

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sse_url = "https://localhost:8080"  # SSE URL
        self.my_value = None

    @task
    def my_task(self):
        # Simulate SSE connection (using HTTP GET)
        self.connect_to_sse()

        # Wait for SSE message processing
        self.wait_for_sse_event()

    def connect_to_sse(self):
        """Connects to SSE and listens for messages."""
        try:
            # Make a GET request to the SSE endpoint
            with self.client.get(self.sse_url, stream=True) as response:
                client = SSEClient(response)
                for event in client.events():
                    if event.event == "message":  # Check for the event type
                        self.on_message(event.data)
                        break  # Stop after processing the first event (you can modify this if needed)
        except Exception as e:
            logging.error(f"Error connecting to SSE: {e}")

    def wait_for_sse_event(self):
        """Simulate waiting for an SSE event."""
        start_time = time.time()
        while not self.my_value:
            if time.time() - start_time > 30:  # Timeout after 30 seconds
                logging.warning("Timeout reached waiting for SSE message.")
                break
            time.sleep(0.1)
        if self.my_value:
            logging.info(f"Received SSE message: {self.my_value}")
        else:
            logging.warning("No SSE message received.")

    def on_message(self, message):
        """Process the message received via SSE."""
        try:
            self.my_value = message  # Adjust the data format as necessary
            logging.info(f"SSE message received: {self.my_value}")
        except Exception as e:
            logging.error(f"Error processing SSE message: {e}")


if __name__ == "__main__":
    # The `host` variable is automatically handled by Locust when the user class is executed.
    # Locust will pass the proper host value during runtime.
    pass
