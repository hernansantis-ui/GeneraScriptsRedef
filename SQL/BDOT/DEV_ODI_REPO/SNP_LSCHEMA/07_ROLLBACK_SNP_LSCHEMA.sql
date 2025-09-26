-- GENERA ROLLBACK  SNP_LSCHEMA

-- Se renombra SNP_LSCHEMA como TMP_SNP_LSCHEMA
-- Se renombre INT_SNP_LSCHEMA como SNP_LSCHEMA
-- Se renombram indices, constraints y trigges
set serveroutput on
declare

        nombre_old      varchar2(400);
        nombre_new      varchar2(400);
        sqlstmnt        varchar2(400);
begin
    for i in (select index_name from all_indexes where table_name='SNP_LSCHEMA' and owner='DEV_ODI_REPO')
    loop
        nombre_old := i.index_name;
        nombre_new := 'T_'||nombre_old;
        
        sqlstmnt := 'alter index DEV_ODI_REPO.'||nombre_old||' rename to '||nombre_new;
        
        execute immediate sqlstmnt;
        
    end loop;    

    for i in (select trigger_name from all_triggers where table_name='SNP_LSCHEMA' and owner='DEV_ODI_REPO')
    loop
        nombre_old := i.trigger_name;
        nombre_new := 'T_'||nombre_old;
        
        sqlstmnt := 'alter trigger DEV_ODI_REPO.'||nombre_old||' rename to '||nombre_new;
        
        execute immediate sqlstmnt;
        
    end loop;    
    for i in (select constraint_name from all_constraints where table_name='SNP_LSCHEMA' and owner='DEV_ODI_REPO')
    loop
        nombre_old := i.constraint_name;
        nombre_new := 'T_'||nombre_old;
        
        sqlstmnt := 'alter table DEV_ODI_REPO.SNP_LSCHEMA rename constraint '||nombre_old||'  to '||nombre_new;
        
        execute immediate sqlstmnt;
        
    end loop;    
    
-- Cambiamos los nombres de indices, triggers y constraints de la tabla INTERINA
    for i in (select index_name from all_indexes where table_name='I_SNP_LSCHEMA' and owner='DEV_ODI_REPO')
    loop
        nombre_old := i.index_name;
        nombre_new := substr(substr(nombre_old,7),1,length(substr(nombre_old,7))-1);
        
        sqlstmnt := 'alter index DEV_ODI_REPO.'||nombre_old||' rename to '||nombre_new;
        
        execute immediate sqlstmnt;
        
    end loop;    

    for i in (select trigger_name from all_triggers where table_name='I_SNP_LSCHEMA' and owner='DEV_ODI_REPO')
    loop
        nombre_old := i.trigger_name;
        nombre_new := substr(substr(nombre_old,7),1,length(substr(nombre_old,7))-1);
        
        sqlstmnt := 'alter trigger DEV_ODI_REPO.'||nombre_old||' rename to '||nombre_new;
        
        execute immediate sqlstmnt;
        
    end loop;    
    for i in (select constraint_name from all_constraints where table_name='I_SNP_LSCHEMA' and owner='DEV_ODI_REPO')
    loop
        nombre_old := i.constraint_name;
        nombre_new := substr(substr(nombre_old,7),1,length(substr(nombre_old,7))-1);
        
        sqlstmnt := 'alter table DEV_ODI_REPO.SNP_LSCHEMA rename constraint '||nombre_old||'  to '||nombre_new;
        
        execute immediate sqlstmnt;
        
    end loop;    

-- Renombramos las tablas SNP_LSCHEMA --> TMP_SNP_LSCHEMA e I_SNP_LSCHEMA --> SNP_LSCHEMA
    

    execute immediate 'RENAME  DEV_ODI_REPO.SNP_LSCHEMA TO TMP_SNP_LSCHEMA';
    execute immediate 'RENAME DEV_ODI_REPO.I_SNP_LSCHEMA TO SNP_LSCHEMA';
-- Borramos la tabla TMP_SNP_LSCHEMA
    execute immediate 'DROP TABLE TMP_SNP_LSCHEMA CASCADE CONSTRAINTS PURGE';

exception
    when others then 
        dbms_output.put_line('Error SNP_LSCHEMA: '||SQLERRM);


end;
/
exit



















