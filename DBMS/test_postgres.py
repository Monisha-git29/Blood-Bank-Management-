import psycopg2

passwords = ["", "postgres", "admin", "root", "password", "1234", "kongu", "kec"]

def test_passwords():
    for pw in passwords:
        try:
            conn = psycopg2.connect(
                dbname="postgres",
                user="postgres",
                password=pw,
                host="localhost",
                connect_timeout=1
            )
            print(f"SUCCESS: Found working password: '{pw}'")
            conn.close()
            return pw
        except Exception as e:
            print(f"FAILED: '{pw}' - {e}")
    return None

if __name__ == "__main__":
    test_passwords()
