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
    except Exception as e:
        logger.critical(f"Error inesperado al conectar a la base de datos: {str(e)}")
        sys.exit(1) 

def crea_script_tabla_from_db(config,esquema, tabla, archivo_salida,logger):
    conexion = conecta_db(config,logger)
    cursor = conexion.cursor()
    cursor.execute(
        """ 
         begin 
            dbms_metadata.set_transform_param(DBMS_METADATA.SESSION_TRANSFORM,'PRETTY', true) ;
            dbms_metadata.set_transform_param(DBMS_METADATA.SESSION_TRANSFORM,'CONSTRAINTS', false); 
            dbms_metadata.set_transform_param(DBMS_METADATA.SESSION_TRANSFORM,'REF_CONSTRAINTS', false); 
            dbms_metadata.set_transform_param(DBMS_METADATA.SESSION_TRANSFORM,'SQLTERMINATOR', true); 
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

    cursor.close()
    conexion.close()
    
    with open(archivo_salida, "w") as archivo:
        archivo.write(ddl_tabla + "\n")
        archivo.writelines(lista_comentarios)
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

def crea_script_indices_from_db(config, esquema, tabla, archivo_salida,logger):
    conexion = conecta_db(config,logger)
    parallel = config.getint('Tablespaces','paralelo')
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
    conexion.close()

    with open(archivo_salida, "w") as archivo:
        if parallel != 0 :
            archivo.write(f'  ALTER SESSION FORCE PARALLEL DML parallel {parallel};\n')
            archivo.write(f'  ALTER SESSION FORCE PARALLEL DDL parallel {parallel};\n')
            archivo.write(f'  ALTER SESSION FORCE PARALLEL QUERY parallel {parallel};\n')

        archivo.write(ddl_indices)
        archivo.write('\n  EXIT')


