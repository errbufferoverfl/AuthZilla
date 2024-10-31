import enum


class ResponseType(enum.Enum):
    CODE = "code"  # authz code as described in Section 4.1.1
    TOKEN = "token"  # access token for implicit grant 4.2.1
