from vidriados.vidriado_detalle_vista import VidriadoDetalleVista


class VidriadosControlador:
    """Controlador del módulo de vidriados.

    Gestiona la apertura de vistas de detalle sin cerrar
    ventanas previamente abiertas, permitiendo la comparación
    simultánea de varios vidriados.
    """

    def __init__(self, db_path):
        self.db_path = db_path
        self._detalles_abiertos = []

    def obtener_lista_filtrable(self):
        from vidriados.vidriados_modelo import VidriadosModelo
        modelo = VidriadosModelo(self.db_path)
        return modelo.obtener_lista_filtrable()

    def abrir_detalle(self, vidriado_id, on_change=None):
        from vidriados.vidriados_modelo import VidriadosModelo
        modelo = VidriadosModelo(self.db_path)
        datos = modelo.obtener_por_id(vidriado_id)
        if not datos:
            return

        vista = VidriadoDetalleVista(
            self.db_path,
            datos,
            on_delete=on_change
        )

        self._detalles_abiertos.append(vista)
        vista.destroyed.connect(lambda *_: self._detalles_abiertos.remove(vista))
        vista.show()

    def crear_nuevo(self, parent=None, datos=None):
        from vidriados.vidriado_editar_vista import VidriadoEditarVista

        on_close = None
        if parent and hasattr(parent, "_cargar_vidriados"):
            on_close = parent._cargar_vidriados

        vista = VidriadoEditarVista(
            self.db_path,
            datos=datos,
            nuevo=True,
            on_close=on_close
        )

        self._detalles_abiertos.append(vista)
        vista.destroyed.connect(lambda *_: self._detalles_abiertos.remove(vista))
        vista.show()
