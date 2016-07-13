
add_library(Qt5::dummySensorPlugin MODULE IMPORTED)

_populate_Sensors_plugin_properties(dummySensorPlugin RELEASE "sensors/qtsensors_dummy.dll")
_populate_Sensors_plugin_properties(dummySensorPlugin DEBUG "sensors/qtsensors_dummyd.dll")

list(APPEND Qt5Sensors_PLUGINS Qt5::dummySensorPlugin)
