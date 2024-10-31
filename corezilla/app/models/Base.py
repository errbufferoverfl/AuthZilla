from corezilla.app import db


class BaseModel(db.Model):
    __abstract__ = True
    """
    Mixin that adds convenience methods for CRUD (create, read, update, delete) operations
    """

    @classmethod
    def create(cls, **kwargs):
        """
        Create a new record and save it the database given the passed in arguments which should represent the
        associated database object

        Warnings:
            No validation or sanitization is done in this function, so if non-nullable parameters are passed in
            SQLAlchemy will likely raise an IntegrityError.

        Args:
            **kwargs: parameters to set in the database columns

        Returns:
            sqlalchemy.db.Model that was created in the database
        """
        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit=True, **kwargs):
        """
        Updates specific fields of a record and save it the database given the passed in arguments which should
        represent the associated database object

        Warnings:
            No validation or sanitization is done in this function, so if non-nullable parameters are passed in
            SQLAlchemy will likely raise an IntegrityError.

            This update is reflective of a `PATCH` update rather than a `PUT`

        Args:
            commit (bool): whether to commit the record to the database or not
            **kwargs: parameters to set in the database columns

        Returns:
            sqlalchemy.db.Model that was created in the database
        """
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        """
        Commits a record to the database

        Warnings:
            No validation or sanitization is done in this function, so if non-nullable parameters are passed in
            SQLAlchemy will likely raise an IntegrityError.

        Args:
            commit (bool): whether to commit the record to the database or not
            **kwargs: parameters to set in the database columns

        Returns:
            sqlalchemy.db.Model that was created in the database
        """
        """Save the record."""
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        """
        Remove the record from the database

        Warnings:
            No validation or sanitization is done in this function, so if non-nullable parameters are passed in
            SQLAlchemy will likely raise an IntegrityError.

        Args:
            commit (bool): whether to commit the record to the database or not

        Returns:
            bool: TODO: fill this in
        """
        db.session.delete(self)
        return commit and db.session.commit()
