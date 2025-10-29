# import psycopg2
# from psycopg2 import sql, OperationalError


# def create_connection():
#     try:
#         # Create a connection to the local PostgreSQL server
#         connection = psycopg2.connect(
#             dbname="your_database_name",
#             user="your_username",
#             password="your_password",
#             host="localhost",
#             port="5432",  # default PostgreSQL port
#         )

#         print("✅ Connection to PostgreSQL established successfully!")

#         return connection

#     except OperationalError as e:
#         print("❌ Error while connecting to PostgreSQL:", e)
#         return None


# def main():
#     conn = create_connection()

#     if conn:
#         # Create a cursor to execute SQL commands
#         cursor = conn.cursor()

#         # Example query
#         cursor.execute("SELECT version();")

#         # Fetch result
#         version = cursor.fetchone()
#         print("🧩 PostgreSQL version:", version)

#         # Close cursor and connection
#         cursor.close()
#         conn.close()
#         print("🔒 Connection closed.")


# if __name__ == "__main__":
#     main()


import csv


def read_csv_file(filename):
    try:
        # Open the CSV file
        with open(filename, mode="r", encoding="utf-8") as file:
            csv_reader = csv.reader(file)

            # Read the header (first row)
            headers = next(csv_reader)
            print(f"🧾 Headers: {headers}")

            # Read each remaining row
            print("\n📄 Data:")
            for row in csv_reader:
                print(row)

    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
    except Exception as e:
        print(f"⚠️ Error reading file: {e}")


if __name__ == "__main__":
    # Change this to your actual CSV file path
    file_path = "data.csv"
    read_csv_file(file_path)
