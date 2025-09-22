import oracledb
import sys

def conecta_db(config,logger):
    """Función para conectar a la base de datos Oracle usando los parámetros del archivo de configuración."""
    logger.debug("Iniciando conexión a la base de datos.")      

    try:
        conecta = oracledb.connect(
            user=config.get('Database','usuario'),
            password=config.get('Database','clave'),
            host=config.get('Database','servidor'),
            port=config.getint('Database','port'),
            service_name=config.get('Database','servicio')
        )
        logger.debug("Conexión a la base de datos establecida con éxito.")
        return conecta
    except oracledb.DatabaseError as e:
        error, = e.args
        logger.critical(f"{error.message}")
        sys.exit(1)

def get_parametros_tbs(config):
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

    return sid_db, parallel, habilita, tablespace_tabla, tablespace_index

def get_parametros_tablas(config,opt):
    esquema = opt.split('.')[0].upper()
    tabla = opt.split('.')[1].upper()
    valores = config.get('Tablas',opt)
    if len(valores) > 0: 
        columnas = [col.strip() for col in config.get('Tablas',opt).split(',')]
    else:
        columnas=[]    

    return esquema,tabla,valores,columnas