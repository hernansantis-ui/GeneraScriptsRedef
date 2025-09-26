
import sys
import re
import configparser #import ConfigParser
from pathlib import Path
import logging

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
    opciones_default = ['log_level','log_file']
    niveles_permitidos = ['DEBUG','INFO','WARNING','ERROR','CRITICAL']  
    try:
        config = configparser.ConfigParser()
        config.read(f'{Path.cwd()/'bin'/config_file}')
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

def get_parametros_tbs(config,logger):
    logger.debug("Obteniendo parámetros de tablespaces desde el archivo de configuración.")
    try:
        sid_db = config.get('Database','servicio')
        parallel = int(config.get('Tablespaces','paralelo'))
        habilita = config.getboolean('Tablespaces','habilita_cambio')
        if habilita:
            tablespace_tabla = config.get('Tablespaces','tablespace_tabla')
            tablespace_index = config.get('Tablespaces','tablespace_indice')
            if len(tablespace_tabla) == 0 :
                tablespace_tabla=None
            if len(tablespace_index) == 0 :
                tablespace_index=None
        else:
            tablespace_tabla=None
            tablespace_index=None
        logger.debug(f"Parámetros obtenidos: SID={sid_db}, Paralelo={parallel}, Habilita Cambio={habilita}, Tablespace Tabla={tablespace_tabla}, Tablespace Índice={tablespace_index}") 
        return sid_db, parallel, habilita, tablespace_tabla, tablespace_index
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

def cambia_tablespace(ddl_objeto,tablespace,logger):
    logger.debug(f"Cambiando tablespace a {tablespace} en el DDL del objeto.")

#   Buscamos la palabra TABLESPACE y cambiamos el tablespace por el indicado
    try:
        patron = r'.*(TABLESPACE\s*\w+)'
        matches = re.finditer(patron,ddl_objeto)
        for match in matches:
            linea = match.group()
            ddl_objeto = ddl_objeto.replace(linea,f'TABLESPACE {tablespace}')
        logger.debug("Cambio de tablespace realizado correctamente.")
        return ddl_objeto   
    except Exception as e:
        logger.critical(f"Error al cambiar tablespace en el DDL: {str(e)}")
        sys.exit(1)
    
def ddl_incorpora_compresion(ddl_indices,logger):
    logger.debug("Incorporando compresión avanzada en el DDL de índices.")
#   Buscamos la palabra TABLESPACE e incorporamos la compresion de indices antes
    try:
        patron=r'.*(TABLESPACE\s*\w+)'
        match = re.finditer(patron,ddl_indices)
        for linea in match:
            linea_nueva = f'  COMPRESS ADVANCED LOW \n  {linea.group()} '
            ddl_indice = ddl_indices.replace(linea.group(),linea_nueva)
        logger.debug("Compresión avanzada incorporada correctamente en el DDL de índices.")
        return ddl_indice
    except Exception as e:
            logger.critical(f"Error al incorporar compresión en el DDL de índices: {str(e)}")
            raise SystemError()

def encripta_columnas(ddl_tabla,columnas,logger):
    logger.debug(f"Incorporando encriptación en las columnas: {columnas}")
#   Buscamos las columnas en el DDL y les incorporamos la cláusula de encriptación
    try:
        for col in columnas:
            patron = fr'.*{col}.*(VARCHAR2|NUMBER).*\(\d+(,.*\d+|.*CHAR.*)\)\s*(,|'')'
            match = re.search(patron,ddl_tabla)
            if match:
                ini = match.start()
                fin = match.end()
                linea=ddl_tabla[ini:fin].strip()

        #  La linea con la columna esta encontrada falta determinar si tiene coma al final o no
            patron=fr'^.*{col}.*\(.*\).*(,)$'
            match = re.search(patron,linea)
            if match == None:  # No tiene coma
                linea_nueva=f"{linea} ENCRYPT USING 'AES256' NO SALT "
            else:     # Tiene coma al final
                fin=match.end()
                ini=match.start()       
                linea_nueva=f"{linea[ini:fin-1]} ENCRYPT USING 'AES256' NO SALT ,"
            ddl_tabla = ddl_tabla.replace(linea,linea_nueva)
        logger.debug("Encriptación incorporada correctamente en el DDL de la tabla.")   
        return ddl_tabla
    except Exception as e:
            logger.critical(f"Error al incorporar encriptación en el DDL de la tabla: {str(e)}")
            sys.exit(1)
