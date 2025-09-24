import logging
from Utils.utilitarios import crea_config_parser


class ConfigError(Exception):
    """Excepción personalizada para errores de configuración."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)    

def valida_seccion_default(config,logger):
    """ Valida que el archivo de configuración tenga las opciones 
            - log_level
            - log_file
            - acceso_base
        configurada con valores que no sean nulos
    """
    logger.debug('Validando opciones de la seccion [default] del archivo redefinition.cfg')

def  valida_secciones(config,logger):
    """ Valida que el archivo de configuración tenga las secciones esperadas """
    logger.debug('Validando secciones del archivo redefinition.cfg')

    secciones_config = ["default","Database", "Tablas", "Tablespaces"]
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
    """ Valida la sección [Database] del archivo redefinition.cfg """   
    logger.debug('Validando sección [Database] del archivo redefinition.cfg')

    # Obtenemos la opcion acceso_base desde la seccion [default]
    acceso_base = config.getboolean('default','acceso_base')

    # Validamos si habrá acceso a la base de datos
    if not acceso_base:
        logger.info('No habrá acceso a la base de datos. Se omite la validación de la sección [Database]')
        return
    
    # Si habrá acceso a la base de datos, validamos las opciones de la sección [Database]
    try:
        opciones_database = ['usuario','clave','servidor','port','servicio']
        l_error = False
        opciones = config.options('Database')
        if not opciones:
            logger.critical('Error: sección [Database] está vacía')
            raise ConfigError('Corrija el archivo redefinition.cfg y vuelva a ejecutar el programa')
        
        # Validamos que esten todas las opciones de [Database]
        for opt in opciones_database:
            if not opt in opciones:
                logger.error(f'Error: Debe aparecer la opción "{opt}" en la sección [Database]')
                l_error = True
            # Validamos que las opciones de [Database] tengan valores      
            valor = config.get('Database',opt)
            if not valor :
                logger.error(f'Error: Opcion "{opt}" no puede estar vacia en sección [Database]')    
                l_error = True                
            if opt == 'port' : # Validamos que el puerto sea este entre 1 y 65535 si no es nulo 
                try:
                    puerto = config.getint('Database','port')
                    if puerto <= 0 or puerto > 65535:
                        logger.error('Error: Opción "port" debe ser un entero entre 1 y 65535 en sección [Database]')
                        l_error = True
                except ValueError:
                    logger.error('Error: Opción "port" debe ser un entero en sección [Database]')
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
   
def valida_archivo_config(config,logger):

    """ Valida el archivo de configuración config_file """

    logger.debug(f'Validando archivo de configuración ')
    
    # Validamos que redefinition.cfg tenga las secciones esperadas
    valida_secciones(config,logger)

    # Validamos la seccion [default], las opciones y sus valores
    valida_seccion_default(config,logger)

    # Validamos la seccion [Database], las  opciones y sus valores
    valida_seccion_db(config,logger)

    # Validamos la sección [Tablas]
    valida_seccion_tablas(config,logger)

    # Validamos la sección [Tablespaces]
    valida_seccion_tablespaces(config,logger)
    logger.info(f'Archivo de configuración validado')
    