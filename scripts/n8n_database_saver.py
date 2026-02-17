#!/usr/bin/env python
"""
n8n Database Saver for Cover Letters
===================================
Saves AI-generated cover letters directly to the database
"""

import sys
import json
import argparse
from pathlib import Path

# Add parent directory to path to import the database manager
sys.path.append(str(Path(__file__).parent.parent))

from data.database_manager import JobDatabase

def save_cover_letter_to_db(job_id: int, ai_provider: str, cover_letter_text: str, notes: str = None):
    """Save cover letter to database and return result"""
    try:
        db = JobDatabase()
        cover_letter_id = db.add_cover_letter(
            job_id=job_id,
            ai_provider=ai_provider,
            cover_letter_text=cover_letter_text,
            notes=notes
        )
        
        return {
            "success": True,
            "cover_letter_id": cover_letter_id,
            "job_id": job_id,
            "ai_provider": ai_provider,
            "message": f"Cover letter saved to database with ID {cover_letter_id}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "job_id": job_id,
            "ai_provider": ai_provider
        }

def get_recent_jobs_with_covers(limit: int = 20):
    """Get recent jobs and their cover letters for reporting"""
    try:
        db = JobDatabase()
        
        # Custom query to get jobs with their cover letters
        import sqlite3
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT j.id, j.job_title, j.job_url, j.parsed_timestamp,
                   COUNT(c.id) as cover_letter_count,
                   GROUP_CONCAT(c.ai_provider) as ai_providers,
                   MAX(c.generated_timestamp) as latest_cover_letter
            FROM jobs j
            LEFT JOIN cover_letters c ON j.id = c.job_id
            GROUP BY j.id
            ORDER BY j.parsed_timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        jobs = []
        for row in cursor.fetchall():
            jobs.append({
                'job_id': row[0],
                'job_title': row[1],
                'job_url': row[2],
                'parsed_timestamp': row[3],
                'cover_letter_count': row[4],
                'ai_providers': row[5].split(',') if row[5] else [],
                'latest_cover_letter': row[6]
            })
        
        conn.close()
        
        return {
            "success": True,
            "jobs": jobs,
            "total_jobs": len(jobs),
            "jobs_with_covers": len([j for j in jobs if j['cover_letter_count'] > 0])
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def main():
    parser = argparse.ArgumentParser(description='Save cover letters to database')
    parser.add_argument('--action', choices=['save', 'report'], required=True,
                       help='Action to perform')
    parser.add_argument('--job_id', type=int, help='Job ID for cover letter')
    parser.add_argument('--ai_provider', type=str, help='AI provider used')
    parser.add_argument('--cover_letter', type=str, help='Cover letter text')
    parser.add_argument('--notes', type=str, help='Additional notes')
    parser.add_argument('--limit', type=int, default=20, help='Limit for report')
    parser.add_argument('--output_format', choices=['json', 'text'], default='json',
                       help='Output format')
    
    args = parser.parse_args()
    
    if args.action == 'save':
        if not all([args.job_id, args.ai_provider, args.cover_letter]):
            result = {
                "success": False,
                "error": "Missing required arguments: job_id, ai_provider, cover_letter"
            }
        else:
            result = save_cover_letter_to_db(
                job_id=args.job_id,
                ai_provider=args.ai_provider,
                cover_letter_text=args.cover_letter,
                notes=args.notes
            )
    
    elif args.action == 'report':
        result = get_recent_jobs_with_covers(args.limit)
    
    # Output result
    if args.output_format == 'json':
        print(json.dumps(result, indent=2))
    else:
        if result['success']:
            if args.action == 'save':
                print(f"✅ {result['message']}")
            else:
                jobs = result['jobs']
                print(f"📊 Database Report: {result['total_jobs']} jobs, {result['jobs_with_covers']} have cover letters")
                for job in jobs[:5]:  # Show first 5
                    print(f"  📝 {job['job_title']} ({job['cover_letter_count']} covers)")
        else:
            print(f"❌ Error: {result['error']}")

if __name__ == "__main__":
    main()