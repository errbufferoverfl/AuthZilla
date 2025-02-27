from corezilla.app import db
from corezilla.app.models import User


class UserService:
    @staticmethod
    def get_user_by_id(user_id):
        """
        Retrieve a user by their ID.
        """
        return User.query.filter_by(id=user_id).first()

    @staticmethod
    def get_user_by_username_or_email(email_or_username):
        """
        """
        return User.query.filter((User.email == email_or_username) | (User.username == email_or_username)).first()

    @staticmethod
    def get_user_by_username(username):
        """
        """
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_user_by_email(email):
        """
        """
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_user_by_client(client):
        """
        Retrieve the user associated with a given client.
        """
        return User.query.filter_by(id=client.user_id).first()

    @staticmethod
    def get_users_paginated(page=1, per_page=20):
        """
        Retrieve a paginated list of users.
        """
        return User.query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def create_user(username, email, password_hash):
        """
        Create a new user and store it in the database.
        """
        user = User(username=username, email=email, password_hash=password_hash)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def update_user(user_id, username=None, email=None, password_hash=None):
        """
        Update user information.
        """
        user = UserService.get_user_by_id(user_id)
        if not user:
            return None

        if username:
            user.username = username
        if email:
            user.email = email
        if password_hash:
            user.password_hash = password_hash

        db.session.commit()
        return user

    @staticmethod
    def delete_user(user_id):
        """
        Delete a user from the database.
        """
        user = UserService.get_user_by_id(user_id)
        if not user:
            return None

        db.session.delete(user)
        db.session.commit()
        return True
