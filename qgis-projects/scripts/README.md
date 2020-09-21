# Introduction

This folder contains various pyqgis scripts which useful for the automation of some routine tasks.

## Running the scripts

`export_styles.py` - Used to export SLD and QML files for each layer theme.
`export_templates.py` - Used to export templates for the print layouts

* Open the script in QGIS python console.
* Change the output path for each script to point to your preferred output folder.
* Execute the script.

> Please note that the relevant directories need to be created prior to running the script to prevent errors. These include the `projectRoot/templates`, `projectRoot/styles/qml` and `projectRoot/styles/sld` directories.

**NB** Only run the scripts if you have modified the styles or the layouts in the current project.
