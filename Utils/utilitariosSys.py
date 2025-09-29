import sys
import logging
from pathlib import Path

def is_archivo_vacio(archivo):
    """
        Verifica si el archivo ingresado como argumento esta vacio o no
        ===============================================================
    """
    path_archivo = Path(archivo)
    if not path_archivo.is_file():
        #print(f"Error: '{archivo}' no es archivo o no existe")
        return False
    return path_archivo.stat().st_size == 0

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

def crea_config_parser(config_file):
    """ Crea el parser para leer el archivo de configuración config_file 
            - Valida que el archivo tenga la sección [default] y las opciones
              log_level, log_file con valores válidos 
    """
    import configparser  # import ConfigParser

    opciones_default = ['log_level','log_file']
    niveles_permitidos = ['DEBUG','INFO','WARNING','ERROR','CRITICAL']  
    try:
        config = configparser.ConfigParser()
        config.read(f'{config_file}')
        config.BOOLEAN_STATES = {'si':True, 'no':False}

        #   Validamos la sección [default] y las opciones referentes al logger
        if config.has_section('default'):
            for opt in opciones_default:
                if config.has_option('default',opt):
                    valor = config.get('default',opt)
                    if not valor :
                        raise ValueError(f'Opcion "{opt}" no puede estar vacia en sección [default]')    
                    if opt == 'log_level' and valor.upper() not in niveles_permitidos:
                        raise ValueError(f'Opción "log_level" debe ser uno de {niveles_permitidos} en sección [default]')
            logger = crea_logger(config)
            return config,logger
        else:
            raise ValueError(f'Error: Archivo de configuración {config_file} debe contener la sección [default]')
    except FileNotFoundError:
        raise SystemExit(f'Archivo de configuración {config_file} no encontrado')  
    except Exception as e:          
        raise SystemExit(f'Error inesperado al leer el archivo de configuración {config_file}: {e}')  

def get_parametros_default(config,logger): 
    logger.debug("Obteniendo parámetros por defecto desde el archivo de configuración.")
    try:
        log_file = config.get('default','log_file')
        log_level = config.get('default','log_level').upper()
        acceso_base = config.getboolean('default','acceso_base')
        logger.debug(f"Parámetros obtenidos: log_file={log_file}, log_level={log_level}") 
        return log_file, log_level,acceso_base
    except Exception as e:
        logger.critical(f"Error al obtener parámetros por defecto: {str(e)}")
        sys.exit(1)

def get_parametros_tbs(config,logger,indice):
    logger.debug("Obteniendo parámetros de tablespaces desde el archivo de configuración.")
    tablespace = str('')
    try:
        habilita = config.getboolean('Tablespaces','habilita_cambio')
        if habilita and indice:
            tablespace = config.get('Tablespaces','tablespace_indice')
        elif habilita and not indice:
            tablespace = config.get("Tablespaces", "tablespace_tabla")
        if len(tablespace) == 0:
            tablespace=None
        logger.debug(f"Parámetros obtenidos: Habilita Cambio={habilita}, Tablespace Tabla={tablespace},") 
        return habilita, tablespace 
    except Exception as e:
        logger.critical(f"Error al obtener parámetros de tablespaces: {str(e)}")
        sys.exit(1)         

def get_parametros_tablas(config,opt,logger):
    logger.debug(f"Obteniendo parámetros para la tabla {opt.upper()} desde el archivo de configuración.")
    try:
        esquema = opt.split('.')[0].upper()
        tabla = opt.split('.')[1].upper()
        valores = config.get('Tablas',opt)
        if len(valores) > 0: 
            columnas = [col.strip() for col in config.get('Tablas',opt).split(',')]
        else:
            columnas=[]    
        logger.debug(f"{esquema}.{tabla}: Columnas a encriptar={columnas}")
        return esquema, tabla, columnas
    except Exception as e: 
        logger.critical(f"Error al obtener parámetros para la tabla {opt}: {str(e)}")
        sys.exit(1)

def crea_directorio_SQL(sql_dir, base_dato, esquema, tabla,logger):
    logger.debug(f"Creando directorio para {base_dato=}, {esquema=}, {tabla=}")
    try:
        ruta = sql_dir / base_dato / esquema / tabla
        ruta.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Directorio creado: {ruta}")  
    except Exception as e:
        logger.critical(f"Error al crear directorio {ruta}: {str(e)}")
        sys.exit(1)
