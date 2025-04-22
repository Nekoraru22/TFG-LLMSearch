from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer

from controllers.prefect_controller import new_file, modified_file, deleted_file

import threading
import logging
import time
import os


class CustomHandler(FileSystemEventHandler):
    """
    Class that handles file creation, modification, and deletion events.
    """
    
    def __init__(self) -> None:
        """
        Initializes the event handler.
        """
        self.stats_cache = {}
        

    def on_created(self, event) -> None:
        """
        Method that is executed when a file is created.

        Args:
            event: Event of creation
        """
        # Ignore directories
        if event.is_directory:
            return
        
        # Add the file to the cache
        try:
            st = os.stat(event.src_path)
        except FileNotFoundError:
            return
        self.stats_cache[event.src_path] = (st.st_mtime, st.st_size)

        logging.info(f"Created file: {event.src_path}")
        new_file(str(event.src_path))
        

    def on_modified(self, event) -> None:
        """
        Method that is executed when a file is modified.

        Args:
            event: Event of modification
        """
        # Ignore directories
        if event.is_directory:
            return

        try:
            st = os.stat(event.src_path)
        except FileNotFoundError:
            return

        new_stat = (st.st_mtime, st.st_size)
        old_stat = self.stats_cache.get(event.src_path)

        # If nothing really changed, skip.
        if old_stat == new_stat:
            return

        # Update cache and fire
        self.stats_cache[event.src_path] = new_stat
        logging.info(f"Modified (real) file: {event.src_path}")
        modified_file(str(event.src_path))
        
        
    def on_deleted(self, event: FileSystemEvent) -> None:
        """
        Method that is executed when a file is deleted.

        Args:
            event: Event of deletion
        """
        # Not worth to check if the event is a directory (is deleted so I cant check)

        # Clean up the cache
        if event.src_path in self.stats_cache:
            del self.stats_cache[event.src_path]

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
