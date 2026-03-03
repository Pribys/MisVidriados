**17/01/2026**
Comienzo aplicación "Mis Vidriados". El primer archivo generado es mis_vidriados_app, que es la ventana de entrada a la aplicación. Para general el sistema de vistas se ha instalado PySide6 en Python. sigo con el módulo de materias primas. El primer archivo generado es materias_primas_bd, para la comunicación con la base de datos, también se han generado materias_primas _logica y materias_primas_vista. Se colocan dentro de la carpeta materias_primas. Se genera una segunda versión de mis_vidriados_app para integrar el módulo de materias primas. Se crea materias_primas_dialogo para la introducción o edición de materias primas. Dejo funcionando correctamente el módulo de materias primas.

**18/01/2026**
El siguiente módulo es el CRUD de vidriados. He colocado las imágenes en la carpeta imagenes_vidriados y se ha creado la carpeta vidriados para contener los archivos del módulo: vidriado_detalle_vista, abre una ventana con los detalles de un vidriado concreto; vidriado_editar_vista, para editar los datos del vidriado; vidriados_controlador, para la lógica del módulo; vidriados_modelo, para la comunicación con la base de datos; y vidriados_vista, para la vista principal en la app, que es una zona de filtros para hacer una selección de vidriados. ChatGPT comienza a no dar pie con bola, hago un primer guardado del todos los archivos del módulo que modifique(.pyold)

**22/01/2026**
Queda cerrada una versión completa del módulo base de datos de vidriados

**24/01/2026**
Ayer me di cuenta de que faltaba por hacer la parte de gestión de imágenes y en eso estamos. Para no sobrecargar el archivo vidriado_editar_vista se ha creado imagenes_vidriado_widget para la gestión de imágenes. vidriado_editar_vista.pyold4 es la versión antes de importar la carga de imágenes...Ahora sí creo que el módulo está acabado.  

Comienzo el módulo Seger. Guardo mis_vidriados_app.pyold. Esta puta mierda de chatGPT es incapaz de hacer nada a derechas así que voy a tratar de copiar el módulo Seger de la app anterior en esta.

**25/01/2026**  
Módulo Seger terminado a falta de la exportación para crear nuevo vidriado. Para ello se retoca vidriados_controlador del módulo de vidriados. Guardo el antiguo como vidriados_controlador.pyold7, tambien guardo mis_vidriados_app.pyold1

**26/01/2026**  
Ayer se estropearon muchas cosas que ha habido que arreglar y quedó un archivo seger_vista que pasaba de 300 líneas, por lo que ha habido que reducirlo extrayendo parte del código en seger_vista_ui. seger_vista.pyold7 funciona e incluye la reducción de código y permite guardar vidriados calculados desde el módulo Seger. El problema es que al guardar los vidriados desde ahí no se refresca la vista del CRUD de vidriados. Para lograr ese refresco hay un nuevo seger_vista y también hubo que modificar mis_vidriados_app. Guardo la versión anterior de este como old1.  
Comienzo el módulo de teoría.

**27/01/2026**
Comienzo el módulo Currie...guardo currie_vista.pyold en un punto en que se desarrollan bien los cálculos de las cuatro esquinas pero falta todo el formateo de la vista

**29/01/2026**
El módulo está casi acabado, voy a incluir la posibilidad de crear un experimento nuevo escribiendo todos los campos sin pasar por Seger. Guardo currie_vista.pyold6, currie_widget_esquinas.pyold5, currie_editor.pyold. De momento, no se ha conseguido, pero se ha arreglado un problema gordo sobre la creación de nuevos vidriados usando Seger. De momento, desisto de la opción de crear nuevo experimento sin pasar por Seger

**30/01/2026**
Añado una pestaña para tener un cuaderno para anotaciones. Guardo mis_vidriados_app.pyold4

**27/02/2026**
Estoy cambiando el módulo seger para que admita cambios en la receta sobre los cálculos hechos por la aplicación. Guardo seger_vista.pyold, seger_vista_ui.pyold1 y seger_cuadratura.pyold