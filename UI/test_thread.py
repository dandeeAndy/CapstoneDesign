import threading
import time

def thread_task(name):
    """Thread task that logs start and end time."""
    start_time = time.time()
    print(f"{name} started at {time.strftime('%X', time.localtime(start_time))}")
    # Simulate work by sleeping
    time.sleep(2)
    end_time = time.time()
    print(f"{name} ended at {time.strftime('%X', time.localtime(end_time))}")

# Create threads
thread1 = threading.Thread(target=thread_task, args=("Thread-1",))
thread2 = threading.Thread(target=thread_task, args=("Thread-2",))
thread3 = threading.Thread(target=thread_task, args=("Thread-3",))

# Start threads
thread1.start()
thread2.start()
thread3.start()

# Wait for all threads to complete
thread1.join()
thread2.join()
thread3.join()

# These function calls are commented to prevent execution here. Uncomment before running the final script.
# thread1.start()
# thread2.start()
# thread3.start()
# thread1.join()
# thread2.join()
# thread3.join()
