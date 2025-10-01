import mysql.connector
from mysql.connector import Error
from datetime import datetime
import time

class GameDatabase:
    def __init__(self, host="localhost", database="rehab_wings", user="root", password="Nihith&*3003"):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        self.cursor = None
        self.connect()
        self.initialize_database()

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            if self.connection.is_connected():
                self.cursor = self.connection.cursor()
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")
            raise

    def initialize_database(self):
        try:
            # Create patients table if not exists
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS patients (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    patient_id VARCHAR(50) NOT NULL UNIQUE,
                    high_score INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)

            # Create game_sessions table if not exists
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS game_sessions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    patient_id VARCHAR(50) NOT NULL,
                    session_date DATE NOT NULL,
                    start_time TIME NOT NULL,
                    end_time TIME,
                    duration_seconds INT,
                    score INT DEFAULT 0,
                    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
                )
            """)

            self.connection.commit()
        except Error as e:
            print(f"Error initializing database: {e}")
            raise

    def add_patient(self, name, patient_id):
        try:
            query = """
                INSERT INTO patients (name, patient_id)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE name = VALUES(name)
            """
            self.cursor.execute(query, (name, patient_id))
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error adding/updating patient: {e}")
            return False

    def start_session(self, patient_id):
        try:
            current_datetime = datetime.now()
            current_date = current_datetime.date()
            current_time = current_datetime.time()
            
            # Always create a new session
            query = """
                INSERT INTO game_sessions 
                (patient_id, session_date, start_time, score)
                VALUES (%s, %s, %s, 0)
            """
            self.cursor.execute(query, (patient_id, current_date, current_time.strftime("%H:%M:%S")))
            self.connection.commit()
            return self.cursor.lastrowid  # Return the new session ID
        except Error as e:
            print(f"Error starting session: {e}")
            return False

    def end_session(self, patient_id, score):
        try:
            current_datetime = datetime.now()
            current_date = current_datetime.date()
            current_time = current_datetime.time()
            
            # Get the patient's current high score
            self.cursor.execute("""
                SELECT COALESCE(high_score, 0) FROM patients WHERE patient_id = %s
            """, (patient_id,))
            patient_high_score = self.cursor.fetchone()[0] or 0
            
            # Update the high score if current score is higher
            new_high_score = max(patient_high_score, score)
            
            # Update the patient's high score if current score is higher
            self.cursor.execute("""
                UPDATE patients 
                SET high_score = %s 
                WHERE patient_id = %s AND (high_score IS NULL OR %s > high_score)
            """, (new_high_score, patient_id, score))
            
            # Get the most recent session for this patient
            self.cursor.execute("""
                SELECT id, start_time, session_date 
                FROM game_sessions 
                WHERE patient_id = %s 
                ORDER BY id DESC 
                LIMIT 1
            """, (patient_id,))
            
            session = self.cursor.fetchone()
            
            if session:
                session_id, start_time_str, session_date = session
                # Parse the start time string into a datetime object
                start_datetime = datetime.strptime(f"{session_date} {start_time_str}", "%Y-%m-%d %H:%M:%S")
                # Calculate duration in seconds
                duration = int((current_datetime - start_datetime).total_seconds())
                
                # Update the session with score and duration
                self.cursor.execute("""
                    UPDATE game_sessions 
                    SET end_time = %s,
                        duration_seconds = %s,
                        score = %s
                    WHERE id = %s
                """, (current_time, duration, score, session_id))
                
                self.connection.commit()
                return True
                
            return False
        except Error as e:
            print(f"Error ending session: {e}")
            return False

    def get_patient_stats(self, patient_id):
        try:
            query = """
                SELECT 
                    p.name,
                    p.patient_id,
                    COUNT(gs.id) as total_sessions,
                    COALESCE(SUM(gs.duration_seconds), 0) as total_play_time,
                    COALESCE(p.high_score, 0) as high_score
                FROM patients p
                LEFT JOIN game_sessions gs ON p.patient_id = gs.patient_id
                WHERE p.patient_id = %s
                GROUP BY p.id, p.name, p.patient_id, p.high_score
            """
            self.cursor.execute(query, (patient_id,))
            result = self.cursor.fetchone()
            if result:
                # Create a dictionary with explicit field names
                columns = [desc[0] for desc in self.cursor.description]
                return dict(zip(columns, result))
            else:
                # If patient exists but has no sessions yet
                query = "SELECT name, patient_id, COALESCE(high_score, 0) as high_score FROM patients WHERE patient_id = %s"
                self.cursor.execute(query, (patient_id,))
                patient = self.cursor.fetchone()
                if patient:
                    return {
                        'name': patient[0],
                        'patient_id': patient[1],
                        'total_sessions': 0,
                        'total_play_time': 0,
                        'high_score': int(patient[2])  # Ensure it's an int
                    }
            return None
        except Error as e:
            print(f"Error getting patient stats: {e}")
            return None

    def close(self):
        if self.connection and self.connection.is_connected():
            if self.cursor:
                self.cursor.close()
            self.connection.close()

# Singleton instance
db = GameDatabase()
