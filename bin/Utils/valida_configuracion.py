import logging
from configparser import ConfigParser

class ConfigError(Exception):
    """Excepción personalizada para errores de configuración."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)    


def  valida_secciones(config,logger):
    """ Valida que el archivo de configuración tenga las secciones esperadas """
    logger.debug('Validando secciones del archivo redefinition.cfg')

    secciones_config = ["Database", "Tablas", "Tablespaces"]
    l_error = False
    try:
        for seccion in secciones_config:
            if not config.has_section(seccion):
                logger.error(f'Archivo redefinition.cfg debe contener una seccion [{seccion}]')
                l_error = True
        if l_error :    
            raise ConfigError('Corrija el archivo redefinition.cfg y vuelva a ejecutar el programa')
    except ConfigError as e:
        logger.critical(e)   
        raise SystemExit() 
    except Exception as e:          
        logger.critical(f'Error inesperado al validar las secciones del archivo redefinition.cfg: {e}')
        raise SystemExit() 
    else:
        logger.debug('Secciones del archivo redefinition.cfg validadas correctamente')        

def valida_seccion_db(config,logger):
    logger.debug('Validando sección [Database] del archivo redefinition.cfg')

    opciones_database = ['usuario','clave','servidor','port','servicio']
    l_error = False
    opciones = config.options('Database')
    try:
        if not opciones:
            logger.critical('Error: sección [Database] está vacía')
            raise ConfigError('Corrija el archivo redefinition.cfg y vuelva a ejecutar el programa')
        
        # Validamos que esten todas las opciones de [Database]
        for opt in opciones_database:
            if not opt in opciones:
                logger.error(f'Error: Debe aparecer la opción "{opt}" en la sección [Database]')
                l_error = True  
        if l_error:
            raise ConfigError('Corrija el archivo redefinition.cfg y vuelva a ejecutar el programa')           
    
        # Validamos si las opciones de [Database] tienen valores
        for opcion,valor in config['Database'].items():
            if not valor :
                logger.error(f'Error: Opcion "{opcion}" no puede estar vacia en sección [Database]')    
                l_error = True

        if l_error:
            raise ConfigError('Corrija el archivo redefinition.cfg y vuelva a ejecutar el programa')            
    except ConfigError as e:
        logger.critical(e)   
        raise SystemExit()  
    except Exception as e:          
        logger.critical(f'Error inesperado al validar la sección [Database]: {e}')
        raise SystemExit()  
    else:
        logger.debug('Sección [Database] del archivo redefinition.cfg validada correctamente')

def valida_seccion_tablas(config,logger):
    """ Valida la sección [Tablas] del archivo redefinition.cfg """
    logger.debug('Validando sección [Tablas] del archivo redefinition.cfg')  

    l_error = False
    opciones = config.options('Tablas')
    try:
        if not opciones:
            raise ConfigError('Error: sección [Tablas] está vacía')

        # Validación si las tablas incluyen el esquema        
        for tabla in opciones:
            if '.' not in tabla:
                logger.error(f'Error : la tabla {tabla} debe llevar esquema.tabla')
                l_error = True
                continue    
            owner =(tabla.upper()).split('.')
            logger.debug(f'Validando tabla {tabla}, owner={owner}')
            if owner[0] == '' :
                logger.error(f'Error : la tabla {owner[1]} debe llevar esquema.tabla')
                l_error = True
        if l_error :
            raise ConfigError('Tabla sin esquema. Corrija el archivo redefinition.cfg y vuelva a ejecutar el programa')
    except ConfigError as e:
        logger.critical(e)   
        raise SystemExit()
    except Exception as e:          
        logger.critical(f'Error inesperado al validar la sección [Tablas]: {e}')
        raise SystemExit()  
    else:
        logger.debug('Sección [Tablas] del archivo redefinition.cfg validada correctamente')  


def valida_seccion_tablespaces(config,logger):
    logger.debug('Validando sección [Tablespaces] del archivo redefinition.cfg') 
    l_error = False
    opciones_ts= ['habilita_cambio','tablespace_tabla','tablespace_indice','paralelo']
    opciones = config.options('Tablespaces')
    try:
        if not opciones:
            print('Error: sección [Tablespaces] está vacía')
            raise ConfigError('Error: sección [Tablespaces] está vacía')
        for opt in opciones_ts:
            if not opt in opciones:
                logger.error(f'Advertencia: No aparece la opción "{opt}" en la sección [Tablespaces]')  
                l_error = True
        if l_error:
            raise ConfigError('Corrija el archivo redefinition.cfg y vuelva a ejecutar el programa') 

        habilita = config.getboolean('Tablespaces','habilita_cambio')

        if habilita :
            if (not config.get('Tablespaces','tablespace_tabla') and
                not config.get('Tablespaces','tablespace_indice')): 
                logger.error('Advertencia: Las opciones tablespace_tabla y tablespace_indice no pueden ser nulas simultaneamente en la sección [Tablespaces]')
                raise ConfigError('Corrija el archivo redefinition.cfg y vuelva a ejecutar el programa')
    except ConfigError as e:
        logger.critical(e)   
        raise SystemExit()
    except Exception as e:          
        logger.critical(f'Error inesperado al validar la sección [Tablespaces]: {e}')
        raise SystemExit()
    else:
        logger.debug('Sección [Tablespaces] del archivo redefinition.cfg validada correctamente') 
   
def valida_archivo_config(config_file,logger):

    """ Valida el archivo de configuración config_file """

    logger.debug(f'Validando archivo de configuración {config_file}')
    try:
        config = ConfigParser()
        config.read(f'bin/{config_file}')
        logger.debug(f'Leyendo archivo de configuración {config_file}')
    except Exception as e:          
        logger.critical(f'Error inesperado al leer el archivo de configuración {config_file}: {e}')
        raise SystemExit()
    # Validamos que redefinition.cfg tenga las secciones esperadas
    valida_secciones(config,logger)
    # Validamos la seccion [Database], las  opciones y sus valores
    valida_seccion_db(config,logger)
    # Validamos la sección [Tablas]
    valida_seccion_tablas(config,logger)
    # Validamos la sección [Tablespaces]
    valida_seccion_tablespaces(config,logger)
    logger.info(f'Archivo de configuración {config_file} validado')
    return config
