def generador_archivo(nombre_archivo, logger):
    logger.debug(f'Generador para leer el archivo DDL {nombre_archivo}')   
    with open(nombre_archivo, 'r') as archivo:
        for linea in archivo:
            yield linea.strip()

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

def reemplaza_espacios(sql_dir,esquema, tabla, archivo_entrada, logger):
    """ Función para reemplazar los tab por espacios 
        y eliminar las comillas en el script de redefinicion de la tabla
    """
    logger.debug(f'Reemplazando tab por espacios en el archivo DDL de la tabla {esquema}.{tabla}')   
    archivo_salida =  sql_dir/f"temp_{tabla}.sql"   
    try:
        lineas = generador_archivo(archivo_entrada, logger)
        with open(archivo_salida, 'w') as archivo:
            logger.debug(f'Procesando archivo {archivo_entrada} para reemplazar tab por espacios y eliminar dobles comillas')
            for linea in lineas:
                linea = linea.expandtabs(tabsize=1)  # Reemplaza tab por 2 espacios
                linea = linea.replace('"','')
                archivo.write(linea+'\n')
    except Exception as e:
        logger.critical(f'Error inesperado en procesamiento tabla {tabla}: {e}')
        raise SystemExit()  
    archivo_entrada.unlink()  # Elimina el archivo original
    archivo_salida.rename(archivo_entrada)
    logger.debug(f'Tab y comillas reemplazados por espacios en el archivo {archivo_entrada} correctamente')

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
        reemplaza_espacios(sql_dir,esquema, tabla, archivo_tabla,logger)
    except Exception as e:
        logger.critical(f'Error inesperado al crear los scripts {archivo_tabla}: {e}')
        raise SystemExit()  
    else:
        logger.debug(f'Scripts de redefinición {archivo_tabla} creado correctamente')

