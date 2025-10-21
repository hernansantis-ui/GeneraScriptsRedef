from Utils.baseDatos     import (
                                crea_script_tabla_from_db,
                                crea_script_indices_from_db,
                                )
from Utils.UtilidadesDDL import (
    obtener_dict_indices,
    cambia_nombre_a_interino,
    cambia_tablespace,
    crea_script_from_ddl,
    reemplaza_tabs_comillas,
    encripta_columnas,
    agrega_compresion_indice,
    agrega_compresion_tabla,
    verificar_largo_indices,
    agrega_paralelismo,
    llena_template_303
)
from Utils.utilitariosSys        import (
                                crea_directorio_SQL, 
                                get_parametros_tablas,
                                get_parametros_tbs,
                                is_archivo_vacio
                               )
import logging
logger = logging.getLogger('main.creaScripts')

def crea_script_redef_300(dir_proyecto,sql_dir,config,archivo_salida,esquema, tabla):
    """
        Funcion para la creación del script de redeficion 300_CREA_INDEX_I...sql

    """

    logger.debug(f"Creando scripts de redefinición {archivo_salida} ")
    acceso_base = config.getboolean('default','acceso_base')
    habilita, tablespace = get_parametros_tbs(config,indice=True)
    parallel = config.getint("Tablespaces", "paralelo")

    try:
        if not acceso_base :
            # Se crea script desde el DDL
            ddls_dir = dir_proyecto/'DDLS'
            crea_script_from_ddl(ddls_dir,sql_dir,archivo_salida,esquema,tabla,indices=True)

        else:
            # Se crea script desde la base
            crea_script_indices_from_db(config, esquema, tabla, archivo_salida)
        # Verificamos que el archivo de indices no este vacio
        if is_archivo_vacio(archivo_salida):
            pass
        else:    
            # reemplazamos tabs y comillas dobles
            reemplaza_tabs_comillas(sql_dir, esquema, tabla, archivo_salida)
            # Se cambia el nombres de tabla a tabla interina(I_"tabla")
            cambia_nombre_a_interino(sql_dir, archivo_salida, esquema)
            # Se cambia el nombre de los tablespaces, si aplica
            if habilita and tablespace != None:
                cambia_tablespace(sql_dir, archivo_salida, tablespace)

            # Se agrega la sentencia de compresion
            agrega_compresion_indice(sql_dir, archivo_salida)
            # Agrega el paralelismo, si aplica
            if parallel != 0 :
                agrega_paralelismo(sql_dir,archivo_salida,parallel)
            
    except Exception as e:
        logger.critical(f'Error inesperado al crear  {archivo_salida} : {e}')
        raise SystemExit()  
    else:
        logger.debug(f'Scripts de redefinición {archivo_salida} creados correctamente ')  

def crea_script_redef_100(dir_proyecto,sql_dir,config,archivo_salida, esquema, tabla,columnas):
    """ Función para crear el script de redefinicion 01_CREA_I...sql
    """
    logger.debug(f"Creando scripts de redefinición {archivo_salida} ")
    acceso_base = config.getboolean('default','acceso_base')
    habilita, tablespace = get_parametros_tbs(config,indice=False)
    try:
        if not acceso_base :
            # Se crea script desde el DDL
            ddls_dir = dir_proyecto/'DDLS'
            crea_script_from_ddl(ddls_dir,sql_dir,archivo_salida,esquema,tabla,indices=False)
        else:
            # Se crea script desde la base
            crea_script_tabla_from_db(config,esquema, tabla, archivo_salida)

        # reemplazamos tabs y comillas dobles
        reemplaza_tabs_comillas(sql_dir, esquema, tabla, archivo_salida)
        # Se cambia el nombre de los tablespaces, si aplica
        if habilita and tablespace != None:
            cambia_tablespace(sql_dir, archivo_salida, tablespace)
        # Se encriptan las columnas, si hay
        encripta_columnas(sql_dir,archivo_salida,columnas)
        # Incorpora parametros de compresion de tabla
        agrega_compresion_tabla(sql_dir, archivo_salida)
        # Se cambian el nombre de la tabla a tabla interina (I_"tabla")
        cambia_nombre_a_interino(sql_dir, archivo_salida, esquema)
    except Exception as e:
        logger.critical(f'Error inesperado al crear el scripts {archivo_salida}: {e}')
        raise SystemExit()  
    else:
        logger.debug(f'Scripts de redefinición {archivo_salida} creados correctamente ')  

def crea_sript_redef_303(sql_dir, archivo_salida, script_300, esquema, tabla, template):
    logger.debug(f"Creando scripts de redefinición {archivo_salida} ")
    if is_archivo_vacio(script_300):
        script_300.unlink()
        pass
    else:
        #   Obtener la lista de indices desde el script_300
        logger.debug(f'Obteniendo diccionario de indices originales')
        dict_indices = obtener_dict_indices(script_300, esquema)
        #   Verificar los indices con mas de 28 caracteres
        logger.debug(f'Completa indices originales con nuevos nombres')
        dict_indices = verificar_largo_indices(sql_dir, script_300, dict_indices)
        #   Componer los nombres de los indices en script_300, si aplica
        #   Rellenar el template REGISTER
        logger.debug(f'Rellena el template con los indices originales y los nuevos')
        llena_template_303(sql_dir,esquema, tabla, dict_indices, archivo_salida,template)

def crea_script_redef_general(template,archivo_script,esquema,tabla,parallel):
    with open(template, "r") as archivo:
        texto = archivo.read()
    with open(archivo_script, "w") as archivo:
        texto = texto.replace("TABLA", tabla).replace("ESQUEMA", esquema).replace('paralelo',str(parallel))
        archivo.write(texto)


def crea_scripts_redefinicion(dir_proyecto,sql_dir,config,base_dato, esquema, tabla,columnas):      
    """ Función para crear los scripts de redefinición de tablas los DDL's de las tablas
        - Crear scripts de redefinición por cada tabla desde DDL
    """
    SCRIPTS = [
        ("000", "CAN_REDEF"),
        ("100", "CREA_I"),
        ("200", "START"),
        ("300", "CREA_INDEX_I"),
        ("303", "REGISTER"),
        ("309", "COPY"),
        ("400", "SYNCHRONIZE"),
        ("500", "FINISH"),
        ("600", "ABORT"),
        ("700", "ROLLBACK"),
        ("990", "DROP"),
    ]

    TEMPLATE_DIR = dir_proyecto/'templates'

    logger.debug(f"Creando scripts de redefinición para la tabla {esquema}.{tabla} desde DDL")
    parallel = config.getint('Tablespaces','paralelo')
    try:
        for orden, tipo in SCRIPTS:
            archivo_script = sql_dir/base_dato/esquema/tabla/ f"{orden}_{tipo}_{tabla}.sql"
            if orden == '300':
                script_300 = archivo_script
            template = TEMPLATE_DIR/f"ESQ_{tipo}.txt"
            if orden == '100':
                crea_script_redef_100(
                    dir_proyecto,
                    sql_dir,
                    config,
                    archivo_script,
                    esquema,
                    tabla,
                    columnas
                )
            elif  orden == '300' :
                crea_script_redef_300(dir_proyecto,sql_dir,config,archivo_script,esquema, tabla)
            elif orden == "303":
                logger.debug(f'Archivo {archivo_script}')
                crea_sript_redef_303(sql_dir,archivo_script,script_300,esquema,tabla,template)
            else:  # orden not in ('303'):
                logger.debug(f"Archivo {archivo_script}")
                crea_script_redef_general(template,archivo_script,esquema,tabla,parallel)
    except Exception as e:
        logger.critical(f'Error inesperado al crear los scripts de redefinición {archivo_script} : {e}')
        raise SystemExit()  
    else:
        logger.debug(f'Scripts de redefinición creados ')

def inicia_scripts_redefinicion(dir_proyecto,config):
    """ Función para iniciar la creación de los scripts de redefinición de tablas
        - Obtener parámetros de configuración de tablespaces 
        - Obtener lista de tablas a procesar
        - Por cada tabla:   
            - Crear estructura de directorios
            - Crear scripts de redefinición por cada tabla 
    """
    SQL_DIR = dir_proyecto /'SQL'
    logger.debug("Inicio del proceso de creación de scripts para redefinición de tablas")
    base_dato= config.get('default','base_dato')
    opciones = config.options('Tablas')
    for opt in opciones:
        esquema,tabla,columnas = get_parametros_tablas(config,opt) 
        logger.debug(f"Procesando tabla {esquema}.{tabla} columnas a encriptar {columnas}") 
        # Creamos la estructura de directorios  por sid, esquema y tabla
        crea_directorio_SQL(SQL_DIR,base_dato,esquema, tabla)  
        # Creamos los scripts de redefinición
        crea_scripts_redefinicion(dir_proyecto,SQL_DIR,config,base_dato,esquema, tabla,columnas)

    logger.debug("Proceso de creación de scripts finalizado")   
