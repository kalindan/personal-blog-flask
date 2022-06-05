from flask_login import current_user


def get_user_name():
    if current_user.is_authenticated:
        return current_user.name
    return None
