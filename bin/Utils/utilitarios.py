
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

def crea_directorio(dir_proyecto,path_inicio, sid_db, esquema, tabla,logger):
    logger.debug(f"Creando directorio para SID={sid_db}, Esquema={esquema}, Tabla={tabla}")
    try:
        ruta = dir_proyecto / path_inicio / sid_db / esquema / tabla
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
