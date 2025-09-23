"""
                              ENCRIPTADOR
En el marco de la encriptación de tablas para las bases de Transbank, se desarrolla
esta aplicación para generar los script SQL que permiten redefinir las tablas
encriptandolas y comprimiendolas

"""

from pathlib import Path
from configparser import ConfigParser
from Utils.valida_configuracion import valida_archivo_config
from Utils.crea_logger   import crea_logger 
from Utils.Util_scripts  import inicia_scripts_redefinicion

CONFIG_FILE = 'redefinition.cfg'

def main():
    """ Función principal del programa :
                - Crear logger para manejo de loging
                - Validar archivo de configuración        
                - Crear script de redefinición de tablas
    """
    dir_proyecto = Path.cwd()
    logger = crea_logger(CONFIG_FILE)
    config = valida_archivo_config(CONFIG_FILE,logger)
    inicia_scripts_redefinicion(dir_proyecto,config,logger)
    
if __name__ == "__main__":
        main()
