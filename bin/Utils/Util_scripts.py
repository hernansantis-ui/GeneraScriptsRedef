from Utils.Util_db       import conecta_db, crea_scripts_redefinicion
from Utils.utilitarios   import get_parametros_tbs, get_parametros_tablas, crea_directorio

def inicia_scripts_redefinicion(dir_proyecto,config,logger):
    """ Función para iniciar la creación de los scripts de redefinición de tablas
        - Conectar a la base de datos
        - Obtener parámetros de configuración
        - Crear estructura de directorios
        - Crear scripts de redefinición por cada tabla
    """
    conexion = conecta_db(config,logger)    
    exit()
    sid_db,parallel,habilita,tablespace_tabla,tablespace_index = get_parametros_tbs(config,logger)
    tablas = config.options('Tablas')
    for tabla in tablas:
        esquema,tabla,columnas = get_parametros_tablas(config,tabla,logger)

        logger.debug(f"Procesando tabla {esquema}.{tabla} columnas a encriptar {columnas}")

        # Creamos la estructura de directorios  por sid, esquema y tabla
        crea_directorio(dir_proyecto,"SQL", sid_db, esquema, tabla)

        # Creamos los scripts de redefinición
        crea_scripts_redefinicion(dir_proyecto,conexion,sid_db, esquema, tabla,columnas,habilita,tablespace_tabla,tablespace_index,parallel) 

