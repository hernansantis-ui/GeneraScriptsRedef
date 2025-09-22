
import sys
import re

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
    logger.debug(f"Obteniendo parámetros para la tabla {opt} desde el archivo de configuración.")
    try:
        esquema = opt.split('.')[0].upper()
        tabla = opt.split('.')[1].upper()
        valores = config.get('Tablas',opt)
        if len(valores) > 0: 
            columnas = [col.strip() for col in config.get('Tablas',opt).split(',')]
        else:
            columnas=[]    
        logger.debug(f"Parámetros obtenidos para {esquema}.{tabla}: Columnas a encriptar={columnas}")
        return esquema, tabla, columnas
    except Exception as e: 
        logger.critical(f"Error al obtener parámetros para la tabla {opt}: {str(e)}")
        sys.exit(1)

def crea_directorio(dir_proyecto,path_inicio, sid_db, esquema, tabla):
    ruta = dir_proyecto / path_inicio / sid_db / esquema / tabla
    ruta.mkdir(parents=True, exist_ok=True)

def cambia_tablespace(ddl_objeto,tablespace):
    patron = r'.*(TABLESPACE\s*\w+)'
    matches = re.finditer(patron,ddl_objeto)
    for match in matches:
        linea = match.group()
        ddl_objeto = ddl_objeto.replace(linea,f'TABLESPACE {tablespace}')
    return ddl_objeto

def ddl_incorpora_compresion(ddl_indices):
#   Buscamos la palabra TABLESPACE e incorporamos la compresion de indices antes
    patron=r'.*(TABLESPACE\s*\w+)'
    match = re.finditer(patron,ddl_indices)
    for linea in match:
        linea_nueva = f'  COMPRESS ADVANCED LOW \n  {linea.group()} '
        ddl_indice = ddl_indices.replace(linea.group(),linea_nueva)
    return ddl_indice

def encripta_columnas(ddl_tabla,columnas):
    for col in columnas:
        patron = fr'.*{col}.*(VARCHAR2|NUMBER).*\(\d+(,.*\d+|.*CHAR.*)\)\s*(,|'')'
        match = re.search(patron,ddl_tabla)
        if match:
            ini = match.start()
            fin = match.end()
            linea=ddl_tabla[ini:fin].strip()

    #  La linea con la columna esta encontrada
    #  falta determinar si tiene coma al final o no
        patron=fr'^.*{col}.*\(.*\).*(,)$'
        match = re.search(patron,linea)
        if match == None:  # No tiene coma
            linea_nueva=f"{linea} ENCRYPT USING 'AES256' NO SALT "
        else:     # Tiene coma al final
            fin=match.end()
            ini=match.start()       
            linea_nueva=f"{linea[ini:fin-1]} ENCRYPT USING 'AES256' NO SALT ,"
        ddl_tabla = ddl_tabla.replace(linea,linea_nueva)

    return ddl_tabla
