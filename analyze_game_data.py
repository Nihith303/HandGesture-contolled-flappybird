import mysql.connector
from mysql.connector import Error
from tabulate import tabulate
from db_operations import db  # Import the existing database connection

class GameAnalyzer:
    def __init__(self):
        self.connection = db.connection
        self.cursor = self.connection.cursor(dictionary=True)

    def get_high_scores(self, limit=10):
        """Get top N high scores across all patients"""
        try:
            query = """
                SELECT 
                    p.name,
                    p.patient_id,
                    p.high_score,
                    RANK() OVER (ORDER BY p.high_score DESC) as `rank`,
                    MAX(gs.session_date) as last_played_date,
                    MAX(gs.start_time) as last_played_time
                FROM patients p
                LEFT JOIN game_sessions gs ON p.patient_id = gs.patient_id
                WHERE p.high_score > 0
                GROUP BY p.patient_id, p.name, p.high_score
                ORDER BY p.high_score DESC
                LIMIT %s
            """
            self.cursor.execute(query, (limit,))
            return self.cursor.fetchall()
        except Error as e:
            print(f"Error fetching high scores: {e}")
            return []

    def get_patient_stats(self, patient_id=None):
        """Get detailed statistics for a specific patient or all patients"""
        try:
            query = """
                WITH patient_stats AS (
                    SELECT 
                        p.name,
                        p.patient_id,
                        COUNT(gs.id) as total_sessions,
                        COALESCE(SUM(gs.duration_seconds), 0) as total_playtime_seconds,
                        p.high_score as best_score,
                        ROUND(AVG(gs.score), 2) as avg_session_score,
                        RANK() OVER (ORDER BY p.high_score DESC) as rank_by_highscore,
                        RANK() OVER (ORDER BY COALESCE(SUM(gs.duration_seconds), 0) DESC) as rank_by_playtime
                    FROM patients p
                    LEFT JOIN game_sessions gs ON p.patient_id = gs.patient_id
                    GROUP BY p.patient_id, p.name, p.high_score
                )
                SELECT * FROM patient_stats
            """
            params = ()
            if patient_id:
                query += " WHERE patient_id = %s"
                params = (patient_id,)
            
            query += " ORDER BY best_score DESC, total_playtime_seconds DESC"
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Error as e:
            print(f"Error fetching patient stats: {e}")
            return []

    def get_session_analysis(self):
        """Analyze session data with various window functions"""
        try:
            query = """
                SELECT 
                    p.name,
                    gs.patient_id,
                    gs.session_date,
                    gs.start_time,
                    gs.duration_seconds,
                    gs.score,
                    p.high_score as patient_high_score,
                    RANK() OVER (PARTITION BY gs.patient_id ORDER BY gs.score DESC) as session_score_rank,
                    RANK() OVER (PARTITION BY gs.patient_id ORDER BY gs.duration_seconds DESC) as duration_rank,
                    LAG(gs.score, 1) OVER (PARTITION BY gs.patient_id ORDER BY gs.session_date, gs.start_time) as prev_session_score,
                    gs.score - LAG(gs.score, 1) OVER (PARTITION BY gs.patient_id ORDER BY gs.session_date, gs.start_time) as score_improvement,
                    ROUND(AVG(gs.score) OVER (PARTITION BY gs.patient_id), 2) as avg_session_score
                FROM game_sessions gs
                JOIN patients p ON gs.patient_id = p.patient_id
                ORDER BY p.name, gs.session_date DESC, gs.start_time DESC
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"Error in session analysis: {e}")
            return []

    def get_daily_statistics(self):
        """Get daily statistics for all patients"""
        try:
            query = """
                WITH daily_stats AS (
                    SELECT 
                        DATE(gs.session_date) as play_date,
                        gs.patient_id,
                        COUNT(*) as session_count,
                        SUM(gs.duration_seconds) as playtime_seconds,
                        MAX(gs.score) as best_session_score
                    FROM game_sessions gs
                    GROUP BY DATE(gs.session_date), gs.patient_id
                )
                SELECT 
                    ds.play_date,
                    COUNT(DISTINCT ds.patient_id) as active_players,
                    SUM(ds.session_count) as total_sessions,
                    SUM(ds.playtime_seconds) as total_playtime_seconds,
                    ROUND(AVG(ds.playtime_seconds), 2) as avg_playtime_seconds,
                    MAX(ds.best_session_score) as best_session_score,
                    (SELECT MAX(p.high_score) 
                     FROM patients p 
                     JOIN game_sessions gs2 ON p.patient_id = gs2.patient_id 
                     WHERE DATE(gs2.session_date) = ds.play_date) as daily_high_score
                FROM daily_stats ds
                GROUP BY ds.play_date
                ORDER BY ds.play_date DESC
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"Error fetching daily stats: {e}")
            return []

def format_duration(duration):
    """Convert duration to HH:MM:SS format
    
    Args:
        duration: Can be an integer (seconds), timedelta, or None
    """
    if duration is None:
        return "00:00:00"
        
    # Handle timedelta objects
    if hasattr(duration, 'total_seconds'):
        total_seconds = int(duration.total_seconds())
    else:
        # Assume it's already in seconds
        total_seconds = int(duration)
        
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def display_results(data, title):
    """Display query results in a formatted table"""
    if not data:
        print(f"No data available for {title}")
        return
    
    # Format duration fields if they exist in the data
    formatted_data = []
    for row in data:
        formatted_row = {}
        for key, value in row.items():
            if 'duration' in key.lower() or 'playtime' in key.lower() or 'time' in key.lower():
                formatted_row[key] = format_duration(value) if value is not None else "N/A"
            else:
                formatted_row[key] = value
        formatted_data.append(formatted_row)
    
    print(f"\n=== {title} ===")
    print(tabulate(formatted_data, headers="keys", tablefmt="grid"))

def main():
    analyzer = GameAnalyzer()
    
    while True:
        print("\nGame Data Analysis Menu:")
        print("1. View Top High Scores")
        print("2. View Player Statistics")
        print("3. View Session Analysis")
        print("4. View Daily Statistics")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == '1':
            limit = input("Enter number of top scores to display (default 10): ")
            try:
                limit = int(limit) if limit.strip() else 10
                data = analyzer.get_high_scores(limit)
                display_results(data, f"Top {limit} High Scores")
            except ValueError:
                print("Please enter a valid number.")
                
        elif choice == '2':
            patient_id = input("Enter patient ID (leave empty for all patients): ").strip()
            data = analyzer.get_patient_stats(patient_id if patient_id else None)
            display_results(data, "Player Statistics")
            
        elif choice == '3':
            data = analyzer.get_session_analysis()
            display_results(data, "Session Analysis")
            
        elif choice == '4':
            data = analyzer.get_daily_statistics()
            display_results(data, "Daily Statistics")
            
        elif choice == '5':
            print("Exiting...")
            break
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    try:
        main()
    except Error as e:
        print(f"Database error: {e}")
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    finally:
        if 'analyzer' in locals():
            analyzer.cursor.close()
