ALTER SESSION FORCE PARALLEL DML parallel 16;
ALTER SESSION FORCE PARALLEL QUERY parallel 16;
ALTER SESSION FORCE PARALLEL DDL parallel 16;
-- Genera START REDEFINITION TABLA_PRUEBA
set serveroutput on

BEGIN
   DBMS_OUTPUT.NEW_LINE;
   DBMS_OUTPUT.PUT_LINE('Inicio: ' || TO_CHAR(SYSDATE,'YYYY/MM/DD  HH24:MI:SS'));

   DBMS_REDEFINITION.START_REDEF_TABLE(
                                       uname      => 'DEV_ODI_REPO' , 
				                           orig_table => 'TABLA_PRUEBA' , 
				                           int_table  => 'I_TABLA_PRUEBA' , 
				                           col_mapping => NULL , 
				                           options_flag => DBMS_REDEFINITION.CONS_USE_ROWID
				                            );

   DBMS_OUTPUT.PUT_LINE('Proceso START TABLA_PRUEBA : OK');
   DBMS_OUTPUT.PUT_LINE('Finalización: ' || TO_CHAR(SYSDATE,'YYYY/MM/DD  HH24:MI:SS'));
   DBMS_OUTPUT.NEW_LINE;


EXCEPTION
   WHEN OTHERS THEN
      DBMS_OUTPUT.PUT_LINE('Proceso START TABLA_PRUEBA con error '||SQLERRM);
      DBMS_OUTPUT.PUT_LINE('Finalización: ' || TO_CHAR(SYSDATE,'YYYY/MM/DD  HH24:MI:SS'));
      DBMS_OUTPUT.NEW_LINE;
  
END;
/
ALTER TABLE I_TABLA_PRUEBA MODIFY(NOPARALLEL) ;

EXIT