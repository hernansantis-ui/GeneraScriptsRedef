import oracledb
from pathlib import Path

def crea_directorio(path_inicio,sid_db,esquema,tabla):
    ruta=Path(f'{path_inicio}//{sid_db}//{esquema}//{tabla}')
    ruta.mkdir(parents=True, exist_ok=True)

def extrae_ddl_tabla(conexion,tipo,esquema,tabla,archivo_salida):
    cursor = conexion.cursor()
    cursor.execute(""" 
         begin 
            dbms_metadata.set_transform_param(DBMS_METADATA.SESSION_TRANSFORM,'PRETTY', true) ;
            dbms_metadata.set_transform_param(DBMS_METADATA.SESSION_TRANSFORM,'CONSTRAINTS', false); 
            dbms_metadata.set_transform_param(DBMS_METADATA.SESSION_TRANSFORM,'REF_CONSTRAINTS', false); 
            dbms_metadata.set_transform_param(DBMS_METADATA.SESSION_TRANSFORM,'SQLTERMINATOR', true); 
            dbms_metadata.set_transform_param(DBMS_METADATA.SESSION_TRANSFORM,'TABLE_COMPRESSION_CLAUSE','ROW STORE COMPRESS ADVANCED');
         end;""")
    cursor.execute("""
    #      select dbms_metadata.get_ddl('TABLE',:p_tabla,:p_esquema) from dual
    #       """ ,p_tabla=tabla,p_esquema=esquema
    #  )
    # resultado = cursor.fetchone()
    # buffer=resultado[0].read()

    # cursor.execute(
    #     """
    #         select 'COMMENT ON COLUMN '||owner||'.'||table_name||'.'||column_name||' IS '''||comments||''' ;' txt
    #         from dba_col_comments
    #         where owner=:p_esquema
    #         and table_name =:p_tabla 
    #         and comments is not null
    #     """
    #     , p_tabla=tabla,p_esquema=esquema
    # )
    # lista_comentarios= cursor.fetchall()
    # for comentario in lista_comentarios:
    #     print(comentario[0])
    cursor.execute(
        """    
            select dbms_metadata.get_dependent_ddl('INDEX', :p_tabla ,:p_esquema)  from dual
        """
        ,p_tabla=tabla,p_esquema=esquema
    )
    resultado = cursor.fetchone()
    buffer = resultado[0].read()

    conexion.close()

    print(buffer)
    with open(archivo_salida,'w') as archivo:
         archivo.write(buffer)


def conecta_db():
    return oracledb.connect(
        user='SYSTEM'
        ,password='welcome1'
        ,host='10.10.1.2'
        ,port=1521
        ,service_name='ORA121'
    )
    

def main():
    conexion = conecta_db()
    sid_db='BDOT'
    orden='300'
    tipo='CREA_INT_INDEX'
    esquema='DEV_ODI_REPO'
    tabla='TABLA_PRUEBA'
    archivo_salida = f"SQL/{sid_db}/{esquema}/{tabla}/{orden}_{tipo}_{tabla}.sql"
    crea_directorio('SQL',sid_db,esquema,tabla)      

    extrae_ddl_tabla(conexion,tipo,esquema,tabla,archivo_salida)



if __name__ == "__main__":
    dir_proyecto = Path.cwd()
    main()

