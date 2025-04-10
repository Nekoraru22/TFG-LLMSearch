from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer

from controllers.prefect_controller import new_file, modified_file, deleted_file

import threading
import logging
import time


class CustomHandler(FileSystemEventHandler):
    """
    Class that handles file creation, modification, and deletion events.
    """
    
    def __init__(self) -> None:
        """
        Initializes the event handler.
        """
        self.recently_created = {}
        self.cooldown = 10.0  # Cooldown period in seconds
        

    def on_created(self, event) -> None:
        """
        Method that is executed when a file is created.

        Args:
            event: Event of creation
        """
        logging.info(f"Created file: {event.src_path}")
        # Store the creation time of the file
        self.recently_created[event.src_path] = time.time()
        new_file(str(event.src_path))
        

    def on_modified(self, event) -> None:
        """
        Method that is executed when a file is modified.

        Args:
            event: Event of modification
        """
        current_time = time.time()
        # Check if the file was recently created
        if event.src_path in self.recently_created:
            # If the modification occurs within the cooldown period after creation, ignore it
            if current_time - self.recently_created[event.src_path] <= self.cooldown:
                return # Ignore the modification event
            else:
                # After the cooldown period, remove the file from the recently created list
                del self.recently_created[event.src_path]
        
        # If we reach here, log the modification normally
        logging.info(f"Modified file: {event.src_path}")
        modified_file(str(event.src_path))
        
        
    def on_deleted(self, event: FileSystemEvent) -> None:
        """
        Method that is executed when a file is deleted.

        Args:
            event: Event of deletion
        """
        # Clear the record if the file is deleted
        if event.src_path in self.recently_created:
            del self.recently_created[event.src_path]
        
        logging.info(f"Deleted file: {event.src_path}")
        deleted_file(str(event.src_path))


class WatchdogsController:
    """
    Class that controls the monitoring of a directory with Watchdog.
    """

    def __init__(self, path: str) -> None:
        """
        Initializes the watchdog controller.

        Args:
            path: Path to the directory to monitor
        """
        self.path = path
        self.event_handler = CustomHandler()
        self.observer = None
        self.watcher_thread = None
        self.running = False
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


    def _watch_directory(self) -> None:
        """
        Method that runs the monitoring in the background.
        """
        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.path, recursive=True)
        self.observer.start()
        
        try:
            while self.running:
                time.sleep(1)
        except Exception as e:
            logging.error(f"Error in the watchdog thread: {e}")
        except KeyboardInterrupt:
            logging.info("Keyboard interrupt received, stopping the watchdog thread.")
        finally:
            if self.observer:
                self.observer.stop()
                self.observer.join()


    def start(self) -> None:
        """
        Initializes the watchdog thread and starts monitoring the directory.
        """
        if self.watcher_thread and self.watcher_thread.is_alive():
            logging.warning("The watchdog thread is already running.")
            return
            
        self.running = True
        self.watcher_thread = threading.Thread(target=self._watch_directory)
        self.watcher_thread.daemon = True  # The thread will exit when the main program exits
        self.watcher_thread.start()
        logging.info(f"Watchdog thread started in background for: {self.path}")


    def stop(self) -> None:
        """
        Stops the directory monitoring.
        """
        self.running = False
        if self.watcher_thread:
            self.watcher_thread.join(timeout=2)  # Wait for 2 seconds for it to finish
            if self.watcher_thread.is_alive():
                logging.warning("The watchdog thread did not finish in time.")
        
        if self.observer:
            self.observer.stop()
            self.observer.join()
            
        logging.info("Watchdog thread stopped.")
