-- Genera SYNCHRONIZE SNP_LSCHEMA
set serveroutput on
BEGIN
        DBMS_OUTPUT.NEW_LINE;
        DBMS_OUTPUT.PUT_LINE('Inicio: ' || TO_CHAR(SYSDATE,'YYYY/MM/DD  HH24:MI:SS'));

	DBMS_REDEFINITION.SYNC_INTERIM_TABLE(
	                                      uname      => 'DEV_ODI_REPO', 
					      orig_table => 'SNP_LSCHEMA', 
					      int_table  => 'I_SNP_LSCHEMA'
					    );

        DBMS_OUTPUT.PUT_LINE('Proceso SINCHRONYZE SNP_LSCHEMA : OK');
        DBMS_OUTPUT.PUT_LINE('Finalización: ' || TO_CHAR(SYSDATE,'YYYY/MM/DD  HH24:MI:SS'));
        DBMS_OUTPUT.NEW_LINE;



EXCEPTION
   WHEN others then
	DBMS_OUTPUT.PUT_LINE('Proceso SINCHRONYZE SNP_LSCHEMA  con error: '||SQLERRM);
	DBMS_OUTPUT.PUT_LINE('Finalización: ' || TO_CHAR(SYSDATE,'YYYY/MM/DD  HH24:MI:SS'));
        DBMS_OUTPUT.NEW_LINE;
END;
/
EXIT
