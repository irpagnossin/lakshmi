def cleanup(database):
    def decorator(f):
        def wrapper():
            database.candidates.drop()
            database.matches.drop()
            database.positions.drop()
            database.users.drop()
            f()

        return wrapper
    return decorator
