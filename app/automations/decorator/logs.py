def logs_history_factory(automation_nb):

    def logs_history(func):

        import json
        from datetime import datetime

        def wrapper(*args, **kwargs):
            
            with open('db.json', 'r') as reader :
                db_data = json.load(reader)

            db_data['automations'][automation_nb]['logs'].append(f"{datetime.now()} - RUN HAS STARTED")

            execute = func(*args, **kwargs)
            
            db_data['automations'][automation_nb]['logs'].append(f"{datetime.now()} - RUN HAS FINISHED")

            with open('db.json', 'w') as writer :
                json.dump(db_data, writer, indent=6)

            return execute
        
        return wrapper
    
    return logs_history