#!/usr/bin/env python3
"""
Job Database Cleanup Script for N8N
Removes duplicate jobs from database before dashboard generation
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.database_manager import JobDatabase
import json
import argparse

def cleanup_job_database(db_path=None, check_only=False):
    """Clean up job database duplicates"""
    
    try:
        # Initialize database
        print("[INFO] Initializing job database...")
        db = JobDatabase(db_path)
        
        if check_only:
            # Only show statistics, don't cleanup
            print("[CHECK] Checking for duplicates...")
            
            duplicate_stats = db.get_duplicate_stats()
            
            result = {
                'action': 'check_only',
                'success': True,
                'stats': duplicate_stats
            }
            
            print(f"[STATS] Duplicate Analysis:")
            print(f"   Total jobs: {duplicate_stats['total_jobs']}")
            print(f"   Title duplicate groups: {duplicate_stats['title_duplicate_groups']}")
            print(f"   Potential title duplicates: {duplicate_stats['title_duplicates_count']}")
            print(f"   URL duplicate groups: {duplicate_stats['url_duplicate_groups']}")
            print(f"   Potential URL duplicates: {duplicate_stats['url_duplicates_count']}")
            print(f"   Total potential duplicates: {duplicate_stats['total_potential_duplicates']}")
            
            return result
        
        else:
            # Perform actual cleanup
            print("[CLEANUP] Starting job database cleanup...")
            
            # Get initial stats
            initial_count = db.get_jobs_count()
            duplicate_stats_before = db.get_duplicate_stats()
            
            print(f"[BEFORE] Before cleanup:")
            print(f"   Total jobs: {initial_count}")
            print(f"   Potential duplicates: {duplicate_stats_before['total_potential_duplicates']}")
            
            # Remove job duplicates
            print("\n[PROCESS] Removing duplicate jobs...")
            job_cleanup_stats = db.remove_duplicate_jobs()
            
            # Clean old scraped data
            print("\n[PROCESS] Cleaning old scraped data...")
            scraped_cleanup_stats = db.cleanup_old_scraped_data(keep_latest=50)
            
            # Get final stats
            final_count = db.get_jobs_count()
            duplicate_stats_after = db.get_duplicate_stats()
            
            result = {
                'action': 'cleanup',
                'success': True,
                'before': {
                    'total_jobs': initial_count,
                    'potential_duplicates': duplicate_stats_before['total_potential_duplicates']
                },
                'after': {
                    'total_jobs': final_count,
                    'potential_duplicates': duplicate_stats_after['total_potential_duplicates']
                },
                'removed': {
                    'jobs_by_title': job_cleanup_stats['title_duplicates_removed'],
                    'jobs_by_url': job_cleanup_stats['url_duplicates_removed'],
                    'total_jobs': job_cleanup_stats['title_duplicates_removed'] + job_cleanup_stats['url_duplicates_removed'],
                    'scraped_entries': scraped_cleanup_stats['scraped_removed'],
                    'orphaned_jobs': scraped_cleanup_stats['orphaned_jobs_removed']
                }
            }
            
            print(f"\n[SUCCESS] Cleanup completed successfully!")
            print(f"[SUMMARY] Summary:")
            print(f"   Jobs: {initial_count} -> {final_count}")
            print(f"   Removed: {result['removed']['total_jobs']} duplicate jobs")
            print(f"   Cleaned: {result['removed']['scraped_entries']} old scraped entries")
            print(f"   Orphaned: {result['removed']['orphaned_jobs']} orphaned jobs")
            
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
    parser = argparse.ArgumentParser(description='Cleanup job database duplicates')
    parser.add_argument('--db-path', help='Path to job database (optional)')
    parser.add_argument('--check-only', action='store_true', help='Only check for duplicates, do not remove')
    parser.add_argument('--output', help='Output file for results JSON')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Run cleanup
    result = cleanup_job_database(
        db_path=args.db_path,
        check_only=args.check_only
    )
    
    # Output results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"[OUTPUT] Results saved to: {args.output}")
    
    # Always output JSON for N8N to parse
    print("\n" + json.dumps(result, indent=2))
    
    # Exit code based on success
    sys.exit(0 if result['success'] else 1)

if __name__ == "__main__":
    main()