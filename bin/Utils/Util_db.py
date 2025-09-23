import oracledb
import sys
from Utils.utilitarios import cambia_tablespace, ddl_incorpora_compresion, encripta_columnas

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
    except Exception as e:
        logger.critical(f"Error inesperado al conectar a la base de datos: {str(e)}")
        sys.exit(1) 

def crea_script_ddl_tabla(conexion, tipo, esquema, tabla, archivo_salida,columnas,tablespace,habilita,logger):
    cursor = conexion.cursor()
    cursor.execute(
        """ 
         begin 
            dbms_metadata.set_transform_param(DBMS_METADATA.SESSION_TRANSFORM,'PRETTY', true) ;
            dbms_metadata.set_transform_param(DBMS_METADATA.SESSION_TRANSFORM,'CONSTRAINTS', false); 
            dbms_metadata.set_transform_param(DBMS_METADATA.SESSION_TRANSFORM,'REF_CONSTRAINTS', false); 
            dbms_metadata.set_transform_param(DBMS_METADATA.SESSION_TRANSFORM,'SQLTERMINATOR', true); 
            dbms_metadata.set_transform_param(DBMS_METADATA.SESSION_TRANSFORM,'TABLE_COMPRESSION_CLAUSE','ROW STORE COMPRESS ADVANCED');
         end;"""
    )
    #   Extraemos el DDL de la tabla
    cursor.execute(
        """
        select dbms_metadata.get_ddl('TABLE',:p_tabla,:p_esquema) from dual
          """,
        p_tabla=tabla,
        p_esquema=esquema,
    )
    resultado = cursor.fetchone()
    ddl_tabla = resultado[0].read()
    # Eliminamos los tabs
    ddl_tabla = ddl_tabla.expandtabs(tabsize=2)
     # Eliminamos las doble comillas 
    ddl_tabla = ddl_tabla.replace('"','')
    # Verificamos si hay columnas para encriptar
    if len(columnas) > 0:
        ddl_tabla = encripta_columnas(ddl_tabla,columnas,logger)

    # Verificamos si debemos cambiar el tableespace
    if habilita and tablespace != None:
        ddl_tabla = cambia_tablespace(ddl_tabla,tablespace,logger)
    # Transforma el nombre de la tabla a interina
    ddl_tabla = ddl_tabla.replace(f'{esquema}.{tabla}',f'{esquema}.I_{tabla}')
    #   Extraemos los comentarios de la tabla
    cursor.execute(
        """
            select 'COMMENT ON COLUMN '||owner||'.'||table_name||'.'||column_name||' IS '''||comments||''' ;' 
            from dba_col_comments
            where owner=:p_esquema
            and table_name =:p_tabla 
            and comments is not null
        """,
        p_tabla=tabla,
        p_esquema=esquema,
    )
    lista_comentarios = cursor.fetchall()
    comentarios = [comen[0].replace(f'{esquema}.{tabla}',f'{esquema}.I_{tabla}') + "\n" for comen in lista_comentarios]

    cursor.close()
    # cambiamos el nombre de la tabla en los comentarios
    
    with open(archivo_salida, "w") as archivo:
        archivo.write(ddl_tabla + "\n")
        archivo.writelines(comentarios)
        archivo.write('EXIT')

def obtener_lista_indices(conexion,esquema,tabla,logger):
    cursor = conexion.cursor()

    cursor.execute(
        """
            select index_name from all_indexes where owner=:p_esquema and table_name = :p_tabla
        """
        ,p_esquema = esquema,p_tabla=tabla
    )
    resultado = cursor.fetchall()
    lista = [l[0] for l in resultado]
    return lista

def crea_script_ddl_indices(conexion, tipo, esquema, tabla, archivo_salida,tablespace,habilita,parallel,logger):
    cursor = conexion.cursor()
    cursor.execute(
        """ 
         begin 
            dbms_metadata.set_transform_param(DBMS_METADATA.SESSION_TRANSFORM,'PRETTY', true) ;
            dbms_metadata.set_transform_param(DBMS_METADATA.SESSION_TRANSFORM,'SQLTERMINATOR', true); 
         end;"""
    )
    cursor.execute(
        """    
            select dbms_metadata.get_dependent_ddl('INDEX', :p_tabla ,:p_esquema)  from dual
        """
        ,p_tabla=tabla,p_esquema=esquema
    )
    resultado = cursor.fetchone()
    ddl_indices = resultado[0].read()

    cursor.close()
    # Eliminamos los tabs
    ddl_indices = ddl_indices.expandtabs(tabsize=2)

#   Eliminamos las comillas en los indices
    ddl_indices = ddl_indices.replace('"','')
#   Verificamos si debemos cambiar el tablespace
    if habilita and tablespace != None:
        ddl_indices = cambia_tablespace(ddl_indices,tablespace,logger)


#   Agregamos la sentencia de compersion de indices
    ddl_indices = ddl_incorpora_compresion(ddl_indices,logger)
        
#   Cambiamos el nombre de los indices para hacerlos interinos
    ddl_indices = ddl_indices.replace(f'{esquema}.',f'{esquema}.I_')    
#   Debemos agregar la sentica que comprime el indice
        

    with open(archivo_salida, "w") as archivo:
        if parallel != 0 :
            archivo.write(f'  ALTER SESSION FORCE PARALLEL DML parallel {parallel};\n')
            archivo.write(f'  ALTER SESSION FORCE PARALLEL DDL parallel {parallel};\n')
            archivo.write(f'  ALTER SESSION FORCE PARALLEL QUERY parallel {parallel};\n')

        archivo.write(ddl_indices)
        archivo.write('\n  EXIT')

def llena_template_register(tipo, esquema, tabla, lista_indices, archivo_salida, template,logger):

    with open(template, "r") as archivo:
        texto = archivo.read()

    with open(archivo_salida, "w+") as archivo:
        for indice in lista_indices:
            archivo.write(
                texto.replace("TABLA", tabla)
                .replace("ESQUEMA", esquema)
                .replace("INDICE", indice)
            )
            archivo.write("\n")
        archivo.write("EXIT")

def crea_scripts_redefinicion(dir_proyecto,conexion,sid_db, esquema, tabla,columnas,habilita,tablespace_tabla,tablespace_index,parallel,logger):
    SCRIPTS = [
        ("00", "CAN_REDEF"),
        ("01", "CREA_I"),
        ("02", "START"),
        ("300", "CREA_INDEX_I"),
        ("303", "REGISTER"),
        ("309", "COPY"),
        ("04", "SYNCHRONIZE"),
        ("05", "FINISH"),
        ("06", "ABORT"),
        ("07", "ROLLBACK"),
        ("99", "DROP"),
        ]
    logger.debug(f"Creando scripts de redefinición para la tabla {esquema}.{tabla}")
     # Creamos los scripts de redefinición
    for orden, tipo in SCRIPTS:
        archivo_salida = dir_proyecto/ "SQL"/sid_db/esquema/tabla/ f"{orden}_{tipo}_{tabla}.sql"
            
        template = dir_proyecto/"templates"/f"ESQ_{tipo}.txt"

        if orden == "01":
                crea_script_ddl_tabla(conexion, tipo, esquema, tabla, archivo_salida,columnas,tablespace_tabla,habilita,logger)
        elif orden == "300":
                crea_script_ddl_indices(conexion, tipo, esquema, tabla, archivo_salida,tablespace_index,habilita,parallel,logger)
        elif orden == "303":
                lista_indices = obtener_lista_indices(conexion,esquema,tabla,logger)
                llena_template_register(tipo, esquema, tabla, lista_indices, archivo_salida, template,logger)
        else:  # orden not in ('303'):
                with open(template, "r") as archivo:
                    texto = archivo.read()
                with open(archivo_salida, "w") as archivo:
                    archivo.write(
                        texto.replace("TABLA", tabla).replace("ESQUEMA", esquema).replace('paralelo',str(parallel))
                    )
