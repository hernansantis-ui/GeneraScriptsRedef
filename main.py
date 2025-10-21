"""
                              ENCRIPTADOR
En el marco de la encriptación de tablas para las bases de Transbank, se desarrolla
esta aplicación para generar los script SQL que permiten redefinir las tablas
encriptandolas y comprimiendolas

"""


from pathlib import Path
from Utils.validacionConfig import valida_archivo_config
from Utils.creaScriptsRedef  import inicia_scripts_redefinicion
from Utils.utilitariosSys   import crea_config_parser
import logging

DIR_PROYECTO = Path.cwd()
CONFIG_FILE = DIR_PROYECTO/"config"/"redefinition.cfg"

def crea_logger(config):
    """ Función para crear el logger de la aplicación
        - Lee el archivo de configuración para obtener nivel de log y archivo de log
        - Crea el logger con manejo de archivo y consola
    """
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


def main():
    """ Función principal del programa :
            - Crea objeto configparser para leer el archivo de configuración
            - Crear logger para manejo de loging
            - Validar archivo de configuración        
            - Crear los script de redefinición de tablas
    """
    config = crea_config_parser(CONFIG_FILE)
    logger = crea_logger(config)
    logger.info('Iniciamos proceso de generación de scripts')
    valida_archivo_config(config)
    inicia_scripts_redefinicion(DIR_PROYECTO,config)

if __name__ == "__main__":
        main()
