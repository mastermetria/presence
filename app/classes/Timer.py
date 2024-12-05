from functools import wraps
from datetime import datetime

class Timer:
    def __init__(self):
        self.created_at = datetime.now()  # Date de création de l'objet Timer
        self.count = {}  # Dictionnaire pour le nombre d'exécutions
        self.time_saved = {}  # Dictionnaire pour le temps total économisé

    def track(self, time_saved):
        """
        Décorateur pour suivre les exécutions et le temps économisé.
        :param time_saved: float, le temps économisé par exécution en heures.
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                func_name = func.__name__
                self.count[func_name] = self.count.get(func_name, 0) + 1
                self.time_saved[func_name] = self.time_saved.get(func_name, 0.0) + time_saved
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def get_function_stats(self, func_name):
        """
        Récupère les statistiques d'une fonction spécifique.
        :param func_name: str, le nom de la fonction.
        :return: dict, avec le nombre d'exécutions et le temps économisé.
        """
        return {
            "count": self.count.get(func_name, 0),
            "time_saved": self.time_saved.get(func_name, 0.0)
        }

    def get_all_stats(self):
        """
        Récupère les statistiques de toutes les fonctions suivies.
        :return: dict, avec le nom de chaque fonction et ses statistiques.
        """
        return {
            func_name: {
                "count": self.count.get(func_name, 0),
                "time_saved": self.time_saved.get(func_name, 0.0)
            }
            for func_name in self.count.keys()
        }
    
    def get_total_time_saved(self):
        """
        Récupère le temps total économisé pour toutes les fonctions suivies.
        :return: float, le temps total économisé.
        """
        return sum(self.time_saved.values())

    def get_creation_date(self):
        """
        Récupère la date de création de l'objet Timer.
        :return: str, la date de création formatée.
        """
        return self.created_at.strftime('%Y-%m-%d')
