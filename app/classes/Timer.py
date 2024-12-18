from functools import wraps
from datetime import datetime
import locale


class Timer:

    def __init__(self):
        self.created_at = datetime.now()  # Date de création de l'objet Timer
        self.count = {}  # Dictionnaire pour le nombre d'exécutions
        self.time_saved = {}  # Dictionnaire pour le temps total économisé
        self.last_run_date = {}  # Dictionnaire pour la date du dernier lancement par fonction

    def track(self, time_saved):
        """
        Décorateur pour suivre les exécutions et le temps économisé.
        :param time_saved: float, le temps économisé par exécution en minutes.
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

    def monitor(self):
        """
        Décorateur pour suivre la date du dernier lancement d'une fonction.
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                func_name = func.__name__
                self.last_run_date[func_name] = datetime.now()
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def get_function_stats(self, func_name):
        """
        Récupère les statistiques d'une fonction spécifique.
        :param func_name: str, le nom de la fonction.
        :return: dict, avec le nombre d'exécutions, le temps économisé formaté et la date du dernier lancement.
        """
        time_saved_minutes = self.time_saved.get(func_name, 0.0)
        hours, minutes = divmod(time_saved_minutes, 60)
        
        if hours > 0:
            formatted_time_saved = f"{int(hours)} heures et {int(minutes)} minutes"
        else:
            formatted_time_saved = f"{int(minutes)} minutes"
        
        return {
            "count": self.count.get(func_name, 0),
            "time_saved": formatted_time_saved,
            "last_run_date": self.last_run_date.get(func_name, None),
            "created_at": self.created_at
        }


    def get_all_stats(self):
        """
        Récupère les statistiques de toutes les fonctions suivies.
        :return: dict, avec le nom de chaque fonction et ses statistiques.
        """
        return {
            func_name: {
                "count": self.count.get(func_name, 0),
                "time_saved": self.time_saved.get(func_name, 0.0),
                "last_run_date": self.last_run_date.get(func_name, None),
                "created_at": self.created_at.strftime('%A %d %B %Y, %H:%M:%S')
            }
            for func_name in self.count.keys()
        }

    def get_total_time_saved(self):
        """
        Récupère le temps total économisé pour toutes les fonctions suivies,
        formaté en heures et minutes si nécessaire.
        :return: str, le temps total formaté.
        """
        total_minutes = sum(self.time_saved.values())
        hours, minutes = divmod(total_minutes, 60)
        if hours > 0:
            return f"{int(hours)} heures et {int(minutes)} minutes"
        else:
            return f"{int(minutes)} minutes"

    def get_creation_date(self):
        """
        Récupère la date de création de l'objet Timer.
        :return: str, la date de création formatée.
        """
        return self.created_at.strftime('%d/%m/%Y')

