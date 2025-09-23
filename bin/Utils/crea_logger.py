import logging
from pathlib import Path
from configparser import ConfigParser


def crea_logger(config_file):
    """ Función para crear el logger de la aplicación
        - Lee el archivo de configuración para obtener nivel de log y archivo de log
        - Crea el logger con manejo de archivo y consola
    """
    
    config = ConfigParser()
    config.read(f'bin/{config_file}')
    nivel = config.get('default','log_level').upper()
    log_file = config.get('default','log_file')

    logger = logging.getLogger('main')
    file_handler = logging.FileHandler(
                filename=log_file,
                mode ='w',
                encoding='utf-8')
    console_handler = logging.StreamHandler()

    formatter_fh = logging.Formatter(
            '[{levelname}]:\t{asctime}\t[{filename}:{lineno}]: {message} ',
            datefmt='%Y-%m-%d %H:%M:%S',
            style='{',
            )
    formater_con = logging.Formatter(
            '[{levelname}]: {message} ',
            datefmt='%Y-%m-%d %H:%M:%S',
            style='{',
            )


    file_handler.setFormatter(formatter_fh)
    console_handler.setFormatter(formater_con)
    console_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.DEBUG)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.setLevel(nivel)
    logger.debug(f"Logger creado con nivel {nivel} y archivo {log_file}")   
    return logger