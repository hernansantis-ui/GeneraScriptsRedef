"""
                              ENCRIPTADOR
En el marco de la encriptación de tablas para las bases de Transbank, se desarrolla
esta aplicación para generar los script SQL que permiten redefinir las tablas
encriptandolas y comprimiendolas

"""

from pathlib import Path
from Utils.valida_configuracion import valida_archivo_config
from Utils.Util_scripts  import inicia_scripts_redefinicion
from Utils.utilitarios   import crea_config_parser

CONFIG_FILE = 'redefinition.cfg'

def main():
    """ Función principal del programa :
            - Crea objeto configparser para leer el archivo de configuración
            - Crear logger para manejo de loging
            - Validar archivo de configuración        
            - Crear los script de redefinición de tablas
    """
    config,logger = crea_config_parser(CONFIG_FILE)

    valida_archivo_config(config,logger)
    dir_proyecto = Path.cwd()
    inicia_scripts_redefinicion(dir_proyecto,config,logger)
    
if __name__ == "__main__":
        main()
