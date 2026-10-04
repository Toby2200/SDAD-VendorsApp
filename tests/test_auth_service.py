from auth.service import authenticate_vendor, get_vendor_by_email

#test for authenticate_vendor function
def test_authenticate_vendor_with_correct_credentials():
    vendor = authenticate_vendor("andres@test.com", "123456")

    assert vendor is not None
    assert vendor["name"] == "Andres"

def test_authenticate_vendor_with_incorrect_password():
    vendor = authenticate_vendor("andres@test.com", "wrongpassword")

    assert vendor is None

def test_authenticate_vendor_with_nonexistent_email():
    vendor = authenticate_vendor("notmail@test.com", "123456")

    assert vendor is None

def test_authenticate_vendor_with_inactive_vendor():
    vendor = authenticate_vendor("carlos@test.com", "123456")

    assert vendor is None

#Test for get_vendor_by_email function
def test_get_vendor_by_email_found():
    vendor = get_vendor_by_email("andres@test.com")
    assert vendor is not None
    assert vendor["name"] == "Andres"

def test_get_vendor_by_email_not_found():
    vendor = get_vendor_by_email("unknown@test.com")
    assert vendor is None