from qgis.core import *
import os

version = '_v1.0.0'
layers = QgsProject.instance().mapLayers().values()
project_home = QgsProject.instance().readPath("./")
for layer in layers:
    if layer.type() == QgsMapLayer.VectorLayer:
        style_manager = layer.styleManager()
        layer_styles = style_manager.styles()
        qml_output_dir = os.path.join(project_home, '/styles/qml')
        sld_output_dir = os.path.join(project_home, '/styles/sld')
        for single_style in layer_styles:
            layer_qml = single_style + version + '.qml'
            qml_output = os.path.join(qml_output_dir, layer_qml)
            layer_sld = single_style + version + '.sld'
            sld_output = os.path.join(sld_output_dir, layer_sld)
            layer.saveNamedStyle(qml_output)
            layer.saveSldStyle(sld_output)
