import logging
import sys

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Formato para ver de forma clara en la terminal
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
    )
    
    # Consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Archivo opcional (podemos llevar a otro nivel para logs en BD más adelante)
    file_handler = logging.FileHandler("backend_system.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

log = setup_logger("vision_backend")
