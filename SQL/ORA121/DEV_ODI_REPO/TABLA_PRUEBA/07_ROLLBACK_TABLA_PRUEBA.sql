-- GENERA ROLLBACK  TABLA_PRUEBA

-- Se renombra TABLA_PRUEBA como TMP_TABLA_PRUEBA
-- Se renombre I_TABLA_PRUEBA como TABLA_PRUEBA
-- Se renombram indices, constraints y trigges
set serveroutput on
declare

        nombre_old      varchar2(400);
        nombre_new      varchar2(400);
        sqlstmnt        varchar2(400);
begin
    for i in (select index_name from all_indexes where table_name='TABLA_PRUEBA' and owner='DEV_ODI_REPO')
    loop
        nombre_old := i.index_name;
        nombre_new := 'T_'||nombre_old;
        
        sqlstmnt := 'alter index DEV_ODI_REPO.'||nombre_old||' rename to '||nombre_new;
        
        execute immediate sqlstmnt;
        
    end loop;    

    for i in (select trigger_name from all_triggers where table_name='TABLA_PRUEBA' and owner='DEV_ODI_REPO')
    loop
        nombre_old := i.trigger_name;
        nombre_new := 'T_'||nombre_old;
        
        sqlstmnt := 'alter trigger DEV_ODI_REPO.'||nombre_old||' rename to '||nombre_new;
        
        execute immediate sqlstmnt;
        
    end loop;    
    for i in (select constraint_name from all_constraints where table_name='TABLA_PRUEBA' and owner='DEV_ODI_REPO')
    loop
        nombre_old := i.constraint_name;
        nombre_new := 'T_'||nombre_old;
        
        sqlstmnt := 'alter table DEV_ODI_REPO.TABLA_PRUEBA rename constraint '||nombre_old||'  to '||nombre_new;
        
        execute immediate sqlstmnt;
        
    end loop;    
    
-- Cambiamos los nombres de indices, triggers y constraints de la tabla INTERINA
    for i in (select index_name from all_indexes where table_name='I_TABLA_PRUEBA' and owner='DEV_ODI_REPO')
    loop
        nombre_old := i.index_name;
        nombre_new := substr(substr(nombre_old,7),1,length(substr(nombre_old,7))-1);
        
        sqlstmnt := 'alter index DEV_ODI_REPO.'||nombre_old||' rename to '||nombre_new;
        
        execute immediate sqlstmnt;
        
    end loop;    

    for i in (select trigger_name from all_triggers where table_name='I_TABLA_PRUEBA' and owner='DEV_ODI_REPO')
    loop
        nombre_old := i.trigger_name;
        nombre_new := substr(substr(nombre_old,7),1,length(substr(nombre_old,7))-1);
        
        sqlstmnt := 'alter trigger DEV_ODI_REPO.'||nombre_old||' rename to '||nombre_new;
        
        execute immediate sqlstmnt;
        
    end loop;    
    for i in (select constraint_name from all_constraints where table_name='I_TABLA_PRUEBA' and owner='DEV_ODI_REPO')
    loop
        nombre_old := i.constraint_name;
        nombre_new := substr(substr(nombre_old,7),1,length(substr(nombre_old,7))-1);
        
        sqlstmnt := 'alter table DEV_ODI_REPO.TABLA_PRUEBA rename constraint '||nombre_old||'  to '||nombre_new;
        
        execute immediate sqlstmnt;
        
    end loop;    

-- Renombramos las tablas TABLA_PRUEBA --> TMP_TABLA_PRUEBA e I_TABLA_PRUEBA --> TABLA_PRUEBA
    

    execute immediate 'RENAME  DEV_ODI_REPO.TABLA_PRUEBA TO TMP_TABLA_PRUEBA';
    execute immediate 'RENAME DEV_ODI_REPO.I_TABLA_PRUEBA TO TABLA_PRUEBA';
-- Borramos la tabla TMP_TABLA_PRUEBA
    execute immediate 'DROP TABLE TMP_TABLA_PRUEBA CASCADE CONSTRAINTS PURGE';

exception
    when others then 
        dbms_output.put_line('Error TABLA_PRUEBA: '||SQLERRM);


end;
/
exit



















