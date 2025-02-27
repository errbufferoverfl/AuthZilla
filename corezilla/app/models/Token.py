from corezilla.app import db


class Token(db.Model):
    """
    Token model to track issued OAuth tokens.
    """
    __tablename__ = "token"

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255), unique=True, nullable=False)
    token_type = db.Column(db.String(50), nullable=False, default="access_token")
    user_id = db.Column(db.Integer, db.ForeignKey("user.fs_uniquifier"), nullable=True)
    client_id = db.Column(db.String(255), db.ForeignKey("client.client_id"), nullable=False)
    scope = db.Column(db.Text, nullable=True)
    issued_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    expires_at = db.Column(db.DateTime, nullable=False)
    revoked = db.Column(db.Boolean, default=False, nullable=False)

    def revoke(self):
        """Mark token as revoked."""
        self.revoked = True
        db.session.commit()

    def is_active(self):
        """Check if the token is active and not expired or revoked."""
        from datetime import datetime
        return not self.revoked and self.expires_at > datetime.utcnow()

    def to_dict(self):
        """Return token details as a dictionary."""
        return {
            "token": self.token,
            "token_type": self.token_type,
            "user_id": self.user_id,
            "client_id": self.client_id,
            "scope": self.scope,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "revoked": self.revoked,
        }

    def __repr__(self):
        return f"<Token(token={self.token}, user_id={self.user_id}, client_id={self.client_id}, revoked={self.revoked})>"

    def __eq__(self, other):
        if isinstance(other, Token):
            return self.token == other.token and self.client_id == other.client_id
        return False

    def __hash__(self):
        return hash((self.token, self.client_id))