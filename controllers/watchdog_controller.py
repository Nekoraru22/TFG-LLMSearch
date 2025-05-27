from watchdog.events import FileSystemEventHandler, FileSystemEvent, FileSystemMovedEvent
from watchdog.observers import Observer

from controllers.prefect_controller import new_file, modified_file, deleted_file, moved_file

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

        if old_stat is None or old_stat == new_stat or new_stat[0] - old_stat[0] < 60:
            logging.info(f"Insufficient time between creation and modification of file: {event.src_path}")
            return

        # Update cache and fire
        self.stats_cache[event.src_path] = new_stat
        logging.info(f"Modified file: {event.src_path}")
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


    def on_moved(self, event: FileSystemMovedEvent) -> None:
        """
        Se ejecuta cuando un archivo o directorio se mueve o renombra.
        event.src_path: ruta original
        event.dest_path: ruta nueva
        """
        if event.is_directory:
            return
        
        # Clean up the cache
        if event.src_path in self.stats_cache:
            del self.stats_cache[event.src_path]
        if event.dest_path in self.stats_cache:
            del self.stats_cache[event.dest_path]
        
        # Add the new file to the cache
        try:
            st = os.stat(event.dest_path)
        except FileNotFoundError:
            return
        self.stats_cache[event.dest_path] = (st.st_mtime, st.st_size)

        logging.info(f"Moved file: {event.src_path} → {event.dest_path}")
        moved_file(str(event.src_path), str(event.dest_path))


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
        # Check if the folder path exists and create it if it doesn't
        if not os.path.exists(self.path) or not os.path.isdir(self.path):
            logging.error(f"The path {self.path} does not exist.")
            os.makedirs(self.path)

        if self.watcher_thread and self.watcher_thread.is_alive():
            logging.warning("The watchdog thread is already running.")
            return
        
        # Process all files in the directory at startup
        for root, _, files in os.walk(self.path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    st = os.stat(file_path)
                    self.event_handler.stats_cache[file_path] = (st.st_mtime, st.st_size)
                    new_file(file_path)
                except FileNotFoundError:
                    logging.warning(f"File not found during startup: {file_path}")

        # Start the watchdog thread
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
