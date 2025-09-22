"""
                              ENCRIPTADOR
En el marco de la encriptación de tablas para las bases de Transbank, se desarrolla
esta aplicación para generar los script SQL que permiten redefinir las tablas
encriptandolas y comprimiendolas

"""

from pathlib import Path
from configparser import ConfigParser
import sys
import re
import logging
from Utils.valida_configuracion import valida_archivo_config
from Utils.utilitarios    import get_parametros_tbs, get_parametros_tablas, crea_directorio
from Utils.Util_db       import conecta_db, crea_scripts_redefinicion  

def main(config,logger):
    
    conexion = conecta_db(config,logger)
    
    sid_db,parallel,habilita,tablespace_tabla,tablespace_index = get_parametros_tbs(config,logger)
    tablas = config.options('Tablas')
    for tabla in tablas:
        esquema,tabla,columnas = get_parametros_tablas(config,tabla,logger)

        logger.debug(f"Procesando tabla {esquema}.{tabla} columnas a encriptar {columnas}")

        # Creamos la estructura de directorios        
        crea_directorio(dir_proyecto,"SQL", sid_db, esquema, tabla)

        crea_scripts_redefinicion(dir_proyecto,conexion,sid_db, esquema, tabla,columnas,habilita,tablespace_tabla,tablespace_index,parallel) 
        

logger = logging.getLogger(__name__)

file_handler = logging.FileHandler(
                filename='logs/encriptador.log',
                mode ='w',
                encoding='utf-8')
console_handler = logging.StreamHandler()

formatter_fh = logging.Formatter(
        '[{levelname}]:\t{asctime}\t[{filename}:{lineno}]: {message} ',
        datefmt='%Y-%m-%d %H:%M:%S',
        style='{',
        )
formater_con = logging.Formatter(
        '[{levelname}]:[{filename}:{lineno}]: {message} ',
        datefmt='%Y-%m-%d %H:%M:%S',
        style='{',
        )


file_handler.setFormatter(formatter_fh)
console_handler.setFormatter(formater_con)
console_handler.setLevel(logging.INFO)
file_handler.setLevel(logging.DEBUG)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
logger.setLevel(logging.DEBUG)

logger.info('Inicio Proceso Generacion Scripts Encriptacion')

if __name__ == "__main__":
    dir_proyecto = Path.cwd()
    config = ConfigParser()
    config = valida_archivo_config(logger)
    main(config,logger)
