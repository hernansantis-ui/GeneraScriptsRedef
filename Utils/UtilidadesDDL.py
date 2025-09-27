import sys
import re
def generador_archivo(nombre_archivo, logger):
    logger.debug(f'Generador para leer el archivo DDL {nombre_archivo}')   
    with open(nombre_archivo, 'r') as archivo:
        for linea in archivo:
            yield linea.strip()

def obtener_lista_indices(script_300,esquema,logger):
    logger.debug(f'{esquema=}, {script_300}')
    lista_indices=[]
    lineas_archivo = generador_archivo(script_300,logger)
    patron = rf'{esquema}\.I_(\$|\w+)+'   
    for linea in lineas_archivo:
        match = re.search(patron,linea)
        if match:
            grupo=match.group(0)
            lista_indices.append(grupo.split('.')[1][2:])
    
    return lista_indices

def modificar_script_300(sql_dir,script_300,lista_nueva,lista_vieja,logger):
    pass
    logger.debug('Modificamos el script 300 con los nuevos nombres de indices')
    archivo_salida = sql_dir/'temporal.sql'

    lineas_archivo = generador_archivo(script_300,logger)
    with open(archivo_salida,'w') as archivo:
        for linea in lineas_archivo:
            for contador in range(len(lista_vieja)):
                indice = lista_vieja[contador]
                linea = linea.replace(indice,lista_nueva[contador])
            archivo.write(linea+'\n')            
    script_300.unlink()
    archivo_salida.rename(script_300)

def verificar_largo_indices(sql_dir,script_300,lista_indices,logger):
    lista_nueva=[]
    contador = 1
    for indice in lista_indices:
        if len(indice) > 28:
            # Si el largo es mayor a 28, debemos eliminar los
            # últimos 2 caracteres y reemplazar por un contador
            n_indice = f'{indice[0:-2]}{contador:02d}'
            contador +=1
        else:
            n_indice = indice            
        lista_nueva.append(n_indice)
    if contador > 1 :    
        modificar_script_300(sql_dir,script_300,lista_nueva,lista_indices,logger)        
    return lista_nueva

def llena_template_303(sql_dir,esquema, tabla, lista_indices, lista_original, archivo_salida, template, logger):
    
    with open(template, "r") as archivo:
        texto = archivo.read()

    with open(archivo_salida, "w") as archivo:
        for i in range(len(lista_original)):
            archivo.write(
                texto.replace("TABLA", tabla)
                .replace("ESQUEMA", esquema)
                .replace("INDICE_ORIGINAL", lista_original[i])
                .replace("INDICE_NUEVO",lista_indices[i])
            )
            archivo.write("\n")
        archivo.write("EXIT")

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
        patron = r".*(TABLESPACE\s*\w+)"

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
                    patron = rf".*{col}.*(VARCHAR2|NUMBER).*\(\d+(,.*\d+|.*CHAR.*)*\)"
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
        patron = f'{esquema}.'
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

    try:
        lineas_archivos = generador_archivo(archivo_redef,logger)
        patron=r'.*(TABLESPACE\s*\w+)'
        with open(archivo_salida,'w') as archivo:
            for linea in lineas_archivos:
                match = re.search(patron,linea)
                if match:
                    grupo = match.group(0)
                    linea = linea.replace(grupo,f'COMPRESS ADVANCED LOW \n{grupo}')
                archivo.write(linea+'\n')
        archivo_redef.unlink()
        archivo_salida.rename(archivo_redef)
        logger.debug("Compresión avanzada incorporada correctamente en el DDL de índices.")
    except Exception as e:
        logger.critical(f"Error al incorporar compresión en el DDL de índices: {str(e)}")
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
