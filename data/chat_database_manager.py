"""
Chat Database Manager for Chat AI Assistant
Manages chat sessions, messages, and AI responses
"""
import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class ChatDatabase:
    def __init__(self, db_path: str = "chat_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize chat database with tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Chat sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE,
                chat_platform TEXT,
                chat_title TEXT,
                participant_name TEXT,
                chat_url TEXT,
                started_at DATETIME,
                last_activity DATETIME,
                total_messages INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active',
                phase TEXT,
                phase_confidence REAL,
                phase_updated_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Chat messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                message_id TEXT UNIQUE,
                sender TEXT,
                sender_type TEXT,
                message_text TEXT,
                timestamp DATETIME,
                message_order INTEGER,
                scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES chat_sessions (session_id)
            )
        ''')
        
        # Raw chat HTML data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS raw_chat_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                html_content TEXT,
                page_url TEXT,
                scrape_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                content_length INTEGER,
                FOREIGN KEY (session_id) REFERENCES chat_sessions (session_id)
            )
        ''')
        
        # GPT-2 AI responses
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gpt2_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                context_messages TEXT,
                generated_response TEXT,
                response_type TEXT,
                confidence_score REAL,
                model_version TEXT,
                generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                used BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (session_id) REFERENCES chat_sessions (session_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("[OK] Chat database initialized")
    
    def save_raw_chat_html(self, session_id: str, html_content: str, page_url: str) -> int:
        """Save raw chat HTML"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO raw_chat_data (session_id, html_content, page_url, content_length)
            VALUES (?, ?, ?, ?)
        ''', (session_id, html_content, page_url, len(html_content)))
        
        raw_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return raw_id
    
    def save_chat_session(self, session_data: Dict) -> str:
        """Save or update chat session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO chat_sessions 
            (session_id, chat_platform, chat_title, participant_name, chat_url,
             started_at, last_activity, total_messages, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_data['session_id'],
            session_data.get('platform', 'unknown'),
            session_data.get('title', 'Unknown Chat'),
            session_data.get('participant', 'Unknown'),
            session_data.get('url', ''),
            session_data.get('started_at', datetime.now()),
            datetime.now(),
            session_data.get('total_messages', 0),
            'active'
        ))
        
        conn.commit()
        conn.close()
        
        return session_data['session_id']
    
    def save_chat_messages(self, session_id: str, messages: List[Dict]) -> int:
        """Save chat messages"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        saved_count = 0
        for msg in messages:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO chat_messages 
                    (session_id, message_id, sender, sender_type, message_text, 
                     timestamp, message_order)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    session_id,
                    msg['message_id'],
                    msg['sender'],
                    msg['sender_type'],
                    msg['text'],
                    msg['timestamp'],
                    msg['order']
                ))
                if cursor.rowcount > 0:
                    saved_count += 1
            except Exception as e:
                print(f"⚠️ Error saving message: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        return saved_count
    
    def get_latest_messages(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Get latest messages from chat"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT sender, sender_type, message_text, timestamp, message_order
            FROM chat_messages 
            WHERE session_id = ?
            ORDER BY message_order DESC
            LIMIT ?
        ''', (session_id, limit))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                'sender': row[0],
                'sender_type': row[1],
                'text': row[2],
                'timestamp': row[3],
                'order': row[4]
            })
        
        conn.close()
        return messages
    
    def get_latest_session(self) -> Optional[Dict]:
        """Get most recent active session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT session_id, chat_platform, chat_title, participant_name, 
                   last_activity, total_messages, chat_url
            FROM chat_sessions 
            WHERE status = 'active'
            ORDER BY last_activity DESC 
            LIMIT 1
        ''')
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'session_id': row[0],
                'platform': row[1],
                'title': row[2],
                'participant': row[3],
                'last_activity': row[4],
                'total_messages': row[5],
                'url': row[6]
            }
        return None
    
    def get_recent_messages(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Get recent messages for a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT message_text, sender, timestamp, sender_type
            FROM chat_messages 
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (session_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        messages = []
        for row in rows:
            messages.append({
                'text': row[0],
                'sender': row[1],
                'timestamp': row[2],
                'sender_type': row[3]
            })
        
        return list(reversed(messages))  # Return in chronological order
    
    def save_gpt2_response(self, session_id: str, response_data: Dict) -> int:
        """Save GPT-2 generated response"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO gpt2_responses 
            (session_id, context_messages, generated_response, response_type,
             confidence_score, model_version)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            json.dumps(response_data.get('context', [])),
            response_data['response'],
            response_data.get('type', 'general'),
            response_data.get('confidence', 0.7),
            response_data.get('model_version', 'gpt2-chat-v1')
        ))
        
        response_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return response_id
    
    def get_dashboard_data(self) -> Dict:
        """Get data for chat dashboard"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Active sessions
        cursor.execute('''
            SELECT cs.session_id, cs.chat_platform, cs.chat_title, 
                   cs.participant_name, cs.last_activity, cs.total_messages,
                   COUNT(cm.id) as recent_messages
            FROM chat_sessions cs
            LEFT JOIN chat_messages cm ON cs.session_id = cm.session_id
                AND cm.scraped_at > datetime('now', '-1 hour')
            WHERE cs.status = 'active'
            GROUP BY cs.session_id
            ORDER BY cs.last_activity DESC
            LIMIT 5
        ''')
        
        active_sessions = [
            {
                'session_id': row[0],
                'platform': row[1],
                'title': row[2],
                'participant': row[3],
                'last_activity': row[4],
                'total_messages': row[5],
                'recent_messages': row[6]
            }
            for row in cursor.fetchall()
        ]
        
        # Recent GPT-2 responses
        cursor.execute('''
            SELECT session_id, generated_response, response_type, 
                   confidence_score, model_version, generated_at, used
            FROM gpt2_responses
            ORDER BY generated_at DESC
            LIMIT 10
        ''')
        
        recent_responses = [
            {
                'session_id': row[0],
                'response': row[1][:150] + '...' if len(row[1]) > 150 else row[1],
                'type': row[2],
                'confidence': row[3],
                'model_version': row[4],
                'generated_at': row[5],
                'used': row[6]
            }
            for row in cursor.fetchall()
        ]
        
        # Statistics
        cursor.execute('SELECT COUNT(*) FROM chat_sessions WHERE status = "active"')
        total_sessions = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM chat_messages')
        total_messages = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM gpt2_responses')
        total_ai_responses = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM gpt2_responses WHERE used = 1')
        used_responses = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'active_sessions': active_sessions,
            'recent_responses': recent_responses,
            'stats': {
                'total_sessions': total_sessions,
                'total_messages': total_messages,
                'total_ai_responses': total_ai_responses,
                'used_responses': used_responses
            }
        }
    
    def update_session_phase(self, session_id: str, phase: str, confidence: float) -> bool:
        """Update session with detected phase"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE chat_sessions 
                SET phase = ?, phase_confidence = ?, phase_updated_at = ?
                WHERE session_id = ?
            ''', (phase, confidence, datetime.now(), session_id))
            
            rows_affected = cursor.rowcount
            conn.commit()
            conn.close()
            
            if rows_affected > 0:
                print(f"[DB] Updated session {session_id} with phase: {phase} ({confidence:.1%})")
                return True
            else:
                print(f"[DB WARN] Session {session_id} not found for phase update")
                return False
                
        except Exception as e:
            print(f"[DB ERROR] Failed to update phase: {e}")
            return False
    
    def get_session_with_phase(self, session_id: str) -> Optional[Dict]:
        """Get session including detected phase"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT session_id, chat_platform, chat_title, participant_name,
                   last_activity, total_messages, phase, phase_confidence, phase_updated_at
            FROM chat_sessions 
            WHERE session_id = ?
        ''', (session_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'session_id': row[0],
                'platform': row[1],
                'title': row[2],
                'participant': row[3],
                'last_activity': row[4],
                'total_messages': row[5],
                'phase': row[6],
                'phase_confidence': row[7],
                'phase_updated_at': row[8]
            }
        return None

    # ======================== 🧹 CHAT CLEANUP FUNCTIONS ========================
    
    def find_duplicate_chat_sessions(self) -> List[Dict]:
        """Find duplicate chat sessions by platform, title, and participant"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT chat_platform, chat_title, participant_name, 
                   COUNT(*) as session_count,
                   GROUP_CONCAT(session_id ORDER BY total_messages DESC, last_activity DESC) as session_ids,
                   GROUP_CONCAT(total_messages ORDER BY total_messages DESC, last_activity DESC) as message_counts
            FROM chat_sessions 
            WHERE chat_platform IS NOT NULL AND participant_name IS NOT NULL
            GROUP BY chat_platform, chat_title, participant_name
            HAVING COUNT(*) > 1
            ORDER BY COUNT(*) DESC
        ''')
        
        duplicates = []
        for row in cursor.fetchall():
            platform, title, participant, count, ids_str, counts_str = row
            session_ids = ids_str.split(',')
            message_counts = [int(c) for c in counts_str.split(',')]
            
            duplicates.append({
                'platform': platform,
                'title': title,
                'participant': participant,
                'duplicate_count': count,
                'session_ids': session_ids,
                'message_counts': message_counts,
                'keep_session': session_ids[0],  # First one has most messages
                'remove_sessions': session_ids[1:]
            })
        
        conn.close()
        return duplicates

    def cleanup_duplicate_chat_sessions(self) -> Dict:
        """Remove duplicate chat sessions, merge messages into session with most content"""
        print("[CLEANUP] Starting chat session cleanup...")
        
        # Find all duplicate groups
        duplicate_groups = self.find_duplicate_chat_sessions()
        
        if not duplicate_groups:
            print("[CLEANUP] No duplicate chat sessions found")
            return {
                'duplicate_groups_found': 0,
                'sessions_removed': 0,
                'messages_merged': 0,
                'duplicate_messages_skipped': 0,
                'success': True
            }
        
        print(f"[CLEANUP] Found {len(duplicate_groups)} duplicate groups")
        
        total_stats = {
            'duplicate_groups_found': len(duplicate_groups),
            'sessions_removed': 0,
            'messages_merged': 0,
            'duplicate_messages_skipped': 0,
            'groups_processed': 0
        }
        
        # Process each duplicate group
        for group in duplicate_groups:
            print(f"\n[CLEANUP] Processing duplicate group:")
            print(f"   Platform: {group['platform']}")
            print(f"   Participant: {group['participant']}")
            print(f"   Sessions: {group['duplicate_count']}")
            print(f"   Keep: {group['keep_session']} ({group['message_counts'][0]} messages)")
            print(f"   Remove: {group['remove_sessions']}")
            
            try:
                merge_stats = self.merge_chat_sessions(
                    group['keep_session'],
                    group['remove_sessions']
                )
                
                total_stats['sessions_removed'] += merge_stats['sessions_removed']
                total_stats['messages_merged'] += merge_stats['messages_merged']
                total_stats['duplicate_messages_skipped'] += merge_stats['duplicate_messages_skipped']
                total_stats['groups_processed'] += 1
                
            except Exception as e:
                print(f"[ERROR] Failed to merge group: {e}")
                continue
        
        total_stats['success'] = True
        
        print(f"\n[SUCCESS] Chat cleanup completed:")
        print(f"   Duplicate groups processed: {total_stats['groups_processed']}")
        print(f"   Sessions removed: {total_stats['sessions_removed']}")
        print(f"   Messages merged: {total_stats['messages_merged']}")
        print(f"   Duplicate messages skipped: {total_stats['duplicate_messages_skipped']}")
        
        return total_stats

    def merge_chat_sessions(self, keep_session_id: str, remove_session_ids: List[str]) -> Dict:
        """Merge multiple chat sessions into one, keeping all unique messages"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {
            'messages_merged': 0,
            'duplicate_messages_skipped': 0,
            'sessions_removed': 0,
            'total_messages_before': 0,
            'total_messages_after': 0
        }
        
        print(f"[MERGE] Merging sessions into {keep_session_id}")
        print(f"[MERGE] Removing sessions: {remove_session_ids}")
        
        # Get current max order in keep session
        cursor.execute('''
            SELECT COALESCE(MAX(message_order), 0), COUNT(*) 
            FROM chat_messages 
            WHERE session_id = ?
        ''', (keep_session_id,))
        max_order, current_messages = cursor.fetchone()
        stats['total_messages_before'] = current_messages
        
        # Process each session to remove
        for remove_session_id in remove_session_ids:
            print(f"[MERGE] Processing session: {remove_session_id}")
            
            # Get all messages from session to remove
            cursor.execute('''
                SELECT message_id, sender, sender_type, message_text, timestamp, message_order, scraped_at
                FROM chat_messages 
                WHERE session_id = ?
                ORDER BY message_order ASC
            ''', (remove_session_id,))
            
            messages_to_merge = cursor.fetchall()
            
            for msg in messages_to_merge:
                message_id, sender, sender_type, text, timestamp, order, scraped_at = msg
                
                # Check if similar message already exists in keep session
                cursor.execute('''
                    SELECT id FROM chat_messages 
                    WHERE session_id = ? AND sender = ? AND message_text = ?
                    LIMIT 1
                ''', (keep_session_id, sender, text))
                
                if cursor.fetchone():
                    stats['duplicate_messages_skipped'] += 1
                    print(f"[SKIP] Duplicate message from {sender}: {text[:30]}...")
                    continue
                
                # Add unique message to keep session
                max_order += 1
                try:
                    cursor.execute('''
                        INSERT INTO chat_messages 
                        (session_id, message_id, sender, sender_type, message_text, 
                         timestamp, message_order, scraped_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        keep_session_id,
                        f"{keep_session_id}_{max_order}",  # New message ID
                        sender,
                        sender_type,
                        text,
                        timestamp,
                        max_order,
                        scraped_at
                    ))
                    stats['messages_merged'] += 1
                    print(f"[MERGE] Added message from {sender}: {text[:50]}...")
                    
                except Exception as e:
                    print(f"[ERROR] Failed to merge message: {e}")
                    continue
            
            # Delete old messages from remove session
            cursor.execute('DELETE FROM chat_messages WHERE session_id = ?', (remove_session_id,))
            
            # Delete old session
            cursor.execute('DELETE FROM chat_sessions WHERE session_id = ?', (remove_session_id,))
            stats['sessions_removed'] += 1
            
            print(f"[REMOVE] Deleted session: {remove_session_id}")
        
        # Update keep session metadata
        cursor.execute('''
            UPDATE chat_sessions 
            SET total_messages = (
                SELECT COUNT(*) FROM chat_messages WHERE session_id = ?
            ),
            last_activity = datetime('now')
            WHERE session_id = ?
        ''', (keep_session_id, keep_session_id))
        
        # Get final message count
        cursor.execute('''
            SELECT COUNT(*) FROM chat_messages WHERE session_id = ?
        ''', (keep_session_id,))
        stats['total_messages_after'] = cursor.fetchone()[0]
        
        conn.commit()
        conn.close()
        
        print(f"[SUCCESS] Session merge completed:")
        print(f"   Messages before: {stats['total_messages_before']}")
        print(f"   Messages after: {stats['total_messages_after']}")
        print(f"   Messages merged: {stats['messages_merged']}")
        print(f"   Duplicates skipped: {stats['duplicate_messages_skipped']}")
        print(f"   Sessions removed: {stats['sessions_removed']}")
        
        return stats

    def get_duplicate_chat_stats(self) -> Dict:
        """Get statistics about duplicate chat sessions without removing them"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Count total sessions
        cursor.execute('SELECT COUNT(*) FROM chat_sessions')
        total_sessions = cursor.fetchone()[0]
        
        # Count duplicate groups
        cursor.execute('''
            SELECT COUNT(*) FROM (
                SELECT chat_platform, chat_title, participant_name, COUNT(*) as count
                FROM chat_sessions 
                WHERE chat_platform IS NOT NULL AND participant_name IS NOT NULL
                GROUP BY chat_platform, chat_title, participant_name
                HAVING count > 1
            )
        ''')
        duplicate_groups = cursor.fetchone()[0]
        
        # Count total duplicate sessions
        cursor.execute('''
            SELECT SUM(count - 1) FROM (
                SELECT COUNT(*) as count
                FROM chat_sessions 
                WHERE chat_platform IS NOT NULL AND participant_name IS NOT NULL
                GROUP BY chat_platform, chat_title, participant_name
                HAVING count > 1
            )
        ''')
        duplicate_sessions_count = cursor.fetchone()[0] or 0
        
        # Count total messages
        cursor.execute('SELECT COUNT(*) FROM chat_messages')
        total_messages = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_sessions': total_sessions,
            'duplicate_groups': duplicate_groups,
            'duplicate_sessions_count': duplicate_sessions_count,
            'total_messages': total_messages,
            'potential_duplicates': duplicate_sessions_count
        }

    def get_chat_sessions_count(self) -> int:
        """Get total count of chat sessions in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM chat_sessions')
        count = cursor.fetchone()[0]
        conn.close()
        return count

if __name__ == "__main__":
    # Test database creation
    db = ChatDatabase()
    print("[OK] Chat database test completed!")