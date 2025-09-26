CREATE TABLE SYSTEM.LOGMNR_TAB$
(
  TS#           NUMBER(22),
  COLS          NUMBER(22),
  PROPERTY      NUMBER(22),
  INTCOLS       NUMBER(22),
  KERNELCOLS    NUMBER(22),
  BOBJ#         NUMBER(22),
  TRIGFLAG      NUMBER(22),
  FLAGS         NUMBER(22),
  OBJ#          NUMBER(22),
  LOGMNR_UID    NUMBER(22),
  LOGMNR_FLAGS  NUMBER(22)
)
TABLESPACE SYSAUX
PCTUSED    0
PCTFREE    10
INITRANS   1
MAXTRANS   255
STORAGE    (
            BUFFER_POOL      DEFAULT
           )
PARTITION BY RANGE (LOGMNR_UID)
(  
  PARTITION P_LESSTHAN100 VALUES LESS THAN (100)
    TABLESPACE SYSAUX
    PCTFREE    10
    INITRANS   1
    MAXTRANS   255
    STORAGE    (
                INITIAL          64K
                NEXT             1M
                MINEXTENTS       1
                MAXEXTENTS       UNLIMITED
                BUFFER_POOL      DEFAULT
               ),  
  PARTITION P100 VALUES LESS THAN (101)
    TABLESPACE SYSAUX
    PCTFREE    10
    INITRANS   1
    MAXTRANS   255
    STORAGE    (
                INITIAL          64K
                NEXT             1M
                MINEXTENTS       1
                MAXEXTENTS       UNLIMITED
                BUFFER_POOL      DEFAULT
               )
);


CREATE INDEX SYSTEM.LOGMNR_I1TAB$ ON SYSTEM.LOGMNR_TAB$
(LOGMNR_UID, OBJ#)
  TABLESPACE SYSAUX
  PCTFREE    10
  INITRANS   2
  MAXTRANS   255
LOCAL (  
  PARTITION P_LESSTHAN100
    TABLESPACE SYSAUX
    PCTFREE    10
    INITRANS   2
    MAXTRANS   255
    STORAGE    (
                INITIAL          64K
                NEXT             1M
                MINEXTENTS       1
                MAXEXTENTS       UNLIMITED
                BUFFER_POOL      DEFAULT
               ),  
  PARTITION P100
    TABLESPACE SYSAUX
    PCTFREE    10
    INITRANS   2
    MAXTRANS   255
    STORAGE    (
                INITIAL          64K
                NEXT             1M
                MINEXTENTS       1
                MAXEXTENTS       UNLIMITED
                BUFFER_POOL      DEFAULT
               )
);


CREATE INDEX SYSTEM.LOGMNR_I2TAB$ ON SYSTEM.LOGMNR_TAB$
(LOGMNR_UID, BOBJ#)
  TABLESPACE SYSAUX
  PCTFREE    10
  INITRANS   2
  MAXTRANS   255
LOCAL (  
  PARTITION P_LESSTHAN100
    TABLESPACE SYSAUX
    PCTFREE    10
    INITRANS   2
    MAXTRANS   255
    STORAGE    (
                INITIAL          64K
                NEXT             1M
                MINEXTENTS       1
                MAXEXTENTS       UNLIMITED
                BUFFER_POOL      DEFAULT
               ),  
  PARTITION P100
    TABLESPACE SYSAUX
    PCTFREE    10
    INITRANS   2
    MAXTRANS   255
    STORAGE    (
                INITIAL          64K
                NEXT             1M
                MINEXTENTS       1
                MAXEXTENTS       UNLIMITED
                BUFFER_POOL      DEFAULT
               )
);
