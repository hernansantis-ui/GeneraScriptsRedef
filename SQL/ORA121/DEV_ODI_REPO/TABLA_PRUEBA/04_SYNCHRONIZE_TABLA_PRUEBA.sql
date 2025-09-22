-- Genera SYNCHRONIZE TABLA_PRUEBA
set serveroutput on
BEGIN
        DBMS_OUTPUT.NEW_LINE;
        DBMS_OUTPUT.PUT_LINE('Inicio: ' || TO_CHAR(SYSDATE,'YYYY/MM/DD  HH24:MI:SS'));

	DBMS_REDEFINITION.SYNC_INTERIM_TABLE(
	                                      uname      => 'DEV_ODI_REPO', 
					      orig_table => 'TABLA_PRUEBA', 
					      int_table  => 'I_TABLA_PRUEBA'
					    );

        DBMS_OUTPUT.PUT_LINE('Proceso SINCHRONYZE TABLA_PRUEBA : OK');
        DBMS_OUTPUT.PUT_LINE('Finalización: ' || TO_CHAR(SYSDATE,'YYYY/MM/DD  HH24:MI:SS'));
        DBMS_OUTPUT.NEW_LINE;



EXCEPTION
   WHEN others then
	DBMS_OUTPUT.PUT_LINE('Proceso SINCHRONYZE TABLA_PRUEBA  con error: '||SQLERRM);
	DBMS_OUTPUT.PUT_LINE('Finalización: ' || TO_CHAR(SYSDATE,'YYYY/MM/DD  HH24:MI:SS'));
        DBMS_OUTPUT.NEW_LINE;
END;
/
EXIT
