import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#  variables de entorno
load_dotenv()

USUARIO = os.getenv("DB_USUARIO", "root")
CLAVE = os.getenv("DB_PASSWORD", "")
HOST = os.getenv("DB_HOST", "localhost")
PUERTO = os.getenv("DB_PUERTO", "3306")
NOMBRE_DB = os.getenv("DB_NOMBRE", "proyecto")

# URL de conexión (Prioridad a DATABASE_URL_FULL si existe)
DATABASE_URL_FULL = os.getenv("DATABASE_URL")

if DATABASE_URL_FULL:
    DATABASE_URL = DATABASE_URL_FULL
else:
    # URL de conexión de respaldo (SQLite) por defecto si no existe archivo .env o configuración
    DATABASE_URL = "sqlite:///./proyecto.db"

# configuración específica para SQLite (POR SI LO USAN, evaluacion de lenguaje II pues)
argumentos_motor = {}
if DATABASE_URL.startswith("sqlite"):
    argumentos_motor = {"check_same_thread": False}

#  motor de la base de datos
motor = create_engine(DATABASE_URL, connect_args=argumentos_motor)

# sesiones
SesionLocal = sessionmaker(autocommit=False, autoflush=False, bind=motor)

# clase base para los modelos
Base = declarative_base()

def obtener_db():
    """Generador para obtener la sesión de base de datos."""
    db = SesionLocal()
    try:
        yield db
    finally:
        db.close()

def inicializar_db():
    """Crea todas las tablas definidas en los modelos."""
    Base.metadata.create_all(bind=motor)
