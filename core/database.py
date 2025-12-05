import sqlite3
import time
from typing import List, Dict, Any

class DatabaseManager:
    def __init__(self, db_name="bot_data.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._setup_tables()

    def _setup_tables(self):
        """Creates database tables if they don't exist."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS channels (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                success_count INTEGER DEFAULT 0,
                attempt_count INTEGER DEFAULT 0,
                total_value_usd REAL DEFAULT 0
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS claims (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER NOT NULL,
                channel_id INTEGER,
                status TEXT NOT NULL,
                amount REAL,
                currency TEXT,
                value_usd REAL,
                FOREIGN KEY (channel_id) REFERENCES channels (id)
            )
        """)
        self.conn.commit()

    def ensure_channel_exists(self, channel_id: int, channel_name: str):
        """Adds a channel to the database if it's not already there."""
        self.cursor.execute("INSERT OR IGNORE INTO channels (id, name) VALUES (?, ?)", (channel_id, channel_name))
        self.conn.commit()

    def log_claim(self, channel_id: int, status: str, amount: float = 0, currency: str = "", value_usd: float = 0):
        """Logs a claim attempt and updates channel stats."""
        timestamp = int(time.time())
        
        # Log the individual claim
        self.cursor.execute(
            "INSERT INTO claims (timestamp, channel_id, status, amount, currency, value_usd) VALUES (?, ?, ?, ?, ?, ?)",
            (timestamp, channel_id, status, amount, currency, value_usd)
        )

        # Update channel aggregate stats
        self.cursor.execute("UPDATE channels SET attempt_count = attempt_count + 1 WHERE id = ?", (channel_id,))
        if status == 'SUCCESS':
            self.cursor.execute(
                "UPDATE channels SET success_count = success_count + 1, total_value_usd = total_value_usd + ? WHERE id = ?",
                (value_usd, channel_id)
            )
        self.conn.commit()

    def get_session_stats(self) -> Dict[str, Any]:
        """Gets stats for the current day."""
        today_start = int(time.mktime(time.strptime(time.strftime('%Y-%m-%d'), '%Y-%m-%d')))
        
        self.cursor.execute("SELECT COUNT(*), SUM(value_usd) FROM claims WHERE status = 'SUCCESS' AND timestamp >= ?", (today_start,))
        result = self.cursor.fetchone()
        
        self.cursor.execute("SELECT COUNT(*) FROM claims WHERE timestamp >= ?", (today_start,))
        total_attempts_today = self.cursor.fetchone()[0]

        claimed_today = result[0] if result[0] is not None else 0
        value_today = result[1] if result[1] is not None else 0.0
        
        return {
            "claimed_today": claimed_today,
            "value_today": value_today,
            "attempts_today": total_attempts_today
        }

    def get_top_channels(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Gets the most profitable channels from the database."""
        self.cursor.execute(
            "SELECT name, success_count, total_value_usd FROM channels ORDER BY total_value_usd DESC LIMIT ?", (limit,)
        )
        return [{"name": name, "success": success, "value": value} for name, success, value in self.cursor.fetchall()]

    def get_total_stats(self) -> Dict[str, int]:
        """Get lifetime stats."""
        self.cursor.execute("SELECT SUM(attempt_count), SUM(success_count) FROM channels")
        result = self.cursor.fetchone()
        attempts = result[0] if result[0] is not None else 0
        successes = result[1] if result[1] is not None else 0
        return {"attempts": attempts, "successes": successes}
