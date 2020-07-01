# Data Workflows

The following data workflows are described in this document:

1. Dataset ingestion - Applies to when a new dataset is brought into the DomiNode platform;

2. Dataset modification - Applies whenever an existing DomiNode dataset needs to be updated;

   2.1. Modify data;
   2.2. Modify metadata;
   2.3. Modify style.
   
3. Dataset removal - Applies whenever an existing DomiNode dataset needs to be removed;


## 1. Dataset Ingestion

Database ingestion workflow generally proceeds like this:

1.1. Acquire dataset

1.2. Load dataset onto QGIS 

1.3. Use QGIS DB Manager to upload dataset to staging schema

   In order to be able to upload a dataset onto DomiNode's staging DB schema you 
   must have a DB user with sufficient permissions. For each department, there 
   are two DB groups:
   
   -  `{department}_editor` - Users in this group are allowed to upload new 
      datasets onto the department's staging area and are also allowed to 
      modify them
      
   -  `{department}_user` - Users in this group are allowed to access 
      datasets that exist on the department's staging area but are not allowed
      to modify them

   1.3.1. Import dataset
   
   -  Rename the dataset in order to match DomiNode conventions
   -  Use a proper version to reflect the dataset's current status
   -  Set the target SRS to one of the DomiNode allowed SRS'
   -  Select the option to replace existing table if it exists
   -  Create a spatial index for the dataset
   -  Convert field names to lowercase
   
   1.3.2. Assign write permissions to department editors
   
   Still using _DB Manager_, issue an SQL query to transfer ownership of the 
   dataset to your parent group (`{department}_editor`). This will allow 
   other editors to access the dataset:

   ```sql
   -- ALTER TABLE {schema}.{table} OWNER TO {department}_editor;
   ALTER TABLE lsd_staging.dominode_lsd_rrmap OWNER TO lsd_editor;
   ```
   
   At this point, only editors from your department are able to access the 
   dataset.
   
   1.3.3. Assign read-only permissions to department users
   
   Still using _DB Manager_, issue another SQL query to allow non editors
   from your department read-only access to the dataset:
   
   ```sql
   -- GRANT SELECT ON {schema}.{table} TO {reader-group};
   GRANT SELECT ON lsd_staging.dominode_lsd_rrmap TO lsd_user;
   ```
   
   At this point any users from your department are able to see the dataset,
   and users that are part of the `{department}_editor` group are able to
   edit it.
   
   Please note that users from other departments are not able to use the newly
   added dataset. It is visible only to your department.

1.4. Process dataset

   Perform any actions that may be required for the dataset in order to be usable
   in the context of DomiNode
   
   -  Check the dataset's thematic content
   -  Add, edit or remove dataset attributes in order to comply with expected data schema
   -  etc.

1.5. Validate dataset

   Use the QGIS plugin `Dataset QA Workbench` with a suitable checklist in order 
   to validate the processed dataset

1.6. If validation succeeds, transfer dataset to public schema, where it shall be read-only

1.7. Generate QGIS style

1.8. Validate QGIS style

1.9. If style validation succeeds, save QGIS style in the DB on the public 
   schema (style shall also be read-only) - Be sure to include the style's 
   version on its name
   
1.10. Generate SLD style (or perhaps tweak the QGIS-generated SLD style)

1.11. Validate SLD style

1.12. If SLD style validation succeeds, save SLD style in the filesystem - Be 
   sure to properly version the style
   
1.13. Publish dataset on GeoServer, so that it may be accessed via WMS and WFS
   with the previously validated SLD style

1.14. Insert dataset onto GeoNode with privileged visibility. The dataset shall
   be visible only to editors at this point

1.15. Create dataset metadata record

1.16. Validate metadata

1.17. If metadata validation succeeds, publish dataset on GeoNode so that it 
   is accessible to general public
   

## 2. Dataset modification

In DomiNode we are applying the concept of immutability to published datasets 
as much as possible. This means that, once a dataset has been published, it 
shall no longer be modified. Any alterations to it shall be made on a copy
of the dataset and then republished under a new version. In order to enable such
workflow, datasets and their respective styles and metadata must be properly:

-  named
-  versioned

### 2.1. Modify data

2.1.1. Copy data from the public schema to the staging schema - Change the 
   dataset's version in order to indicate an intermediary version
2.1.2. Perform any modifications needed
2.1.3. Validate dataset
2.1.4. If dataset validation succeeds, transfer dataset to the public schema

### 2.2. Modify metadata
### 2.3. Modify style


## 3. Dataset removal

