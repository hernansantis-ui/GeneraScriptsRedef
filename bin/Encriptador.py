"""
                              ENCRIPTADOR
En el marco de la encriptación de tablas para las bases de Transbank, se desarrolla
esta aplicación para generar los script SQL que permiten redefinir las tablas
encriptandolas y comprimiendolas

"""

from pathlib import Path
from configparser import ConfigParser
import sys
import oracledb
import re
 
scripts = [
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


def conecta_db(config):
    servidor = config.get('Database','servidor')
    puerto = config.getint('Database','port')
    servicio = config.get('Database','servicio')
    usuario = config.get('Database','usuario')
    clave = config.get('Database','clave')

    conecta = oracledb.connect(
        user=usuario,
        password=clave,
        host=servidor,
        port=puerto,
        service_name=servicio,
    )
    return conecta

def  valida_secciones(config):
    l_error = False
    if not config.has_section('Database'):
        print('Archivo encriptador.cfg debe contener una seccion [Database]')
        l_error = True
    elif not config.has_section('Tablespaces'):
        print('Archivo encriptador.cfg debe contener una seccion [Tablespace]')
        l_error = True
    elif not config.has_section('Tablas'):
        print('Archivo encriptador.cfg debe contener una seccion [Tablas]')
        l_error = True
    if l_error :    
        raise SystemExit()

def valida_seccion_db(config):
    l_error = False
    opciones = config.options('Database')

    if not opciones:
        print(f'Error: sección [Database] está vacía')
        raise SystemExit()

    if not config.has_option('Database','usuario'):
        print(f'Error: Opcion "usuario" no aparece sección [Database]')    
        l_error = True
    elif not config.has_option('Database','clave'):
        print(f'Error: Opcion "clave" no aparece en sección [Database]')    
        l_error = True
    elif not config.has_option('Database','servidor'):
        print(f'Error: Opcion "servidor" no aparece en sección [Database]')    
        l_error = True
    elif not config.has_option('Database','port'):
        print(f'Error: Opcion "port" no aparece en sección [Database]')    
        l_error = True
    elif not config.has_option('Database','servicio'):
        print(f'Error: Opcion "servicio" no aparece en sección [Database]')    
        l_error = True
    if l_error:
        raise SystemExit()           
    
    # Validamos si las opciones tienen valores esperados
    for opcion,valor in config['Database'].items():
        if not valor :
            print(f'Error: Opcion "{opcion}" no puede estar vacia en sección [Database]')    
            l_error = True
    if l_error:
        raise SystemExit()            

def valida_seccion_tablas(config):
    l_error = False
    opciones = config.options('Tablas')
    if not opciones:
        print(f'Error: sección [Tablas] está vacía')
        raise SystemExit()

    # Validación si las tablas incluyen el esquema        
    for tabla in opciones:
        owner =(tabla.upper()).split('.')
        if len(owner) < 2:
            print(f'Error : la tabla {owner[0]} debe llevar esquema.tabla')
            l_error = True
    if l_error :
        raise SystemExit()
    

def valida_seccion_tablespaces(config):
    l_error = False
    opciones = config.options('Tablespaces')
   
    if not opciones:
        print(f'Error: sección [Tablespaces] está vacía')
        raise SystemExit()
    if  not ('habilita_cambio' in opciones):
        print(f'Error: Opción "habilita_cambio" no aparece en la sección [Tablespaces]')
        raise SystemExit()

    
    habilita = config.getboolean('Tablespaces','habilita_cambio')
    # Validamos que esten las opciones tablespace
    if habilita :
        if not config.has_option('Tablespaces','tablespace_tabla'): 
           print(f'Error: Debe aparecer la opcion tablespace_tabla en la sección [Tablespaces]')
           l_error =  True
        elif not config.has_option('Tablespaces','tablespace_indice'):
           print(f'Error: Debe aparecer la opcion tablespace_indice en la sección[Tablespaces]')
           l_error = True
    if l_error:
        raise SystemExit()

   
def valida_archivo_config():
    # Validamos que encriptador.cfg tenga las secciones esperadas
    config = ConfigParser()
    config.read('bin/encriptador.cfg')

    # Validamos que encriptador.cfg tenga las secciones esperadas
    valida_secciones(config)
    # Validamos la seccion [Database], las  opciones y sus valores
    valida_seccion_db(config)
    # Validamos la sección [Tablas]
    valida_seccion_tablas(config)
    # Validamos la sección [Tablespaces]
    valida_seccion_tablespaces(config)
    return config

def crea_directorio(path_inicio, sid_db, esquema, tabla):
    ruta = dir_proyecto / path_inicio / sid_db / esquema / tabla
    ruta.mkdir(parents=True, exist_ok=True)


def llena_template_register(
    tipo, esquema, tabla, lista_indices, archivo_salida, template
):

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


def extrae_ddl_indices(conexion, tipo, esquema, tabla, archivo_salida,tablespace,habilita,parallel):
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
        ddl_indices = cambia_tablespace(ddl_indices,tablespace)


#   Agregamos la sentencia de compersion de indices
    ddl_indices = ddl_incorpora_compresion(ddl_indices)
        
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




def extrae_ddl_tabla(conexion, tipo, esquema, tabla, archivo_salida,columnas,tablespace,habilita):
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
        ddl_tabla = encripta_columnas(ddl_tabla,columnas)

    # Verificamos si debemos cambiar el tableespace
    if habilita and tablespace != None:
        ddl_tabla = cambia_tablespace(ddl_tabla,tablespace)
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



def obtener_lista_indices(conexion,esquema,tabla):
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


def main(config):
    
    conexion = conecta_db(config)

    # Por cada tabla en el archivo de configuración procesamos la informacion
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

    opciones = config.options('Tablas')
    for opt in opciones:
        esquema = opt.split('.')[0].upper()
        tabla = opt.split('.')[1].upper()
        valores = config.get('Tablas',opt)
        if len(valores) > 0: 
            columnas = [col.strip() for col in config.get('Tablas',opt).split(',')]
        else:
            columnas=[]    
        
        crea_directorio("SQL", sid_db, esquema, tabla)

        for orden, tipo in scripts:
            archivo_salida = (
                dir_proyecto
                / "SQL"
                / sid_db
                / esquema
                / tabla
                / f"{orden}_{tipo}_{tabla}.sql"
            )
            template = dir_proyecto / "templates" / f"ESQ_{tipo}.txt"
            if orden == "01":
                # TODO : Falta Postproceso
                extrae_ddl_tabla(conexion, tipo, esquema, tabla, archivo_salida,columnas,tablespace_tabla,habilita)
            elif orden == "300":
                # TODO : Falta Postproceso
                extrae_ddl_indices(conexion, tipo, esquema, tabla, archivo_salida,tablespace_index,habilita,parallel)
            elif orden == "303":
                lista_indices = obtener_lista_indices(conexion,esquema,tabla)
                llena_template_register(
                    tipo, esquema, tabla, lista_indices, archivo_salida, template
                )
            else:  # orden not in ('303'):
                with open(template, "r") as archivo:
                    texto = archivo.read()
                with open(archivo_salida, "w") as archivo:
                    archivo.write(
                        texto.replace("TABLA", tabla).replace("ESQUEMA", esquema).replace('paralelo',str(parallel))
                    )


if __name__ == "__main__":
    dir_proyecto = Path.cwd()
    config = ConfigParser()
    config = valida_archivo_config()
    main(config)
