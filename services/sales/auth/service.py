from database.database import get_connection
from werkzeug.security import check_password_hash

def get_vendor_by_email(mail):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM vendors
        WHERE mail = %s
        """,
        (mail,)
    )
    vendor = cursor.fetchone()

    connection.close()

    return vendor


def authenticate_vendor(mail, password):
    vendor = get_vendor_by_email(mail)

    if vendor is None:
        return None

    if not vendor["active"]:
        return None

    if not check_password_hash(vendor["password"], password):
        return None

    return vendor