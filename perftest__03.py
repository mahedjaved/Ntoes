import time
import logging
from locust import task, between, HttpUser, events
from sseclient import SSEClient
from locust.env import Environment
from locust.stats import stats_history, stats_printer
import gevent

# Enable logging for debugging
logging.basicConfig(level=logging.DEBUG)

class MySSEUser(HttpUser):
    wait_time = between(5, 10)  # Simulate real user with a random wait time between 5 to 10 seconds
    host = "https://localhost:8080" 

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


# Function to setup and start the Locust test environment
def start_locust_test():
    # Setup Environment and Runner
    env = Environment(user_classes=[MySSEUser], events=events)
    runner = env.create_local_runner()

    # Start a WebUI instance
    web_ui = env.create_web_ui("127.0.0.1", 8089)

    # Execute init event handlers (only really needed if you have registered any)
    env.events.init.fire(environment=env, runner=runner, web_ui=web_ui)

    # Start a greenlet that periodically outputs the current stats
    gevent.spawn(stats_printer(env.stats))

    # Start a greenlet that saves current stats to history
    gevent.spawn(stats_history, env.runner)

    # Start with 5 users immediately (0-10 seconds)
    runner.start(5, spawn_rate=5)  # Start with 5 users

    # After 10 seconds, increase total users to 10
    gevent.spawn_later(10, runner.start, 5, 5)  # Add 5 more users, total = 10

    # After 20 seconds, increase total users to 100
    gevent.spawn_later(30, runner.start, 20, 20)  # Add 90 more users, total = 100

    gevent.spawn_later(60, runner.start, 100, 100)  # Add 90 more users, total = 100

    # Stop the runner after 60 seconds
    # gevent.spawn_later(120, runner.quit)
    logging.info("Waiting for 30 seconds to allow downloading the report...")
    time.sleep(60)  # Wait for 30 seconds to give you time to download the report

    # Now quit the runner
    logging.info("Quitting the test runner and generating the HTML report...")
    runner.quit()


    # Wait for the greenlets
    runner.greenlet.join()

    # Stop the web server for good measure
    web_ui.stop()


if __name__ == "__main__":
    # Start the Locust test
    start_locust_test()
