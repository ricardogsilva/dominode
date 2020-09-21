from qgis.core import *
import os

version = '_v1.0.0'
manager = QgsProject.instance().layoutManager()
project_home = QgsProject.instance().readPath("./")
output_dir = os.path.join(project_home, '/templates')
for layout in manager.printLayouts():
    qpt_layout = layout.name() + version + '.qpt'
    layout_template = os.path.join(output_dir, qpt_layout)
    layout.saveAsTemplate(layout_template, QgsReadWriteContext())
