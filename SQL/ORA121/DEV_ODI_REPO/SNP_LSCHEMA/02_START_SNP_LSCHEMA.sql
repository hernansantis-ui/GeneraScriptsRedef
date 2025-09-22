ALTER SESSION FORCE PARALLEL DML parallel 16;
ALTER SESSION FORCE PARALLEL QUERY parallel 16;
ALTER SESSION FORCE PARALLEL DDL parallel 16;
-- Genera START REDEFINITION SNP_LSCHEMA
set serveroutput on

BEGIN
   DBMS_OUTPUT.NEW_LINE;
   DBMS_OUTPUT.PUT_LINE('Inicio: ' || TO_CHAR(SYSDATE,'YYYY/MM/DD  HH24:MI:SS'));

   DBMS_REDEFINITION.START_REDEF_TABLE(
                                       uname      => 'DEV_ODI_REPO' , 
				                           orig_table => 'SNP_LSCHEMA' , 
				                           int_table  => 'I_SNP_LSCHEMA' , 
				                           col_mapping => NULL , 
				                           options_flag => DBMS_REDEFINITION.CONS_USE_ROWID
				                            );

   DBMS_OUTPUT.PUT_LINE('Proceso START SNP_LSCHEMA : OK');
   DBMS_OUTPUT.PUT_LINE('Finalización: ' || TO_CHAR(SYSDATE,'YYYY/MM/DD  HH24:MI:SS'));
   DBMS_OUTPUT.NEW_LINE;


EXCEPTION
   WHEN OTHERS THEN
      DBMS_OUTPUT.PUT_LINE('Proceso START SNP_LSCHEMA con error '||SQLERRM);
      DBMS_OUTPUT.PUT_LINE('Finalización: ' || TO_CHAR(SYSDATE,'YYYY/MM/DD  HH24:MI:SS'));
      DBMS_OUTPUT.NEW_LINE;
  
END;
/
ALTER TABLE I_SNP_LSCHEMA MODIFY(NOPARALLEL) ;

EXIT