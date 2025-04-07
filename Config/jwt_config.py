"""Konfigurationseinstellungen für JSON Web Tokens (JWT).

Dieses Modul definiert die zentralen Konstanten, die für die Erstellung,
Signierung und Validierung von JWT-Zugriffstokens in der Anwendung benötigt werden.

Es legt den geheimen Schlüssel, den verwendeten Algorithmus und die
Gültigkeitsdauer der Tokens fest.

Attributes:
    SECRET_KEY (str): Der geheime Schlüssel für die HMAC-Signierung von JWTs.
                      Wird zur Erstellung und Überprüfung der Token-Signatur verwendet.
    ALGORITHM (str): Der Verschlüsselungsalgorithmus, der für die Signierung
                     des Tokens verwendet wird.
    ACCESS_TOKEN_EXPIRE_MINUTES (int): Die Zeitspanne in Minuten, nach der ein
                                       ausgestelltes Zugriffstoken abläuft.
"""

# Schlüssel zur Verschlüsselung und Entschlüsselung des JWT Tokens
SECRET_KEY = "4ddbb4ed971024eba33f24912a5e229c72e02c40f8fcb467a34b5b99fbb08d35"
# Algorithmus der zur Ver- und Entschlüsselung verwendet wird
ALGORITHM = "HS256"
# Anzahl der Minuten in denen der Token gültig ist
ACCESS_TOKEN_EXPIRE_MINUTES = 30
