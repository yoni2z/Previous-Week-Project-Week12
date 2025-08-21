import psycopg2
import pandas as pd
import yaml
import logging
import os

logging.basicConfig(filename='logs/database.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PostgresDB:
    def __init__(self, config_path='config.yaml'):
        """Initialize connection to PostgreSQL database using config.yaml."""
        try:
            # Load config
            if not os.path.exists(config_path):
                raise FileNotFoundError(f"Config file {config_path} not found.")
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            db_config = config.get('database', {})
            
            # Extract credentials
            self.user = db_config.get('user', 'postgres')
            self.password = db_config.get('password', '')
            self.dbname = db_config.get('dbname', 'bank_reviews')
            self.host = db_config.get('host', 'localhost')
            self.port = db_config.get('port', '5432')

            # Connect
            self.conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            self.cursor = self.conn.cursor()
            logging.info("Connected to PostgreSQL database.")
        except Exception as e:
            logging.error(f"Failed to connect to database: {e}")
            raise

    def create_tables(self):
        """Create banks and reviews tables with foreign key relationship."""
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS banks (
                    bank_id INTEGER PRIMARY KEY,
                    bank_name VARCHAR(100) NOT NULL
                );
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS reviews (
                    review_id INTEGER PRIMARY KEY,
                    review_text TEXT,
                    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                    date DATE,
                    bank_id INTEGER,
                    source VARCHAR(50),
                    sentiment_label VARCHAR(50),
                    sentiment_score FLOAT,
                    themes VARCHAR(500),
                    FOREIGN KEY (bank_id) REFERENCES banks(bank_id)
                );
            """)
            self.conn.commit()
            logging.info("Tables created successfully.")
        except Exception as e:
            logging.error(f"Error creating tables: {e}")
            self.conn.rollback()
            raise

    def insert_data(self, csv_path='data/insights/review_analysis.csv'):
        """Insert data from CSV into banks and reviews tables."""
        try:
            df = pd.read_csv(csv_path)
            # Insert unique banks
            banks = df['bank_name'].unique()
            for i, bank in enumerate(banks, 1):
                self.cursor.execute(
                    "INSERT INTO banks (bank_id, bank_name) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                    (i, bank)
                )
            
            # Insert reviews
            for idx, row in df.iterrows():
                bank_id = list(banks).index(row['bank_name']) + 1
                themes_str = ','.join(eval(row['themes'])) if isinstance(row['themes'], str) and row['themes'].startswith('[') else row['themes']
                self.cursor.execute("""
                    INSERT INTO reviews (review_id, review_text, rating, date, bank_id, source, sentiment_label, sentiment_score, themes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    idx + 1,
                    row['review_text'],
                    row['rating'],
                    row['date'],
                    bank_id,
                    row['source'],
                    row['sentiment_label'],
                    row['sentiment_score'],
                    themes_str
                ))
            
            self.conn.commit()
            logging.info(f"Inserted {len(df)} reviews into database.")
        except Exception as e:
            logging.error(f"Error inserting data: {e}")
            self.conn.rollback()
            raise

    def export_dump(self, output_path='docs/bank_reviews_dump.sql'):
        """Export database schema and data to SQL dump (manual trigger via pg_dump)."""
        logging.info(f"Run `pg_dump -U {self.user} {self.dbname} > {output_path}` manually.")

    def close(self):
        """Close cursor and connection."""
        try:
            self.cursor.close()
            self.conn.close()
            logging.info("Database connection closed.")
        except Exception as e:
            logging.error(f"Error closing connection: {e}")

if __name__ == "__main__":
    try:
        db = PostgresDB(config_path='config.yaml')
        db.create_tables()
        db.insert_data()
        db.close()
    except Exception as e:
        logging.error(f"Script execution failed: {e}")