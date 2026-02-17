# 🗂️ Database Cleanup Workflow

**File**: `n8n_database_cleanup_workflow.json`  
**Purpose**: Automated database maintenance and optimization  
**Trigger**: can be triggered manualy or scheduled     

---

## 🎯 How It Works

This workflow performs regular maintenance tasks to keep databases optimized and remove unnecessary data.

### 🔄 Workflow Steps

```
Manual Trigger or Daily Schedule
  ↓
Check Database Sizes
  ↓
Remove Duplicate Entries
  ↓
Clean Old HTML Snapshots
  ↓
Remove Expired Chat Sessions
  ↓
Optimize Database Indexes
  ↓
Update Statistics Dashboard
```

### 📁 Files Used

| File | Purpose |
|------|---------|
| `run_database_cleanup.ps1` | Main cleanup orchestrator |
| `run_check_database_health.ps1` | Database health assessment |
| `run_optimize_database.ps1` | Performance optimization |
| `run_remove_duplicates.ps1` | Duplicate record removal |
| `run_cleanup_old_data.ps1` | Remove expired data |

### 🗄️ Core Components

#### **Database Health Checker**
- **File**: `data/database_health_manager.py`
- **Function**: Analyzes database size, fragmentation, and performance
- **Output**: Health report with recommendations

#### **Duplicate Remover**
- **File**: `scripts/database_duplicate_cleaner.py`
- **Function**: Finds and removes duplicate job listings and chat messages
- **Method**: Hash-based comparison for efficient detection

#### **Data Archiver**
- **File**: `scripts/database_archiver.py`
- **Function**: Archives old data before deletion
- **Retention**: Configurable retention periods per data type

---

## 🧹 Cleanup Operations

### **1. Job Database Cleanup**
```sql
-- Remove duplicate jobs (same URL)
DELETE FROM jobs WHERE id NOT IN (
    SELECT MIN(id) FROM jobs GROUP BY url
);

-- Remove old HTML snapshots (>30 days)
DELETE FROM html_snapshots 
WHERE date(snapshot_date) < date('now', '-30 days');

-- Update job statistics
UPDATE jobs SET has_cover_letter = 1 
WHERE id IN (SELECT job_id FROM cover_letters);
```

### **2. Chat Database Cleanup**
```sql
-- Remove incomplete chat sessions
DELETE FROM chat_sessions 
WHERE total_messages < 3 
AND date(session_start) < date('now', '-7 days');

-- Clean orphaned chat messages
DELETE FROM chat_messages 
WHERE session_id NOT IN (SELECT id FROM chat_sessions);

-- Update session statistics
UPDATE chat_sessions SET total_messages = (
    SELECT COUNT(*) FROM chat_messages 
    WHERE session_id = chat_sessions.id
);
```

### **3. File System Cleanup**
```powershell
# Remove temporary files
Remove-Item "temp_*.json" -Force

# Clean Chrome profile cache
Remove-Item "chrome_profile*/Default/Cache/*" -Recurse -Force

# Archive old log files
Compress-Archive -Path "logs/*.log" -DestinationPath "logs/archive.zip"
```

---

## ⚙️ Configuration Options

### **Retention Periods**
```python
# In database_cleanup_config.py
RETENTION_DAYS = {
    'html_snapshots': 30,        # Keep HTML for 1 month
    'incomplete_sessions': 7,    # Remove incomplete chats after 1 week
    'old_jobs': 90,             # Archive jobs after 3 months
    'log_files': 14,            # Keep logs for 2 weeks
    'temp_files': 1             # Clean temp files daily
}
```

### **Cleanup Thresholds**
```python
DATABASE_SIZE_LIMITS = {
    'upwork_data.db': '500MB',   # Job database limit
    'chat_data.db': '100MB',     # Chat database limit
    'max_html_snapshots': 1000   # Maximum HTML records
}
```

### **Performance Optimization**
```python
OPTIMIZATION_SETTINGS = {
    'vacuum_threshold': 0.3,     # Run VACUUM if 30% fragmented
    'reindex_frequency': 'weekly', # Rebuild indexes weekly
    'analyze_after_cleanup': True # Update statistics after cleanup
}
```

---

## 📊 Database Health Monitoring

### **Health Check Reports**
The system generates detailed health reports:

```
📊 Database Health Report - 2025-11-18
===========================================
🗄️ Job Database (upwork_data.db):
   Size: 45.2 MB / 500 MB limit (9% used)
   Jobs: 1,247 total, 156 with cover letters
   HTML Snapshots: 87 (oldest: 15 days ago)
   Fragmentation: 12% (Good)
   
🤖 Chat Database (chat_data.db):
   Size: 8.7 MB / 100 MB limit (8% used)  
   Sessions: 234 total, 12 active
   Messages: 3,891 total
   Fragmentation: 5% (Excellent)

🚨 Recommendations:
   ✅ No action required - databases healthy
   💡 Consider archiving HTML snapshots older than 30 days
```

### **Performance Metrics**
```python
# Database performance tracking
METRICS_TRACKED = [
    'query_response_time',      # Average query speed
    'database_size_growth',     # Size increase over time
    'fragmentation_level',      # Disk fragmentation percentage
    'index_efficiency',         # Index usage statistics
    'backup_success_rate'       # Backup operation success
]
```

---

## 🛠️ Maintenance Schedules

### **Daily Operations**
- Clean temporary files
- Remove failed chat sessions from last 24 hours
- Check database size limits
- Generate health summary

### **Weekly Operations**
- Remove duplicate job entries
- Clean old HTML snapshots (>30 days)
- Optimize database indexes (REINDEX)
- Update database statistics (ANALYZE)

### **Monthly Operations**
- Archive old job data (>90 days)
- Full database vacuum and optimize
- Backup database files
- Generate detailed performance reports

### **On-Demand Operations**
- Emergency cleanup for disk space
- Manual duplicate removal
- Database corruption repair
- Performance troubleshooting

---

## 📁 Backup and Recovery

### **Automated Backups**
```powershell
# Daily database backups
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item "upwork_data.db" "backups/upwork_data_$timestamp.db"
Copy-Item "chat_data.db" "backups/chat_data_$timestamp.db"

# Keep last 7 days of backups
Get-ChildItem "backups/*.db" | 
    Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-7)} |
    Remove-Item
```

### **Recovery Procedures**
```powershell
# Restore from backup
$backupFile = "backups/upwork_data_20251117_143022.db"
Copy-Item $backupFile "upwork_data.db" -Force

# Verify database integrity
sqlite3 upwork_data.db "PRAGMA integrity_check;"
```

---

## 🚨 Error Handling

### **Common Issues and Solutions**

#### **Database Locked Error**
```powershell
# Check for active connections
netstat -an | findstr :5432
tasklist | findstr sqlite

# Force close connections
taskkill /F /IM sqlite3.exe
```

#### **Disk Space Issues**
```powershell
# Emergency cleanup script
Remove-Item "chrome_profile*/Default/Cache/*" -Recurse -Force
Remove-Item "temp_*" -Force  
Remove-Item "logs/*.log" -Force

# Compress large databases
sqlite3 upwork_data.db "VACUUM;"
```

#### **Corruption Detection**
```sql
-- Check database integrity
PRAGMA integrity_check;

-- Quick check
PRAGMA quick_check;

-- Repair if possible
.backup backup.db
.open backup.db
```

---

## 📈 Performance Benefits

### **Before Cleanup**
- Database queries slow (>1s for complex searches)
- Large file sizes (databases >100MB)
- Disk fragmentation causing performance issues
- Duplicate records wasting space

### **After Cleanup**
- Fast query response (<0.1s average)
- Optimized database sizes (30-50% reduction)
- Improved index efficiency
- Clean, deduplicated data

### **Storage Optimization**
```
📊 Cleanup Results Example:
================================
🗄️ Jobs Database:
   Before: 127.4 MB (3,500 records, 45% fragmentation)
   After:   45.2 MB (1,247 records, 12% fragmentation)
   Savings: 82.2 MB (64% reduction)

🤖 Chat Database:
   Before: 23.1 MB (8,900 messages, 30% fragmentation)  
   After:   8.7 MB (3,891 messages, 5% fragmentation)
   Savings: 14.4 MB (62% reduction)

💾 File System:
   Temp files removed: 156 MB
   Cache cleared: 89 MB
   Logs archived: 34 MB
   Total space freed: 362 MB
```

---

## 🔧 Advanced Configuration

### **Custom Cleanup Rules**
```python
# Create custom cleanup rules in database_cleanup_config.py
CUSTOM_RULES = {
    'remove_failed_jobs': {
        'table': 'jobs',
        'condition': "title = '' AND description = ''",
        'age_limit': 7  # days
    },
    'clean_test_sessions': {
        'table': 'chat_sessions', 
        'condition': "total_messages < 2",
        'age_limit': 1  # day
    }
}
```

### **Integration with Monitoring**
```python
# Send cleanup reports to monitoring system
def send_cleanup_report(results):
    report = {
        'timestamp': datetime.now(),
        'records_removed': results['deleted_count'],
        'space_freed': results['space_saved'],
        'performance_improvement': results['speed_gain']
    }
    # Send to monitoring dashboard
```