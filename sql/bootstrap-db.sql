-- DDL commands to bootstrap the DomiNode DB

-- -----
-- ROLES
-- -----

CREATE ROLE admin WITH CREATEDB CREATEROLE;
CREATE ROLE replicator WITH REPLICATION;

CREATE ROLE editor;

CREATE ROLE ppd_editor IN ROLE editor;
CREATE ROLE ppd_user;

CREATE ROLE lsd_editor IN ROLE editor;
CREATE ROLE lsd_user;

-- ---------------
-- STAGING SCHEMAS
-- ---------------

CREATE SCHEMA IF NOT EXISTS ppd_staging AUTHORIZATION ppd_editor;
CREATE SCHEMA IF NOT EXISTS lsd_staging AUTHORIZATION lsd_editor;

-- Grant schema access to the relevant roles
GRANT USAGE ON SCHEMA ppd_staging TO ppd_user;
GRANT USAGE ON SCHEMA lsd_staging TO lsd_user;

-- -------------
-- PUBLIC SCHEMA
-- -------------

-- Create the `layer_styles` table which is used by QGIS to save styles
CREATE TABLE IF NOT EXISTS public.layer_styles
(
    id                serial not null
        constraint layer_styles_pkey
            primary key,
    f_table_catalog   varchar,
    f_table_schema    varchar,
    f_table_name      varchar,
    f_geometry_column varchar,
    stylename         text,
    styleqml          xml,
    stylesld          xml,
    useasdefault      boolean,
    description       text,
    owner             varchar(63) default CURRENT_USER,
    ui                xml,
    update_time       timestamp   default CURRENT_TIMESTAMP
);

ALTER TABLE public.layer_styles OWNER TO editor;


-- Disable creation of objects on the public schema by default
REVOKE CREATE ON SCHEMA public FROM public;

-- Grant permission to editors for creating new objects on the public schema
GRANT CREATE ON SCHEMA public TO editor;


-- After the initial setup is done, perform the following:

-- 1. Create initial users
-- PPD users
CREATE USER ppd_editor1 PASSWORD 'ppd_editor1' IN ROLE ppd_editor, admin;
CREATE USER ppd_editor2 PASSWORD 'ppd_editor2' IN ROLE ppd_editor;
CREATE USER ppd_user1 PASSWORD 'ppd_user1' IN ROLE ppd_user;
-- LSD users
CREATE USER lsd_editor1 PASSWORD 'lsd_editor1' IN ROLE lsd_editor;
CREATE USER lsd_editor2 PASSWORD 'lsd_editor2' IN ROLE lsd_editor;
CREATE USER lsd_user1 PASSWORD 'lsd_user1' IN ROLE lsd_user;


-- 2. Whenever a new dataset is added by an editor,
--   1. assign ownership to the group role
--   ALTER TABLE ppd_staging.schools OWNER TO ppd_editor;
--   2. Grant relevant permissions to users
--   GRANT SELECT ON ppd_staging.schools TO ppd_user;
