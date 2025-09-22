-- Genera COPY DEPENDANTS SNP_LSCHEMA
set serveroutput on

DECLARE
num_errors PLS_INTEGER;
BEGIN 
   DBMS_OUTPUT.NEW_LINE;
   DBMS_OUTPUT.PUT_LINE('Inicio: ' || TO_CHAR(SYSDATE,'YYYY/MM/DD  HH24:MI:SS'));

   DBMS_REDEFINITION.COPY_TABLE_DEPENDENTS(
                                            uname         => 'DEV_ODI_REPO', 
                                            orig_table    => 'SNP_LSCHEMA',
                                            int_table     => 'I_SNP_LSCHEMA',
                                            copy_indexes  => 0 ,  -- No se copian los indices 
                                            copy_triggers    => TRUE, 
                                            copy_constraints => TRUE, 
                                            copy_privileges  => TRUE, 
                                            ignore_errors    => TRUE, 
                                            num_errors       => num_errors
        				   );
  if (num_errors <> 0 )
  then
      DBMS_OUTPUT.PUT_LINE('Proceos COPY DEPENDANTS SNP_LSCHEMA con '||num_errors||' error(es)' );
      DBMS_OUTPUT.PUT_LINE('Finalización: ' || TO_CHAR(SYSDATE,'YYYY/MM/DD  HH24:MI:SS'));
      DBMS_OUTPUT.PUT_LINE('Ejecutar para verificar errores, columns err_no debe ser nula ');
      DBMS_OUTPUT('****** select object_name, base_table_name,err_no, ddl_txt from DBA_REDEFINITION_ERRORS;');
      DBMS_OUTPUT.NEW_LINE;
  else
      DBMS_OUTPUT.PUT_LINE('Proceso COPY DEPENDANTS SNP_LSCHEMA : OK' );
      DBMS_OUTPUT.PUT_LINE('Finalización: ' || TO_CHAR(SYSDATE,'YYYY/MM/DD  HH24:MI:SS'));
      DBMS_OUTPUT.NEW_LINE;
  end if;	
END;
/
EXIT