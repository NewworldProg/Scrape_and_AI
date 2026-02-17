#!/usr/bin/env python3
"""
Chat Database Cleanup Script for N8N
Removes duplicate chat sessions and merges messages
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.chat_database_manager import ChatDatabase
import json
import argparse

def cleanup_chat_database(db_path=None, check_only=False):
    """Clean up chat database duplicates and old sessions"""
    
    try:
        # If no db_path provided, use default chat database location
        if db_path is None:
            db_path = os.path.join("data", "chat_data.db")
        
        print(f"[DEBUG] Starting cleanup_chat_database with db_path={db_path}, check_only={check_only}")
        print("[INFO] Initializing chat database...")
        
        # Check if database exists
        if not os.path.exists(db_path):
            print(f"[WARNING] Database not found at {db_path}, creating new one")
        
        db = ChatDatabase(db_path)
        
        if check_only:
            print("[INFO] Checking for duplicates...")
            
            duplicate_stats = db.get_duplicate_chat_stats()
            
            result = {
                'action': 'check_only',
                'success': True,
                'stats': duplicate_stats
            }
            
            print(f"[INFO] Duplicate Analysis:")
            print(f"   Total sessions: {duplicate_stats['total_sessions']}")
            print(f"   Duplicate groups: {duplicate_stats['duplicate_groups']}")
            print(f"   Potential duplicates: {duplicate_stats['potential_duplicates']}")
            print(f"   Total messages: {duplicate_stats['total_messages']}")
            
            return result
        
        else:
            print("[INFO] Starting chat database cleanup...")
            
            # Get initial stats
            initial_sessions = db.get_chat_sessions_count()
            duplicate_stats_before = db.get_duplicate_chat_stats()
            
            print(f"[INFO] Before cleanup:")
            print(f"   Total sessions: {initial_sessions}")
            print(f"   Potential duplicates: {duplicate_stats_before['potential_duplicates']}")
            
            # Remove duplicate chat sessions
            print("\n[INFO] Removing duplicate chat sessions...")
            chat_cleanup_stats = db.cleanup_duplicate_chat_sessions()
            
            # Get final stats
            final_sessions = db.get_chat_sessions_count()
            duplicate_stats_after = db.get_duplicate_chat_stats()
            
            result = {
                'action': 'cleanup',
                'success': True,
                'before': {
                    'total_sessions': initial_sessions,
                    'potential_duplicates': duplicate_stats_before['potential_duplicates']
                },
                'after': {
                    'total_sessions': final_sessions,
                    'potential_duplicates': duplicate_stats_after['potential_duplicates']
                },
                'removed': {
                    'duplicate_sessions': chat_cleanup_stats['sessions_removed'],
                    'total_sessions': chat_cleanup_stats['sessions_removed'],
                    'messages_merged': chat_cleanup_stats['messages_merged'],
                    'duplicate_messages_skipped': chat_cleanup_stats['duplicate_messages_skipped']
                }
            }
            
            print(f"\n[SUCCESS] Chat cleanup completed!")
            print(f"[INFO] Summary:")
            try:
                print(f"   Sessions: {initial_sessions} -> {final_sessions}")
                print(f"   Removed duplicates: {result['removed']['duplicate_sessions']}")
                print(f"   Messages merged: {result['removed']['messages_merged']}")
                print(f"   Duplicate messages skipped: {result['removed']['duplicate_messages_skipped']}")
            except UnicodeEncodeError:
                # Handle Windows encoding issues
                print(f"   Sessions: {initial_sessions} to {final_sessions}")
                print(f"   Removed duplicates: {result['removed']['duplicate_sessions']}")
                print(f"   Messages merged: {result['removed']['messages_merged']}")
                print(f"   Duplicate messages skipped: {result['removed']['duplicate_messages_skipped']}")
            
            return result
        
    except Exception as e:
        error_result = {
            'action': 'cleanup' if not check_only else 'check_only',
            'success': False,
            'error': str(e)
        }
        
        print(f"[ERROR] Error during cleanup: {e}")
        return error_result

def main():
    print("[DEBUG] Cleanup script started - this is cleanup_chat_database.py")
    print(f"[DEBUG] Current working directory: {os.getcwd()}")
    print(f"[DEBUG] Script path: {__file__}")
    
    parser = argparse.ArgumentParser(description='Cleanup chat database duplicates')
    parser.add_argument('--db-path', help='Path to chat database (optional)')
    parser.add_argument('--check-only', action='store_true', help='Only check for duplicates, do not remove')
    parser.add_argument('--output', help='Output file for results JSON')
    
    args = parser.parse_args()
    
    print(f"[DEBUG] Arguments: db_path={args.db_path}, check_only={args.check_only}, output={args.output}")
    
    result = cleanup_chat_database(
        db_path=args.db_path,
        check_only=args.check_only
    )
    
    # Output results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"[INFO] Results saved to: {args.output}")
    
    # Always output JSON for N8N
    print("\n" + json.dumps(result, indent=2))
    
    # Exit code based on success
    sys.exit(0 if result['success'] else 1)

if __name__ == "__main__":
    main()