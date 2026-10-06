from alg_preemptive import (
    generar_resumen,
    generar_timeline,
    generar_timeline_no_apropiativo,
)


class PriorityScheduler:
    @staticmethod
    def generar_timeline(procesos, apropiativo=True):
        generador = generar_timeline if apropiativo else generar_timeline_no_apropiativo
        return generador(
            procesos,
            criterio=lambda proceso, _: proceso["priority"],
        )

    @staticmethod
    def simular(procesos, apropiativo=True):
        timeline = PriorityScheduler.generar_timeline(procesos, apropiativo)
        tipo = "Apropiativo" if apropiativo else "No apropiativo"
        return generar_resumen(
            procesos,
            timeline,
            f"Prioridad ({tipo})",
        )
