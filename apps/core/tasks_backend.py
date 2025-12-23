"""
Custom Django Tasks Backend pour Python 3.12
Contourne le bug de django_tasks avec TaskResult[T]
"""

from django_tasks.backends.base import BaseTaskBackend


class ImmediateBackend(BaseTaskBackend):
    """
    Backend qui exécute les tâches immédiatement et ignore les résultats.
    Évite le bug Python 3.12 avec TaskResult[T].__orig_class__
    """

    supports_defer = False
    supports_async_task = False

    def enqueue(self, task, args, kwargs):
        """Exécute la tâche immédiatement sans retourner de TaskResult."""
        try:
            # Exécuter la fonction directement
            task.func(*args, **kwargs)
        except Exception:
            # Ignorer les erreurs pour éviter de bloquer les saves
            pass
        # Retourner None au lieu de TaskResult pour éviter le bug
        return None
