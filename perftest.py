import time
import logging
from locust import task, between
from locust_plugins.users.socketio import SocketIOUser
import requests
from sseclient import SSEClient


# Enable logging for debugging
logging.basicConfig(level=logging.DEBUG)


class MySocketIOUser(SocketIOUser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sse_url = "http://localhost:8080"  # SSE URL
        self.ws_url = "ws://localhost:8080"  # WebSocket URL
        self.my_value = None

    @task
    def my_task(self):
        # Simulate SSE connection (using HTTP GET)
        self.connect_to_sse()

        # Simulate WebSocket connection
        self.connect_to_websocket()

        # Subscribe to WebSocket events (you can modify this based on the server's logic)
        self.send(
            '42["subscribe",{"url":"/sport/matches/11995208/draws","sendInitialUpdate": true}]'
        )

        # Wait for SSE message processing (SSE running in background)
        self.wait_for_sse_event()

        # Sleep to simulate a real user interacting with the server
        self.sleep_with_heartbeat(10)

    def connect_to_sse(self):
        """Connects to SSE and listens for messages."""
        try:
            response = requests.get(self.sse_url, stream=True)
            client = SSEClient(response)
            for event in client.events():
                if (
                    event.event == "message"
                ):  # Adjust if you expect different event names
                    self.on_message(event.data)
                    break  # Stop after processing the first event
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

    def connect_to_websocket(self):
        """Connect to WebSocket and listen for WebSocket messages."""
        try:
            self.ws = self.connect(
                "ws://localhost:8080/socket.io/?EIO=3&transport=websocket"
            )
            logging.info("WebSocket connection established.")
        except Exception as e:
            logging.error(f"Error connecting to WebSocket: {e}")

    def on_message(self, message):
        """Process the message received via SSE."""
        try:
            self.my_value = message  # Adjust the data format as necessary
            logging.info(f"SSE message received: {self.my_value}")
        except Exception as e:
            logging.error(f"Error processing SSE message: {e}")


if __name__ == "__main__":
    host = "http://localhost:8080"  # Adjust host if necessary
