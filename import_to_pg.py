from jrdb import load
from jrdb import parse
import pandas as pd
import os
import psycopg2
import argparse
import io

def is_file_empty(file_path):
    return os.path.getsize(file_path) == 0

def import_txt_to_postgresql(directory, table_name, conn_params):
    # Initialize loader and parser
    loader = load.FileLoader()
    parser = parse.JrdbDataParser()
    
    with psycopg2.connect(**conn_params) as conn:
        cursor = conn.cursor()
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith(".txt"):
                    # Check if the file is empty
                    if is_file_empty(file_path):
                        print(f"Warning: Skipping empty file {file_path}")
                        continue
                    
                    try:
                        text_data = loader.load(file_path)
                        df = parser.parse(text_data, 'SED')  # Assuming 'SED' type for now
                    
                        # Convert DataFrame to CSV for PostgreSQL import
                        csv_data = df.to_csv(index=False)
                        csv_file = io.StringIO(csv_data)
                        cursor.copy_expert(f"COPY {table_name} FROM STDIN WITH CSV HEADER", csv_file)
                        print(f"Imported: {file_path} -> {table_name}")
                    except Exception as e:
                        print(f"Error processing file {file_path}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Import TXT files into a PostgreSQL database.")
    parser.add_argument("directory", help="Directory containing TXT files.")
    parser.add_argument("--dbname", required=True, help="Name of the PostgreSQL database.")
    parser.add_argument("--user", required=True, help="Username for the PostgreSQL database.")
    parser.add_argument("--password", required=True, help="Password for the PostgreSQL database.")
    parser.add_argument("--host", default="localhost", help="Host of the PostgreSQL database.")
    parser.add_argument("--port", default="5432", help="Port of the PostgreSQL database.")
    parser.add_argument("--table", required=True, help="Table name in the PostgreSQL database to import data into.")
    
    args = parser.parse_args()
    
    conn_params = {
        "dbname": args.dbname,
        "user": args.user,
        "password": args.password,
        "host": args.host,
        "port": args.port
    }
    
    import_txt_to_postgresql(args.directory, args.table, conn_params)

if __name__ == '__main__':
    main()


