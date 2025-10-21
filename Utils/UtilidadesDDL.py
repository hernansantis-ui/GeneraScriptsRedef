import sys
import re

def generador_archivo(nombre_archivo, logger):
    logger.debug(f'Generador para leer el archivo DDL {nombre_archivo}')   
    with open(nombre_archivo, 'r') as archivo:
        for linea in archivo:
            yield linea.strip()

def obtener_dict_indices(script_300,esquema,logger):
    logger.debug(f'{esquema=}, {script_300}')
    dict_indices={}
    lineas_archivo = generador_archivo(script_300,logger)
    patron = rf'{esquema}\.I_(\$|\w+)+'   
    for linea in lineas_archivo:
        match = re.search(patron,linea)
        if match:
            grupo=match.group(0)
            dict_indices[grupo.split('.')[1][2:]]=None
    
    return dict_indices

def modificar_script_300(sql_dir,script_300,dict_indices,logger):
    pass
    logger.debug('Modificamos el script 300 con los nuevos nombres de indices')
    archivo_salida = sql_dir/'temporal.sql'

    lineas_archivo = generador_archivo(script_300,logger)
    with open(archivo_salida,'w') as archivo:
        for linea in lineas_archivo:
            for key,indice in dict_indices.items():
                linea = linea.replace(key,indice)
            archivo.write(linea+'\n')            
    script_300.unlink()
    archivo_salida.rename(script_300)


def verificar_largo_indices(sql_dir,script_300,dict_indices,logger):
    LARGO_INDICE=28
    contador = 1
    for indice in dict_indices.keys():
        if len(indice) > LARGO_INDICE:
            # Si el largo es mayor a LARGO_INDICE, debemos eliminar los
            # últimos 2 caracteres y reemplazar por un contador
            valor_indice = f'{indice[0:-4]}{contador:02d}'
            contador +=1
        else:
            valor_indice = indice            
        dict_indices[indice]=valor_indice    
    if contador > 1 :    # Algun indice resulto mayor al LARGO_INDICE
        modificar_script_300(sql_dir,script_300,dict_indices,logger)        
    return dict_indices

def llena_template_303(sql_dir,esquema, tabla, dict_indices, archivo_salida, template, logger):
    logger.debug('Llenamos el template 303')
    try:
        with open(template, "r") as archivo:
            texto = archivo.read()

        with open(archivo_salida, "w") as archivo:
            for indice_original,indice_nuevo in dict_indices.items():
                archivo.write(
                    texto.replace("TABLA", tabla)
                    .replace("ESQUEMA", esquema)
                    .replace("INDICE_ORIGINAL", indice_original)
                    .replace("INDICE_NUEVO",indice_nuevo)
                )
                archivo.write("\n")
            archivo.write("EXIT")
    except Exception as e:
        logger.critical(f"Error al rellenar template 303: {str(e)}"
        )
        sys.exit(1)

def separa_ddl_indices(ddls_dir,esquema, tabla, archivo_salida, logger):
    """ Función para separar el DDL de los índices en un archivos distinto
    """
    logger.debug(f'Separando DDL de los índices de la tabla {tabla} en un archivo distinto')   
    archivo_entrada= ddls_dir / f"{esquema}.{tabla}.sql"   
 
    try:
        lineas = generador_archivo(archivo_entrada, logger)
        with open(archivo_salida, 'w') as archivo:
            es_ddl_indice = False
            for linea in lineas:
                if 'CREATE INDEX' in linea or 'CREATE UNIQUE INDEX' in linea :
                    es_ddl_indice = True
                if 'ALTER TABLE' in linea:
                    es_ddl_indice = False    
                if es_ddl_indice:
                    archivo.write(linea+'\n')
    except Exception as e:
        logger.critical(f'Error inesperado en procesamiento tabla {archivo_entrada}: {e}')
        raise SystemExit()  
    else:
        logger.debug(f'DDL de los índices de la tabla {tabla} separados correctamente en un archivo distinto')

def separa_ddl_tabla(ddls_dir,esquema, tabla, archivo_salida, logger):
    """ Función para separar el DDL de la tabla del archivo entregado
    """
    logger.debug(f'Separando DDL de la tabla {tabla}  y comentarios')   
    archivo_entrada= ddls_dir/ f"{esquema}.{tabla}.sql"    
    try:
        lineas = generador_archivo(archivo_entrada, logger)
        with open(archivo_salida, 'w') as archivo:
            es_ddl_tabla = True
            for linea in lineas:
                if 'ALTER ' in linea or 'DROP ' in linea:  
                    es_ddl_tabla = False
                if 'CREATE TABLE' in linea: 
                    es_ddl_tabla = True
                elif 'COMMENT ' in linea:
                    es_ddl_tabla = True
                elif 'CREATE INDEX' in linea or 'CREATE UNIQUE ' in linea :
                    es_ddl_tabla = False
                if es_ddl_tabla:
                    archivo.write(linea+'\n')
    except Exception as e:
        logger.critical(f'Error inesperado en procesamiento tabla {archivo_entrada}: {e}')
        raise SystemExit()  
    else:
        logger.debug(f'DDL de la tabla {tabla} y DDL de los índices separados correctamente en archivos distintos') 

def reemplaza_tabs_comillas(sql_dir,esquema, tabla, archivo_redef, logger):
    """ Función para reemplazar los tab por espacios 
        y eliminar las comillas en el script de redefinicion de la tabla
    """
    logger.debug(f'Reemplazando tab por espacios en el archivo {archivo_redef}')   
    archivo_salida =  sql_dir/f"temporal.sql"   
    try:
        lineas = generador_archivo(archivo_redef, logger)
        with open(archivo_salida, 'w') as archivo:
            for linea in lineas:
                linea = linea.expandtabs(tabsize=1)  # Reemplaza tab por 1 espacios
                linea = linea.replace('"','')
                archivo.write(linea+'\n')
    except Exception as e:
        logger.critical(f'Error inesperado en procesamiento tabla {tabla}: {e}')
        raise SystemExit()  
    archivo_redef.unlink()  # Elimina el archivo original
    archivo_salida.rename(archivo_redef)
    logger.debug(f'Tab y comillas reemplazados por espacios en el archivo {archivo_redef} correctamente')

def cambia_tablespace(sql_dir,archivo_redef, tablespace, logger):
    logger.debug(f"Cambiando tablespace a {tablespace} en el DDL del objeto.")
    #   Buscamos la palabra TABLESPACE y cambiamos el tablespace por el indicado
    archivo_salida =  sql_dir/"temporal.sql"   
    try:
        lineas_archivo = generador_archivo(archivo_redef,logger)
        #patron = r".*(TABLESPACE\s*)(\w|\w(_\w)*)"
        patron=r'.*(TABLESPACE\s*)(\w+)'
        with open(archivo_salida,'w') as archivo:

            for linea in lineas_archivo:
                match = re.search(patron, linea)
                if match :
                    linea_old = match.group()
                    linea = linea.replace(linea_old, f"TABLESPACE {tablespace}")
                archivo.write(linea+'\n')
        archivo_redef.unlink() 
        archivo_salida.rename(archivo_redef)
        logger.debug("Cambio de tablespace realizado correctamente.")
    except Exception as e:
        logger.critical(f"Error al cambiar tablespace en el DDL: {str(e)}")
        sys.exit(1)

def encripta_columnas(sql_dir,archivo_redef,columnas, logger):
    logger.debug(f"Incorporando encriptación en las columnas: {columnas}")
    #   Buscamos las columnas en el DDL y les incorporamos la cláusula de encriptación
    archivo_salida = sql_dir / 'temporal.sql'
    try:
        lineas_archivo = generador_archivo(archivo_redef,logger)
        with open(archivo_salida,'w') as archivo: 
            for linea in lineas_archivo:
                for col in columnas:
                    patron = rf"^{col}\s*(VARCHAR2|NUMBER).*\(\d+(,.*\d+|.*CHAR.*|.*BYTE.*)*\)"
                    match = re.search(patron, linea)
                    if match:
                        grupo = match.group(0)
                        linea = linea.replace(grupo,f"{grupo} ENCRYPT USING 'AES256' NO SALT ")
                archivo.write(linea+'\n')
        archivo_redef.unlink()
        archivo_salida.rename(archivo_redef)
        logger.debug("Encriptación correcta en el DDL de la tabla.")
    except Exception as e:
        logger.critical(
            f"Error al incorporar encriptación en el DDL de la tabla: {str(e)}"
        )
        sys.exit(1)

def cambia_nombre_a_interino(sql_dir,archivo_redef,esquema,logger):
    logger.debug(f"Cambiando nombre a interino")
    archivo_salida = sql_dir / "temporal.sql"
    try:
        lineas_archivo = generador_archivo(archivo_redef,logger)
        patron = fr'{esquema}\.'
        with open(archivo_salida,'w') as archivo:
            for linea in lineas_archivo:
                match = re.search(patron,linea)
                if match:
                    grupo=match.group(0)
                    linea = linea.replace(grupo,f'{esquema}.I_')
                archivo.write(linea+'\n')
        archivo_redef.unlink()
        archivo_salida.rename(archivo_redef)
        logger.debug("Cambio a tabla interina  correcto en el DDL de la tabla.")
                    
    except Exception as e:
        logger.critical(f"Error al incorporar encriptación en el DDL de la tabla: {str(e)}")
        sys.exit(1)

def agrega_compresion_indice(sql_dir,archivo_redef,logger):
    logger.debug("Incorporando compresión avanzada en el DDL de índices.")
    #   Buscamos la palabra TABLESPACE e incorporamos la compresion de indices antes
    archivo_salida = sql_dir /"temporal.sql"
    unique_index = False  # Indica bloque Unique Index
    comprimir = False     # Indica que se debe comprimir
    fin_bloque = True    # Indica que se acaba el bloque (CREATE... )
    try:
        lineas_archivos = generador_archivo(archivo_redef,logger)
#   1.- Primero buscamos CREATE INDEX o CREATE UNIQUE 
#   2.- Si es CREATE INDEX buscamos TABLESPACE y agregamos la compresión
#   3.- Si es CREATE UNIQUE buscamos cuantas columnas tiene el indice
#   4.- Si tiene mas de una buscamos TABLESPACE y agregamos la compresion
#   5.- Si solo tiene una volvemos al punto 1.

        buscar_tablespace = False

        patron=r'.*(TABLESPACE\s*\w+)'
        lineas_archivo = generador_archivo(archivo_redef,logger)
        with open(archivo_salida,'w') as archivo:
            for linea in lineas_archivo:
                match linea :
#                    case s if match_obj := re.search(r"\s*CREATE\s*(UNIQUE)\s*INDEX\s*(\(\w.*(,\w.*)?\))", s ):
                    case s if match_obj := re.search(r"\s*CREATE\s*(UNIQUE)\s*INDEX\s*((\((\w.*(,\w.*)?)\))?)", s ):
                        unique_index = True
                        fin_bloque = False
                        if (match_obj := re.search(r"(\(\w.*(,\w.*)?\))",s)):
                            columnas = match_obj.group(0).strip('(').strip(')').split(',')
                            comprimir = len(columnas) > 1
                    case s if (match_obj := re.search(r"(\(\w.*(,\w.*)?\))",s)):
                        if unique_index :
                            columnas = match_obj.group(0).strip('(').strip(')').split(',')
                            comprimir = len(columnas) > 1
                    case s if (match_obj := re.search(r"\s*CREATE\s*INDEX.*",s)):
                        fin_bloque = False
                        comprimir = True  
                    case s if (match_obj := re.search(r'.*NOPARALLEL;', s)):
                        if not fin_bloque:
                            unique_index = False
                            fin_bloque = True
                    case s if (match_obj := re.search(r'.*(TABLESPACE\s*)(\w+)',s)):
                        if comprimir:
                            grupo = match_obj.group(0)
                            linea = linea.replace(grupo,f'COMPRESS ADVANCED LOW \n{grupo}')
                            comprimir = True
                    case _:
                        pass
                            
                archivo.write(linea+'\n')
        archivo_redef.unlink()
        archivo_salida.rename(archivo_redef)
        logger.debug("Compresión avanzada incorporada correctamente en el DDL de índices.")
    except Exception as e:
        logger.critical(f"Error al incorporar compresión en el DDL de índices: {str(e)}")
        raise SystemError()

def agrega_compresion_tabla(sql_dir, archivo_redef, logger):
    logger.debug("Incorporando compresión avanzada en el DDL de tabla.")
    #   Buscamos la palabra TABLESPACE e incorporamos la compresion de tabla antes
    archivo_salida = sql_dir /"temporal.sql"

    try:
        lineas_archivos = generador_archivo(archivo_redef,logger)
        patron=r'.*(TABLESPACE\s*\w+)'
        with open(archivo_salida,'w') as archivo:
            for linea in lineas_archivos:
                if 'NOCOMPRESS' not in linea:
                    match = re.search(patron,linea)
                    if match:
                        grupo = match.group(0)
                        linea = linea.replace(grupo, f"ROW STORE COMPRESS ADVANCED\n{grupo}" )
                    archivo.write(linea+'\n')
        archivo_redef.unlink()
        archivo_salida.rename(archivo_redef)
        logger.debug("Compresión avanzada incorporada correctamente en el DDL de tablas.")
    except Exception as e:
        logger.critical(f"Error al incorporar compresión en el DDL de tablas: {str(e)}")
        raise SystemError()


def agrega_paralelismo(sql_dir,archivo_redef,parallel,logger):
    logger.debug("Agregando sentencias para ejecutar paralelismo en la creacion de los indices")
    archivo_salida = sql_dir /'temporal.sql'
    try:
        lineas_archivo= generador_archivo(archivo_redef,logger)
        with open(archivo_salida,'w') as archivo:
            archivo.write(f'ALTER SESSION FORCE PARALLEL DML parallel {parallel};\n')
            archivo.write(f'ALTER SESSION FORCE PARALLEL DDL parallel {parallel};\n')
            archivo.write(f'ALTER SESSION FORCE PARALLEL QUERY parallel {parallel};\n\n')
            for linea in lineas_archivo:
                archivo.write(linea+'\n')
        archivo_redef.unlink()
        archivo_salida.rename(archivo_redef)
        logger.debug("Compresión avanzada incorporada correctamente en el DDL de índices." )
    except Exception as e:
        logger.critical(f'Error al agregar paralelismo el script de indices (300): {str(e)}')
        raise SystemError()

def crea_script_from_ddl(ddls_dir,sql_dir,archivo_tabla, esquema, tabla,logger,indices):      
    """ Función para crear los scripts de redefinición de tablas los DDL's de las tablas
        - Crea script de redefinición por cada tabla desde DDL
        - Crea script de redefinicion de  indices  para la tabla desde DDL
    """
    try:
        if not indices:
            separa_ddl_tabla(ddls_dir,esquema, tabla, archivo_tabla, logger)
        else:
            separa_ddl_indices(ddls_dir,esquema, tabla, archivo_tabla, logger)
    except Exception as e:
        logger.critical(f'Error inesperado al crear los scripts {archivo_tabla}: {e}')
        raise SystemExit()  
    else:
        logger.debug(f'Scripts de redefinición {archivo_tabla} creado correctamente')
