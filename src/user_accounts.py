import os
import sqlite3
import hashlib
import uuid
import json
from datetime import datetime

class UserDatabase:
    """
    Manages user accounts and saved financial profiles.
    """
    
    def __init__(self, db_path='data/users.db'):
        """Initialize the user database connection."""
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db_path = db_path
        # Don't maintain a persistent connection - will create new ones per method
        self.create_tables()
    
    def _get_connection(self):
        """Get a new database connection."""
        return sqlite3.connect(self.db_path)
    
    def create_tables(self):
        """Create the necessary database tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TEXT NOT NULL,
            last_login TEXT
        )
        ''')
        
        # Financial profiles table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS financial_profiles (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            profile_name TEXT NOT NULL,
            profile_data TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE (user_id, profile_name)
        )
        ''')
        
        # Analysis results table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_results (
            id TEXT PRIMARY KEY,
            profile_id TEXT NOT NULL,
            analysis_data TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (profile_id) REFERENCES financial_profiles (id)
        )
        ''')
        
        # Simulation results table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS simulation_results (
            id TEXT PRIMARY KEY,
            profile_id TEXT NOT NULL,
            simulation_data TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (profile_id) REFERENCES financial_profiles (id)
        )
        ''')
        
        # Achievements table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS achievements (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            achievement_type TEXT NOT NULL,
            achievement_data TEXT NOT NULL,
            achieved_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def _hash_password(self, password, salt=None):
        """
        Hash a password with a salt for secure storage.
        
        Args:
            password (str): Plain text password
            salt (str, optional): Salt to use. If None, a new salt is generated.
            
        Returns:
            tuple: (password_hash, salt)
        """
        if salt is None:
            salt = uuid.uuid4().hex
        
        # Create a hash combining password and salt
        hash_obj = hashlib.sha256((password + salt).encode())
        password_hash = hash_obj.hexdigest()
        
        return password_hash, salt
    
    def create_user(self, username, email, password):
        """
        Create a new user account.
        
        Args:
            username (str): Desired username
            email (str): User's email address
            password (str): Plain text password
            
        Returns:
            tuple: (success, message, user_id)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Check if username or email already exists
        cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
        if cursor.fetchone():
            conn.close()
            return False, "Username or email already exists", None
        
        # Hash the password
        password_hash, salt = self._hash_password(password)
        
        # Generate a unique ID
        user_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        
        # Insert the new user
        try:
            cursor.execute(
                "INSERT INTO users (id, username, email, password_hash, salt, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, username, email, password_hash, salt, current_time)
            )
            conn.commit()
            conn.close()
            return True, "User created successfully", user_id
        except sqlite3.Error as e:
            conn.close()
            return False, f"Database error: {e}", None
    
    def authenticate_user(self, username_or_email, password):
        """
        Authenticate a user login attempt.
        
        Args:
            username_or_email (str): Username or email address
            password (str): Plain text password
            
        Returns:
            tuple: (success, message, user_id)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Find the user
        cursor.execute(
            "SELECT id, password_hash, salt FROM users WHERE username = ? OR email = ?",
            (username_or_email, username_or_email)
        )
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return False, "Invalid username or email", None
        
        user_id, stored_hash, salt = result
        
        # Verify the password
        hash_attempt, _ = self._hash_password(password, salt)
        
        if hash_attempt == stored_hash:
            # Update last login time
            current_time = datetime.now().isoformat()
            cursor.execute(
                "UPDATE users SET last_login = ? WHERE id = ?",
                (current_time, user_id)
            )
            conn.commit()
            conn.close()
            return True, "Authentication successful", user_id
        else:
            conn.close()
            return False, "Invalid password", None
    
    def save_financial_profile(self, user_id, profile_name, profile_data):
        """
        Save a financial profile for a user.
        
        Args:
            user_id (str): ID of the user
            profile_name (str): Name of the profile
            profile_data (dict): Financial profile data
            
        Returns:
            tuple: (success, message, profile_id)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Check if the user exists
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            conn.close()
            return False, "User not found", None
        
        # Convert profile data to JSON
        profile_json = json.dumps(profile_data)
        
        # Generate a unique ID
        profile_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        
        try:
            # Check if a profile with this name already exists for this user
            cursor.execute(
                "SELECT id FROM financial_profiles WHERE user_id = ? AND profile_name = ?",
                (user_id, profile_name)
            )
            existing_profile = cursor.fetchone()
            
            if existing_profile:
                # Update existing profile
                profile_id = existing_profile[0]
                cursor.execute(
                    "UPDATE financial_profiles SET profile_data = ?, updated_at = ? WHERE id = ?",
                    (profile_json, current_time, profile_id)
                )
                message = "Profile updated successfully"
            else:
                # Insert new profile
                cursor.execute(
                    "INSERT INTO financial_profiles (id, user_id, profile_name, profile_data, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (profile_id, user_id, profile_name, profile_json, current_time, current_time)
                )
                message = "Profile created successfully"
            
            conn.commit()
            conn.close()
            return True, message, profile_id
        except sqlite3.Error as e:
            conn.close()
            return False, f"Database error: {e}", None
    
    def get_financial_profiles(self, user_id):
        """
        Get all financial profiles for a user.
        
        Args:
            user_id (str): ID of the user
            
        Returns:
            list: List of profile dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, profile_name, profile_data, created_at, updated_at FROM financial_profiles WHERE user_id = ? ORDER BY updated_at DESC",
            (user_id,)
        )
        
        profiles = []
        for row in cursor.fetchall():
            profile_id, name, data_json, created, updated = row
            profile = {
                "id": profile_id,
                "name": name,
                "data": json.loads(data_json),
                "created_at": created,
                "updated_at": updated
            }
            profiles.append(profile)
        
        conn.close()
        return profiles
    
    def get_financial_profile(self, profile_id):
        """
        Get a specific financial profile.
        
        Args:
            profile_id (str): ID of the profile
            
        Returns:
            dict: Profile data or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, user_id, profile_name, profile_data, created_at, updated_at FROM financial_profiles WHERE id = ?",
            (profile_id,)
        )
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        
        profile_id, user_id, name, data_json, created, updated = row
        profile = {
            "id": profile_id,
            "user_id": user_id,
            "name": name,
            "data": json.loads(data_json),
            "created_at": created,
            "updated_at": updated
        }
        
        conn.close()
        return profile
    
    def delete_financial_profile(self, profile_id, user_id):
        """
        Delete a financial profile.
        
        Args:
            profile_id (str): ID of the profile
            user_id (str): ID of the user (for security verification)
            
        Returns:
            tuple: (success, message)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Verify the profile belongs to the user
        cursor.execute(
            "SELECT id FROM financial_profiles WHERE id = ? AND user_id = ?",
            (profile_id, user_id)
        )
        
        if not cursor.fetchone():
            conn.close()
            return False, "Profile not found or access denied"
        
        try:
            # First delete any associated analysis or simulation results
            cursor.execute("DELETE FROM analysis_results WHERE profile_id = ?", (profile_id,))
            cursor.execute("DELETE FROM simulation_results WHERE profile_id = ?", (profile_id,))
            
            # Then delete the profile
            cursor.execute("DELETE FROM financial_profiles WHERE id = ?", (profile_id,))
            conn.commit()
            
            conn.close()
            return True, "Profile deleted successfully"
        except sqlite3.Error as e:
            conn.close()
            return False, f"Database error: {e}"
    
    def save_analysis_results(self, profile_id, analysis_data):
        """
        Save analysis results for a financial profile.
        
        Args:
            profile_id (str): ID of the profile
            analysis_data (dict): Analysis results
            
        Returns:
            tuple: (success, message, analysis_id)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Check if the profile exists
        cursor.execute("SELECT id FROM financial_profiles WHERE id = ?", (profile_id,))
        if not cursor.fetchone():
            conn.close()
            return False, "Profile not found", None
        
        # Convert analysis data to JSON
        analysis_json = json.dumps(analysis_data)
        
        # Generate a unique ID
        analysis_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        
        try:
            # First delete any existing analysis for this profile
            cursor.execute("DELETE FROM analysis_results WHERE profile_id = ?", (profile_id,))
            
            # Insert new analysis
            cursor.execute(
                "INSERT INTO analysis_results (id, profile_id, analysis_data, created_at) VALUES (?, ?, ?, ?)",
                (analysis_id, profile_id, analysis_json, current_time)
            )
            
            conn.commit()
            conn.close()
            return True, "Analysis saved successfully", analysis_id
        except sqlite3.Error as e:
            conn.close()
            return False, f"Database error: {e}", None
    
    def get_analysis_results(self, profile_id):
        """
        Get analysis results for a financial profile.
        
        Args:
            profile_id (str): ID of the profile
            
        Returns:
            dict: Analysis data or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, analysis_data, created_at FROM analysis_results WHERE profile_id = ? ORDER BY created_at DESC LIMIT 1",
            (profile_id,)
        )
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        
        analysis_id, data_json, created = row
        analysis = {
            "id": analysis_id,
            "data": json.loads(data_json),
            "created_at": created
        }
        
        conn.close()
        return analysis
    
    def save_simulation_results(self, profile_id, simulation_data):
        """
        Save simulation results for a financial profile.
        
        Args:
            profile_id (str): ID of the profile
            simulation_data (dict): Simulation results
            
        Returns:
            tuple: (success, message, simulation_id)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Check if the profile exists
        cursor.execute("SELECT id FROM financial_profiles WHERE id = ?", (profile_id,))
        if not cursor.fetchone():
            conn.close()
            return False, "Profile not found", None
        
        # Convert simulation data to JSON
        simulation_json = json.dumps(simulation_data)
        
        # Generate a unique ID
        simulation_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        
        try:
            # First delete any existing simulation for this profile
            cursor.execute("DELETE FROM simulation_results WHERE profile_id = ?", (profile_id,))
            
            # Insert new simulation
            cursor.execute(
                "INSERT INTO simulation_results (id, profile_id, simulation_data, created_at) VALUES (?, ?, ?, ?)",
                (simulation_id, profile_id, simulation_json, current_time)
            )
            
            conn.commit()
            conn.close()
            return True, "Simulation saved successfully", simulation_id
        except sqlite3.Error as e:
            conn.close()
            return False, f"Database error: {e}", None
    
    def get_simulation_results(self, profile_id):
        """
        Get simulation results for a financial profile.
        
        Args:
            profile_id (str): ID of the profile
            
        Returns:
            dict: Simulation data or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, simulation_data, created_at FROM simulation_results WHERE profile_id = ? ORDER BY created_at DESC LIMIT 1",
            (profile_id,)
        )
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        
        simulation_id, data_json, created = row
        simulation = {
            "id": simulation_id,
            "data": json.loads(data_json),
            "created_at": created
        }
        
        conn.close()
        return simulation
    
    def save_achievement(self, user_id, achievement_type, achievement_data):
        """
        Save a user achievement.
        
        Args:
            user_id (str): ID of the user
            achievement_type (str): Type of achievement (e.g., "debt_free", "emergency_fund")
            achievement_data (dict): Achievement details
            
        Returns:
            tuple: (success, message, achievement_id)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Check if the user exists
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            conn.close()
            return False, "User not found", None
        
        # Check if the achievement already exists
        cursor.execute(
            "SELECT id FROM achievements WHERE user_id = ? AND achievement_type = ?",
            (user_id, achievement_type)
        )
        if cursor.fetchone():
            conn.close()
            return False, "Achievement already exists", None
        
        # Convert achievement data to JSON
        achievement_json = json.dumps(achievement_data)
        
        # Generate a unique ID
        achievement_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        
        try:
            # Insert the achievement
            cursor.execute(
                "INSERT INTO achievements (id, user_id, achievement_type, achievement_data, achieved_at) VALUES (?, ?, ?, ?, ?)",
                (achievement_id, user_id, achievement_type, achievement_json, current_time)
            )
            
            conn.commit()
            conn.close()
            return True, "Achievement saved successfully", achievement_id
        except sqlite3.Error as e:
            conn.close()
            return False, f"Database error: {e}", None
    
    def get_user_achievements(self, user_id):
        """
        Get all achievements for a user.
        
        Args:
            user_id (str): ID of the user
            
        Returns:
            list: List of achievement dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, achievement_type, achievement_data, achieved_at FROM achievements WHERE user_id = ? ORDER BY achieved_at DESC",
            (user_id,)
        )
        
        achievements = []
        for row in cursor.fetchall():
            achievement_id, achievement_type, data_json, achieved_at = row
            achievement = {
                "id": achievement_id,
                "type": achievement_type,
                "data": json.loads(data_json),
                "achieved_at": achieved_at
            }
            achievements.append(achievement)
        
        conn.close()
        return achievements