-- Genera REGISTER TP_AK_LSCHEMA
BEGIN
    DBMS_OUTPUT.NEW_LINE;
    DBMS_OUTPUT.PUT_LINE('Inicio: ' || TO_CHAR(SYSDATE,'YYYY/MM/DD  HH24:MI:SS'));


	DBMS_REDEFINITION.REGISTER_DEPENDENT_OBJECT(
	                                            uname      =>'DEV_ODI_REPO' ,
	                                            orig_table => 'TABLA_PRUEBA',
	                                            int_table  => 'I_TABLA_PRUEBA',
		                                        dep_type   => DBMS_REDEFINITION.CONS_INDEX,
		                                        dep_owner     => 'DEV_ODI_REPO',
		                                        dep_orig_name => 'TP_AK_LSCHEMA',
			                                    dep_int_name  => 'I_TP_AK_LSCHEMA');

    DBMS_OUTPUT.PUT_LINE('Proceso REGISTER TP_AK_LSCHEMA : OK');
    DBMS_OUTPUT.PUT_LINE('Finalización: ' || TO_CHAR(SYSDATE,'YYYY/MM/DD  HH24:MI:SS'));
    DBMS_OUTPUT.NEW_LINE;

EXCEPTION
   	WHEN others then
		DBMS_OUTPUT.PUT_LINE('Proceso REGISTER  TP_AK_LSCHEMA  con error: '||SQLERRM);
		DBMS_OUTPUT.PUT_LINE('Finalización: ' || TO_CHAR(SYSDATE,'YYYY/MM/DD  HH24:MI:SS'));
        DBMS_OUTPUT.NEW_LINE;
END;
/

-- Genera REGISTER TP_PK_LSCHEMA
BEGIN
    DBMS_OUTPUT.NEW_LINE;
    DBMS_OUTPUT.PUT_LINE('Inicio: ' || TO_CHAR(SYSDATE,'YYYY/MM/DD  HH24:MI:SS'));


	DBMS_REDEFINITION.REGISTER_DEPENDENT_OBJECT(
	                                            uname      =>'DEV_ODI_REPO' ,
	                                            orig_table => 'TABLA_PRUEBA',
	                                            int_table  => 'I_TABLA_PRUEBA',
		                                        dep_type   => DBMS_REDEFINITION.CONS_INDEX,
		                                        dep_owner     => 'DEV_ODI_REPO',
		                                        dep_orig_name => 'TP_PK_LSCHEMA',
			                                    dep_int_name  => 'I_TP_PK_LSCHEMA');

    DBMS_OUTPUT.PUT_LINE('Proceso REGISTER TP_PK_LSCHEMA : OK');
    DBMS_OUTPUT.PUT_LINE('Finalización: ' || TO_CHAR(SYSDATE,'YYYY/MM/DD  HH24:MI:SS'));
    DBMS_OUTPUT.NEW_LINE;

EXCEPTION
   	WHEN others then
		DBMS_OUTPUT.PUT_LINE('Proceso REGISTER  TP_PK_LSCHEMA  con error: '||SQLERRM);
		DBMS_OUTPUT.PUT_LINE('Finalización: ' || TO_CHAR(SYSDATE,'YYYY/MM/DD  HH24:MI:SS'));
        DBMS_OUTPUT.NEW_LINE;
END;
/

-- Genera REGISTER TP_AK_LSCHEMA_GUID
BEGIN
    DBMS_OUTPUT.NEW_LINE;
    DBMS_OUTPUT.PUT_LINE('Inicio: ' || TO_CHAR(SYSDATE,'YYYY/MM/DD  HH24:MI:SS'));


	DBMS_REDEFINITION.REGISTER_DEPENDENT_OBJECT(
	                                            uname      =>'DEV_ODI_REPO' ,
	                                            orig_table => 'TABLA_PRUEBA',
	                                            int_table  => 'I_TABLA_PRUEBA',
		                                        dep_type   => DBMS_REDEFINITION.CONS_INDEX,
		                                        dep_owner     => 'DEV_ODI_REPO',
		                                        dep_orig_name => 'TP_AK_LSCHEMA_GUID',
			                                    dep_int_name  => 'I_TP_AK_LSCHEMA_GUID');

    DBMS_OUTPUT.PUT_LINE('Proceso REGISTER TP_AK_LSCHEMA_GUID : OK');
    DBMS_OUTPUT.PUT_LINE('Finalización: ' || TO_CHAR(SYSDATE,'YYYY/MM/DD  HH24:MI:SS'));
    DBMS_OUTPUT.NEW_LINE;

EXCEPTION
   	WHEN others then
		DBMS_OUTPUT.PUT_LINE('Proceso REGISTER  TP_AK_LSCHEMA_GUID  con error: '||SQLERRM);
		DBMS_OUTPUT.PUT_LINE('Finalización: ' || TO_CHAR(SYSDATE,'YYYY/MM/DD  HH24:MI:SS'));
        DBMS_OUTPUT.NEW_LINE;
END;
/

-- Genera REGISTER TP_LSCHEMA_FK1
BEGIN
    DBMS_OUTPUT.NEW_LINE;
    DBMS_OUTPUT.PUT_LINE('Inicio: ' || TO_CHAR(SYSDATE,'YYYY/MM/DD  HH24:MI:SS'));


	DBMS_REDEFINITION.REGISTER_DEPENDENT_OBJECT(
	                                            uname      =>'DEV_ODI_REPO' ,
	                                            orig_table => 'TABLA_PRUEBA',
	                                            int_table  => 'I_TABLA_PRUEBA',
		                                        dep_type   => DBMS_REDEFINITION.CONS_INDEX,
		                                        dep_owner     => 'DEV_ODI_REPO',
		                                        dep_orig_name => 'TP_LSCHEMA_FK1',
			                                    dep_int_name  => 'I_TP_LSCHEMA_FK1');

    DBMS_OUTPUT.PUT_LINE('Proceso REGISTER TP_LSCHEMA_FK1 : OK');
    DBMS_OUTPUT.PUT_LINE('Finalización: ' || TO_CHAR(SYSDATE,'YYYY/MM/DD  HH24:MI:SS'));
    DBMS_OUTPUT.NEW_LINE;

EXCEPTION
   	WHEN others then
		DBMS_OUTPUT.PUT_LINE('Proceso REGISTER  TP_LSCHEMA_FK1  con error: '||SQLERRM);
		DBMS_OUTPUT.PUT_LINE('Finalización: ' || TO_CHAR(SYSDATE,'YYYY/MM/DD  HH24:MI:SS'));
        DBMS_OUTPUT.NEW_LINE;
END;
/

-- Genera REGISTER TP_LSCHEMA_FK2
BEGIN
    DBMS_OUTPUT.NEW_LINE;
    DBMS_OUTPUT.PUT_LINE('Inicio: ' || TO_CHAR(SYSDATE,'YYYY/MM/DD  HH24:MI:SS'));


	DBMS_REDEFINITION.REGISTER_DEPENDENT_OBJECT(
	                                            uname      =>'DEV_ODI_REPO' ,
	                                            orig_table => 'TABLA_PRUEBA',
	                                            int_table  => 'I_TABLA_PRUEBA',
		                                        dep_type   => DBMS_REDEFINITION.CONS_INDEX,
		                                        dep_owner     => 'DEV_ODI_REPO',
		                                        dep_orig_name => 'TP_LSCHEMA_FK2',
			                                    dep_int_name  => 'I_TP_LSCHEMA_FK2');

    DBMS_OUTPUT.PUT_LINE('Proceso REGISTER TP_LSCHEMA_FK2 : OK');
    DBMS_OUTPUT.PUT_LINE('Finalización: ' || TO_CHAR(SYSDATE,'YYYY/MM/DD  HH24:MI:SS'));
    DBMS_OUTPUT.NEW_LINE;

EXCEPTION
   	WHEN others then
		DBMS_OUTPUT.PUT_LINE('Proceso REGISTER  TP_LSCHEMA_FK2  con error: '||SQLERRM);
		DBMS_OUTPUT.PUT_LINE('Finalización: ' || TO_CHAR(SYSDATE,'YYYY/MM/DD  HH24:MI:SS'));
        DBMS_OUTPUT.NEW_LINE;
END;
/

-- Genera REGISTER TP_IDX_LSCHEMA_LD
BEGIN
    DBMS_OUTPUT.NEW_LINE;
    DBMS_OUTPUT.PUT_LINE('Inicio: ' || TO_CHAR(SYSDATE,'YYYY/MM/DD  HH24:MI:SS'));


	DBMS_REDEFINITION.REGISTER_DEPENDENT_OBJECT(
	                                            uname      =>'DEV_ODI_REPO' ,
	                                            orig_table => 'TABLA_PRUEBA',
	                                            int_table  => 'I_TABLA_PRUEBA',
		                                        dep_type   => DBMS_REDEFINITION.CONS_INDEX,
		                                        dep_owner     => 'DEV_ODI_REPO',
		                                        dep_orig_name => 'TP_IDX_LSCHEMA_LD',
			                                    dep_int_name  => 'I_TP_IDX_LSCHEMA_LD');

    DBMS_OUTPUT.PUT_LINE('Proceso REGISTER TP_IDX_LSCHEMA_LD : OK');
    DBMS_OUTPUT.PUT_LINE('Finalización: ' || TO_CHAR(SYSDATE,'YYYY/MM/DD  HH24:MI:SS'));
    DBMS_OUTPUT.NEW_LINE;

EXCEPTION
   	WHEN others then
		DBMS_OUTPUT.PUT_LINE('Proceso REGISTER  TP_IDX_LSCHEMA_LD  con error: '||SQLERRM);
		DBMS_OUTPUT.PUT_LINE('Finalización: ' || TO_CHAR(SYSDATE,'YYYY/MM/DD  HH24:MI:SS'));
        DBMS_OUTPUT.NEW_LINE;
END;
/

EXIT