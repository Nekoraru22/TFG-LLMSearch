from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer

import threading
import logging
import time


class CustomHandler(FileSystemEventHandler):
    """
    Clase que maneja los eventos de creación, modificación y eliminación de archivos.
    """
    
    def __init__(self) -> None:
        """
        Inicializa el manejador de eventos.
        """
        self.recently_created = {}
        self.cooldown = 1.0  # tiempo en segundos para ignorar modificaciones después de crear
        

    def on_created(self, event) -> None:
        """
        Método que se ejecuta cuando se crea un archivo.

        Args:
            event: Evento de creación de
        """
        logging.info(f"Created file: {event.src_path}")
        # Registrar cuándo se creó el archivo
        self.recently_created[event.src_path] = time.time()
        

    def on_modified(self, event) -> None:
        """
        Método que se ejecuta cuando se modifica un archivo.

        Args:
            event: Evento de modificación
        """
        current_time = time.time()
        # Verificar si el archivo fue creado recientemente
        if event.src_path in self.recently_created:
            # Si la modificación ocurre dentro del periodo de cooldown después de la creación, ignorarla
            if current_time - self.recently_created[event.src_path] <= self.cooldown:
                return  # No registrar la modificación
            else:
                # Después del periodo de cooldown, eliminamos el archivo de la lista de recién creados
                del self.recently_created[event.src_path]
        
        # Si llegamos aquí, registrar la modificación normalmente
        logging.info(f"Modified file: {event.src_path}")
        
        
    def on_deleted(self, event: FileSystemEvent) -> None:
        """
        Método que se ejecuta cuando se elimina un archivo.

        Args:
            event: Evento de eliminación
        """
        logging.info(f"Deleted file: {event.src_path}")
        # Limpiar el registro si el archivo es eliminado
        if event.src_path in self.recently_created:
            del self.recently_created[event.src_path]


class WatchdogsController:
    """
    Clase que controla la vigilancia de un directorio con Watchdog.
    """

    def __init__(self, path: str) -> None:
        """
        Inicializa el controlador de vigilancia.

        Args:
            path: Ruta al directorio a vigilar
        """
        self.path = path
        self.event_handler = CustomHandler()
        self.observer = None
        self.watcher_thread = None
        self.running = False
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


    def _watch_directory(self) -> None:
        """
        Método interno que ejecuta la vigilancia en segundo plano.
        """
        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.path, recursive=True)
        self.observer.start()
        
        try:
            while self.running:
                time.sleep(1)
        except Exception as e:
            logging.error(f"Error en la vigilancia: {e}")
        finally:
            if self.observer:
                self.observer.stop()
                self.observer.join()


    def start(self) -> None:
        """
        Inicia la vigilancia del directorio en segundo plano.
        """
        if self.watcher_thread and self.watcher_thread.is_alive():
            logging.warning("La vigilancia ya está en ejecución")
            return
            
        self.running = True
        self.watcher_thread = threading.Thread(target=self._watch_directory)
        self.watcher_thread.daemon = True  # El hilo se cerrará cuando el programa principal termine
        self.watcher_thread.start()
        logging.info(f"Vigilancia iniciada en segundo plano para: {self.path}")


    def stop(self) -> None:
        """
        Detiene la vigilancia del directorio.
        """
        self.running = False
        if self.watcher_thread:
            self.watcher_thread.join(timeout=2)  # Esperar hasta 2 segundos a que termine
            if self.watcher_thread.is_alive():
                logging.warning("No se pudo detener el hilo de vigilancia correctamente")
        
        if self.observer:
            self.observer.stop()
            self.observer.join()
            
        logging.info("Vigilancia detenida")
