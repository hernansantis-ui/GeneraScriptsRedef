-- Genera FINISH REDEFINITION SNP_LSCHEMA
set serveroutput on

BEGIN
        DBMS_OUTPUT.NEW_LINE;
        DBMS_OUTPUT.PUT_LINE('Inicio: ' || TO_CHAR(SYSDATE,'YYYY/MM/DD  HH24:MI:SS'));

        DBMS_REDEFINITION.FINISH_REDEF_TABLE(
					      uname      => 'DEV_ODI_REPO' , 
					      orig_table => 'SNP_LSCHEMA' , 
					      int_table  => 'I_SNP_LSCHEMA'
					    );

        DBMS_OUTPUT.PUT_LINE('Proceso FINISH SNP_LSCHEMA : OK');
        DBMS_OUTPUT.PUT_LINE('Finalización: ' || TO_CHAR(SYSDATE,'YYYY/MM/DD  HH24:MI:SS'));
        DBMS_OUTPUT.NEW_LINE;
        
        FOR INDICE IN (SELECT INDEX_NAME FROM ALL_INDEXES 
                       WHERE TABLE_NAME='SNP_LSCHEMA' AND OWNER='DEV_ODI_REPO')
        LOOP
                EXECUTE IMMEDIATE('ALTER INDEX DEV_ODI_REPO.INDICE NOPARALLEL') ;
        END LOOP;        

EXCEPTION
    when OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('Proceso FINISH SNP_LSCHEMA con error: '||SQLERRM);
        DBMS_OUTPUT.PUT_LINE('Finalización: ' || TO_CHAR(SYSDATE,'YYYY/MM/DD  HH24:MI:SS'));
        DBMS_OUTPUT.NEW_LINE;

END;
/
EXIT