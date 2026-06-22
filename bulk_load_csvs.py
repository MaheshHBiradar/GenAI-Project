import os
import sys
import time
import psycopg2
from psycopg2 import sql

sys.path.insert(0, "./abcl_ai_platform")
from app.database import engine
from app.models.sentinel import Base

def bulk_load():
    print("[SENTINEL] Creating all database tables using SQLAlchemy...")
    Base.metadata.create_all(bind=engine)
    print("[SENTINEL] Tables created successfully.")

    csv_dir = "./abcl_sample_data_500k"
    
    # Read row counts to establish table order if needed, or just read all csv files
    csv_files = [f for f in os.listdir(csv_dir) if f.endswith(".csv") and f != "row_counts.csv"]
    
    # We want to load them. Since we disable constraints during load, order doesn't matter,
    # but let's do it cleanly.
    
    # Get raw connection from SQLAlchemy engine to run copy_expert
    raw_conn = engine.raw_connection()
    try:
        with raw_conn.cursor() as cur:
            # Disable triggers and foreign key constraints for this session
            print("[SENTINEL] Disabling foreign keys and triggers for session...")
            cur.execute("SET session_replication_role = 'replica';")
            
            total_rows = 0
            start_time = time.time()
            
            for csv_file in csv_files:
                table_name = csv_file.replace(".csv", "")
                csv_path = os.path.join(csv_dir, csv_file)
                
                # Get the headers from the CSV file
                with open(csv_path, 'r', encoding='utf-8') as f:
                    header_line = f.readline().strip()
                
                headers = [h.strip() for h in header_line.split(',')]
                
                # Build the COPY statement
                # Format: COPY table_name (col1, col2, ...) FROM STDIN WITH (FORMAT CSV, HEADER TRUE, NULL '')
                columns_str = ", ".join(f'"{h}"' for h in headers)
                copy_query = f'COPY "{table_name}" ({columns_str}) FROM STDIN WITH (FORMAT CSV, HEADER TRUE, NULL \'\')'
                
                print(f"[SENTINEL] Importing {csv_file} into '{table_name}' table...")
                sub_start = time.time()
                
                with open(csv_path, 'r', encoding='utf-8') as f:
                    cur.copy_expert(copy_query, f)
                
                # Get row count of what was imported
                cur.execute(f'SELECT COUNT(*) FROM "{table_name}"')
                row_count = cur.fetchone()[0]
                total_rows += row_count
                
                print(f"           Imported successfully in {time.time() - sub_start:.2f}s (Current row count: {row_count})")
            
            # Re-enable triggers and constraints
            print("[SENTINEL] Re-enabling foreign keys and triggers...")
            cur.execute("SET session_replication_role = 'origin';")
            
            raw_conn.commit()
            print(f"[SENTINEL] Bulk load complete! Total rows in database: {total_rows} in {time.time() - start_time:.2f}s")
            
    except Exception as e:
        raw_conn.rollback()
        print(f"[ERROR] Bulk load failed: {e}")
        raise
    finally:
        raw_conn.close()

if __name__ == "__main__":
    bulk_load()
