# installation_records.py
import datetime
import datetime as dt
from corezilla.app import db


class InstallationRecords(db.Model):
    __tablename__ = "installation_record"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey("user.fs_uniquifier"), nullable=False)
    client_id = db.Column(db.String, db.ForeignKey("client.id"), nullable=False)
    configuration_id = db.Column(db.String, db.ForeignKey("client_configuration.id"), nullable=False)
    authorized_at = db.Column(db.DateTime, default=dt.datetime.now(datetime.UTC), nullable=False)

    # Relationships
    user = db.relationship("User", back_populates="installation_records")
    client = db.relationship("Client", back_populates="installation_records")
