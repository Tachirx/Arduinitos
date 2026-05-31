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
    
    from logging.handlers import RotatingFileHandler
    
    # Sistema de rotación de logs (5 MB máximo por archivo, 3 respaldos históricos)
    file_handler = RotatingFileHandler(
        "backend_system.log", 
        maxBytes=5 * 1024 * 1024, 
        backupCount=3, 
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

log = setup_logger("vision_backend")
