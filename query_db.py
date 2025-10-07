import sqlite3
import os

# Define the database path. IMPORTANT: Ensure this path is correct.
DATABASE_PATH = r"C:\Users\Sooryakant\Downloads\heart_disease_site\database.db"

def inspect_database(db_path):
    """Connects to the SQLite database and prints the content of all tables."""
    
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at: {db_path}")
        print("Please check the file path.")
        return

    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # Get all table names
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cur.fetchall()

        # List of tables we want to skip (internal SQLite tables)
        skip_tables = ["sqlite_sequence"] 
        
        print(f"--- Database Inspection: {os.path.basename(db_path)} ---")

        for table_name_tuple in tables:
            table_name = table_name_tuple[0]

            if table_name in skip_tables:
                continue

            print(f"\n=============================================")
            print(f"=== Table: {table_name.upper()} ===")
            print(f"=============================================")

            # Get column names (Schema)
            cur.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cur.fetchall()]
            
            # Print column headers
            header = " | ".join(columns)
            print(header)
            print("-" * len(header))

            # Fetch and print all rows
            cur.execute(f"SELECT * FROM {table_name}")
            for row in cur.fetchall():
                # For the 'users' table, we want to show the hashed password
                # For other tables, we print all content normally
                
                # Check if this is the users table and print the row
                if table_name == "users":
                    # Row contents example: (1, 'testuser1', '$pbkdf2:sha256:...')
                    # Print ID, Username, and a truncated Password Hash for readability
                    output = f"{row[0]} | {row[1]} | {str(row[2])[:30]}..."
                else:
                    # Print all data for other tables (predictions, contacts)
                    output = " | ".join(str(item) for item in row)
                    
                print(output)

    except sqlite3.Error as e:
        print(f"An SQLite error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

# Execute the inspection function
inspect_database(DATABASE_PATH)
