import os
import sys
import json
import re
import sqlite3
from datetime import datetime
from typing import List, Tuple
from bs4 import BeautifulSoup
from pathlib import Path
import argparse

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from data.database_manager import JobDatabase

# ======= 🧱 function to detect website type from HTML =======
def detect_website_type(soup, url_hint=None):
    """
    Detect what type of website was scraped based on HTML structure
    """
    html_text = str(soup).lower()
    
    # Check URL hint first (more reliable than content detection)
    if url_hint:
        if 'python.org' in url_hint.lower():
            return "python.org"
        elif 'upwork.com' in url_hint.lower():
            return "upwork"
    
    # Check for Python.org indicators
    python_indicators = [
        'python.org',
        'python job board',
        'python software foundation'
    ]
    
    if any(indicator in html_text for indicator in python_indicators):
        return "python.org"
    
    # Check for Upwork indicators (only if not Python.org)
    upwork_indicators = [
        'data-test="jobtile"',
        'data-qa="job-tile"',
        'job-tile-title'
    ]
    
    if any(indicator in html_text for indicator in upwork_indicators):
        return "upwork"
    
    # Default to generic parser
    return "generic"

# ======= 🧱 Generic parser for any job website =======
def parse_python_org_job(element, index):
    """Parse job element specific to Python.org format"""
    job_data = {}
    
    # Generate unique job_uid using timestamp and index
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    job_data['job_uid'] = f'python_org_{timestamp}_{index+1}'
    
    # Extract title from h2 a
    title_link = element.select_one('h2.listing-company a')
    if title_link:
        job_data['title'] = title_link.get_text(strip=True)
        job_data['url'] = f"https://python.org{title_link.get('href', '')}"
    else:
        job_data['title'] = f'Python Job {index+1}'
        job_data['url'] = f'#job_{index+1}'
    
    # Extract company - it's in the text after the <br> in .listing-company-name
    company_elem = element.select_one('.listing-company-name')
    if company_elem:
        # The company name is the text after <br>
        br_tag = company_elem.find('br')
        if br_tag and br_tag.next_sibling:
            company_text = br_tag.next_sibling.strip()
            if company_text:
                job_data['company'] = company_text
            else:
                job_data['company'] = 'Company not specified'
        else:
            job_data['company'] = 'Company not specified'
    else:
        job_data['company'] = 'Company not specified'
    
    # Extract location
    location_elem = element.select_one('.listing-location a')
    if location_elem:
        job_data['location'] = location_elem.get_text(strip=True)
    else:
        job_data['location'] = 'Location not specified'
    
    # Extract job type
    job_type_elem = element.select_one('.listing-job-type')
    if job_type_elem:
        job_data['skills'] = job_type_elem.get_text(strip=True).split(',')
    else:
        job_data['skills'] = []
    
    # Extract posted date
    date_elem = element.select_one('.listing-posted time')
    if date_elem:
        job_data['posted_time'] = date_elem.get_text(strip=True)
    else:
        job_data['posted_time'] = 'Date not specified'
    
    # Extract category
    category_elem = element.select_one('.listing-company-category a')
    if category_elem:
        job_data['category'] = category_elem.get_text(strip=True)
    else:
        job_data['category'] = 'Category not specified'
    
    # Create job_info structure compatible with database
    job_data['job_info'] = {
        'type': job_data.get('category', 'Developer / Engineer'),
        'budget': 'Not specified',
        'experience_level': 'Not specified',
        'duration': 'Not specified'
    }
    
    job_data['budget'] = 'Not specified'
    job_data['description'] = f"{job_data.get('category', '')}: {', '.join(job_data.get('skills', []))}"
    
    return job_data

def parse_generic_job_element(element, index, soup):
    """Parse generic job element for non-specific websites"""
    job_data = {}
    
    # Extract title (try various approaches)
    title = None
    
    # Try to find title in element text
    if hasattr(element, 'get_text'):
        title = element.get_text().strip()
    
    # Try to find title in nested headings
    if not title or len(title) > 200:  # Too long, probably not just a title
        heading = element.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if heading:
            title = heading.get_text().strip()
    
    # Try to find title in link text if element is a link
    if not title and element.name == 'a':
        title = element.get_text().strip()
    
    # Clean and validate title
    if title:
        title = re.sub(r'\s+', ' ', title)  # Clean whitespace
        if len(title) > 200:
            title = title[:200] + '...'
        job_data['title'] = title
    else:
        job_data['title'] = f'Job Listing {index+1}'
    
    # Extract URL
    if element.name == 'a' and element.get('href'):
        href = element.get('href')
        # Handle relative URLs
        if href.startswith('/'):
            # Try to get base URL from soup
            base_tag = soup.find('base')
            if base_tag and base_tag.get('href'):
                base_url = base_tag.get('href').rstrip('/')
            else:
                base_url = ''  # Will need to be fixed manually
            job_data['url'] = base_url + href
        else:
            job_data['url'] = href
    else:
        # Try to find a link within the element
        link = element.find('a', href=True)
        if link:
            href = link.get('href')
            if href.startswith('/'):
                job_data['url'] = href  # Relative URL
            else:
                job_data['url'] = href
        else:
            job_data['url'] = f'#job_{index+1}'
    
    # Extract description (try to get more context)
    description_parts = []
    
    # Get element text
    if hasattr(element, 'get_text'):
        element_text = element.get_text().strip()
        if element_text and element_text != title:
            description_parts.append(element_text)
    
    # Look for description in parent or sibling elements
    parent = element.parent
    if parent:
        siblings = element.find_next_siblings()[:3]  # Check next 3 siblings
        for sibling in siblings:
            if hasattr(sibling, 'get_text'):
                sibling_text = sibling.get_text().strip()
                if sibling_text and len(sibling_text) > 20:  # Meaningful text
                    description_parts.append(sibling_text)
    
    # Combine description parts
    description = ' | '.join(description_parts) if description_parts else 'No description available'
    if len(description) > 500:
        description = description[:500] + '...'
    
    job_data['description'] = description
    job_data['budget'] = 'Not specified'
    job_data['skills'] = []
    job_data['posted_time'] = datetime.now().strftime('%Y-%m-%d')
    
    # Create job_info structure compatible with database
    job_data['job_info'] = {
        'type': 'Generic',
        'budget': 'Not specified',
        'experience_level': 'Not specified',
        'duration': 'Not specified'
    }
    
    return job_data

def parse_generic_jobs(soup):
    """
    Generic job parser for non-Upwork websites
    Looks for common job listing patterns
    """
    jobs = []
    
    # Common job listing selectors to try
    job_selectors = [
        'ol.list-recent-jobs li',  # Python.org specific 
        '.job-listing',
        '.job-item', 
        '.job-post',
        '.position',
        'article.job',
        '.opening',
        '.vacancy',
        'li.job',
        '[class*="job"]',
        '[class*="position"]',
        '[class*="opening"]'
    ]
    
    job_elements = []
    selected_selector = None
    for selector in job_selectors:
        elements = soup.select(selector)
        if elements:
            job_elements = elements
            selected_selector = selector
            print(f'🎯 Found {len(elements)} job elements using selector: {selector}')
            break
    
    # Fallback: look for links that might be job postings
    if not job_elements:
        # Look for links containing job-related keywords
        all_links = soup.find_all('a', href=True)
        job_links = []
        job_keywords = ['job', 'position', 'career', 'opening', 'vacancy', 'work']
        
        for link in all_links:
            link_text = link.get_text().strip().lower()
            link_href = link.get('href', '').lower()
            
            # Check if link text or href contains job keywords
            if any(keyword in link_text or keyword in link_href for keyword in job_keywords):
                # Avoid navigation links, filters, etc.
                if not any(avoid in link_text for avoid in ['filter', 'search', 'sort', 'page', 'next', 'prev']):
                    job_links.append(link)
        
        job_elements = job_links[:20]  # Limit to 20 to avoid too many results
        print(f'🔍 Found {len(job_elements)} potential job links as fallback')
    
    # Parse each job element
    for i, element in enumerate(job_elements):
        job_data = {
            'job_uid': f'generic_{i+1}',
            'source_type': 'generic'
        }
        
        # Special parsing for Python.org
        if selected_selector == 'ol.list-recent-jobs li':
            job_data.update(parse_python_org_job(element, i))
        else:
            job_data.update(parse_generic_job_element(element, i, soup))
        
        jobs.append(job_data)
    
    print(f'✅ Extracted {len(jobs)} generic job listings')
    return jobs

# ======= 🧱 Main parsing function with auto-detection =======
def parse_jobs_from_html(html_content, url_hint=None):
    """
    Parse jobs from HTML with automatic website type detection
    """
    try:
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Detect website type
        website_type = detect_website_type(soup, url_hint)
        print(f'🌐 Detected website type: {website_type}')
        
        # Debug: Print title to see what we're parsing
        title = soup.title.get_text(strip=True) if soup.title else ''
        print(f'🏷️  Page title: {title}')
        
        # Use appropriate parser
        if website_type == "upwork":
            jobs = parse_upwork_jobs(soup)
            source_type = "upwork"
        elif website_type == "python.org":
            jobs = parse_python_org_jobs(soup)
            source_type = "python.org"
        else:
            jobs = parse_generic_jobs(soup)
            source_type = "generic"
        
        return {
            'success': True,
            'jobs': jobs,
            'jobs_count': len(jobs),
            'website_type': website_type,
            'source_type': source_type,
            'parsed_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'jobs': [],
            'jobs_count': 0
        }

def parse_python_org_jobs(soup):
    """
    Parse jobs from Python.org job board
    """
    jobs = []
    
    # Python.org uses ol.list-recent-jobs li structure
    job_elements = soup.select('ol.list-recent-jobs li')
    print(f'🎯 Found {len(job_elements)} job elements using selector: ol.list-recent-jobs li')
    
    for index, job_element in enumerate(job_elements):
        try:
            job_data = parse_python_org_job(job_element, index)
            if job_data:
                jobs.append(job_data)
        except Exception as e:
            print(f'⚠️  Error parsing job {index+1}: {str(e)}')
            continue
    
    print(f'✅ Extracted {len(jobs)} Python.org job listings')
    return jobs

def parse_upwork_jobs(soup):
    """
    Parse jobs from BeautifulSoup object (optimized - no HTML parsing here)
    """
    # array to hold job data
    jobs = []
    
    # inside job elements append jobs that are based on JobTile article tags
    # Try multiple selectors for different Upwork versions
    job_elements = soup.select('article[data-test="JobTile"]')
    if not job_elements:
        # Try newer format
        job_elements = soup.select('section[data-qa="job-tile"]')
    if not job_elements:
        # Try alternative selectors
        job_elements = soup.select('[data-qa="job-tile"]')
    
    # print number of job elements found
    print(f'🔍 Found {len(job_elements)} job elements')
    
    # loop through each job element and extract data
    for job_element in job_elements:
        # data dictionary for each job
        job_data = {}
        
        # Extract job UID
        # ===================================== Extract job UID ===========================
        job_uid = job_element.get('data-ev-job-uid', '')
        if job_uid:
            job_data['job_uid'] = job_uid

        # ========================== Extract job title and URL ==============================
        title_link = job_element.select_one('h2.job-tile-title a[data-test="job-tile-title-link"]')
        if not title_link:
            # Try alternative selectors for newer version
            title_link = job_element.select_one('h2 a[data-qa="job-title"]')
        if not title_link:
            # Try more generic selectors
            title_link = job_element.select_one('h2 a')
            if not title_link:
                title_link = job_element.select_one('a[data-test="job-tile-title-link"]')
                if not title_link:
                    title_link = job_element.select_one('a[data-qa="job-title"]')
        if title_link:
            job_data['title'] = title_link.get_text(strip=True)
            href = title_link.get('href', '')
            if href and not href.startswith('http'):
                job_data['url'] = f'https://www.upwork.com{href}'
            else:
                job_data['url'] = href

        # ========================== Extract posted time ===========================
        posted_time = job_element.select_one('small[data-test="job-pubilshed-date"]')
        if not posted_time:
            posted_time = job_element.select_one('small')
        
        if posted_time:
            job_data['posted_time'] = posted_time.get_text(strip=True)

        # =============== Extract job info (type, experience level, budget) ================
        job_info = {}
        job_info_items = job_element.select('ul[data-test="JobInfo"] li')
        if not job_info_items:
            job_info_items = job_element.select('ul li')
        
        for item in job_info_items:
            text = item.get_text(strip=True)
            # ==========================  fixed price ===========================
            if 'Fixed price' in text:
                job_info['type'] = 'Fixed price'
            # ==========================  hourly rate ===========================
            elif 'Hourly:' in text:
                job_info['type'] = 'Hourly'
                # Extract hourly rate
                rate_match = re.search(r'Hourly:\s*\$([0-9,.]+)\s*-\s*\$([0-9,.]+)', text)
                if rate_match:
                    job_info['hourly_rate_min'] = rate_match.group(1)
                    job_info['hourly_rate_max'] = rate_match.group(2)
            # ==========================  budget ===========================
            elif 'Est. budget:' in text:
                budget_match = re.search(r'Est\. budget:\s*\$([0-9,.]+)', text)
                if budget_match:
                    job_info['budget'] = budget_match.group(1)
            # ==========================  experience level ===========================
            elif 'Entry Level' in text or 'Intermediate' in text or 'Expert' in text:
                if 'Entry Level' in text:
                    job_info['experience_level'] = 'Entry Level'
                elif 'Intermediate' in text:
                    job_info['experience_level'] = 'Intermediate'
                elif 'Expert' in text:
                    job_info['experience_level'] = 'Expert'
            elif 'Est. time:' in text:
                job_info['duration'] = text.replace('Est. time:', '').strip()
        
        job_data['job_info'] = job_info

        # ========================== Extract description ===========================
        description_elem = job_element.select_one('[data-test="UpCLineClamp JobDescription"] .air3-line-clamp p')
        if not description_elem:
            description_elem = job_element.select_one('.air3-line-clamp p')
        if not description_elem:
            description_elem = job_element.select_one('p')
        
        if description_elem:
            job_data['description'] = description_elem.get_text(strip=True)

        # ========================== Extract skills/tokens ===========================
        skills = []
        skill_elements = job_element.select('[data-test="TokenClamp JobAttrs"] .air3-token span')
        if not skill_elements:
            skill_elements = job_element.select('.air3-token span')
        
        for skill_elem in skill_elements:
            skill_text = skill_elem.get_text(strip=True)
            if skill_text and skill_text not in ['+1', '+2', '+3', '+4', '+5']:  # Skip "more" indicators
                skills.append(skill_text)
        job_data['skills'] = skills
        
        # Only add job if it has at least a title
        if job_data.get('title'):
            jobs.append(job_data)
    
    return jobs
# ======= 🧱 function to extract metadata from HTML =======
def extract_metadata(soup):
    """
    Extract metadata from BeautifulSoup object (optimized - no HTML parsing here)
    """
    # metadata of the page currently being parsed
    metadata = {
        'title': soup.title.get_text(strip=True) if soup.title else '',
        'url': '',
        'scraped_at': datetime.now().isoformat(),
        'total_jobs_found': 0,
        'jobs_count_text': ''
    }
    
    # Try to extract URL from canonical link
    canonical = soup.find('link', {'rel': 'canonical'})
    if canonical:
        metadata['url'] = canonical.get('href', '')
    
    # Extract jobs count from the page
    jobs_count_elem = soup.select_one('[data-test="JobsCountQA JobsCount"]')
    if jobs_count_elem:
        count_text = jobs_count_elem.get_text(strip=True)
        metadata['jobs_count_text'] = count_text
        # Extract number from text like "5,679 jobs found"
        count_match = re.search(r'([\d,]+)\s+jobs?\s+found', count_text)
        if count_match:
            try:
                metadata['total_jobs_on_page'] = int(count_match.group(1).replace(',', ''))
            except ValueError:
                pass
    
    return metadata
def parse_html_content(html_content: str, source_identifier: str = "unknown"):
    """Parse HTML content directly (for database sources)"""
    try:
        # Parse HTML content with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Detect website type
        website_type = detect_website_type(soup)
        
        # Use appropriate parser
        if website_type == "upwork":
            jobs = parse_upwork_jobs(soup)
        else:
            jobs = parse_generic_jobs(soup)
        
        # Extract metadata
        metadata = extract_metadata(soup)
        metadata['total_jobs_found'] = len(jobs)
        metadata['source_file'] = source_identifier
        
        return {
            'metadata': metadata,
            'jobs': jobs,
            'parsing_stats': {
                'html_length': len(html_content),
                'jobs_extracted': len(jobs),
                'parsing_successful': len(jobs) > 0
            }
        }
    except Exception as e:
        return {
            'error': str(e),
            'source_file': source_identifier,
            'parsing_stats': {
                'parsing_successful': False
            }
        }

# ======= 🗃️ Function that parses file and orchestrates other functions =======
def parse_html_file(file_path):

    # open and read HTML file
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        # inside variable call BeautifulSoup amd parse HTML file
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Use auto-detection parsing instead of hardcoded upwork
        parsing_result = parse_jobs_from_html(html_content)
        
        if parsing_result['success']:
            jobs = parsing_result['jobs']
            website_type = parsing_result['website_type']
            print(f'🌐 Detected website type: {website_type}')
        else:
            print(f'❌ Parsing failed: {parsing_result["error"]}')
            jobs = []
            website_type = 'unknown'
        
        # 2. extract_metadata to get page metadata
        metadata = extract_metadata(soup)
        metadata['website_type'] = website_type
        
        metadata['total_jobs_found'] = len(jobs)
        metadata['source_file'] = os.path.basename(file_path)
        # return combined result
        return {
            'metadata': metadata,
            'jobs': jobs,
            'parsing_stats': {
                'html_length': len(html_content),
                'jobs_extracted': len(jobs),
                'parsing_successful': len(jobs) > 0
            }
        }
    # handle exceptions and return error info
    except Exception as e:
        return {
            'error': str(e),
            'source_file': os.path.basename(file_path),
            'parsing_stats': {
                'parsing_successful': False
            }
        }

def get_html_from_database(db: JobDatabase, limit: int = 10) -> List[Tuple[str, str]]:
    """
    Get HTML content from database 
    Returns list of tuples: (source_identifier, html_content)
    """
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    
    # Get recent scraped HTML data - simplified query first
    cursor.execute('''
        SELECT id, file_path, raw_content, source_url, scrape_timestamp
        FROM scraped_data 
        WHERE scrape_type = 'browser'
        ORDER BY scrape_timestamp DESC 
        LIMIT ?
    ''', (limit,))
    
    html_data = []
    for row in cursor.fetchall():
        scrape_id, file_path, html_content, source_url, timestamp = row
        # Check if content is actually HTML
        if html_content and ('<html' in html_content or '<!DOCTYPE' in html_content):
            # Use file_path as identifier, or create one from scrape_id
            identifier = file_path if file_path else f'db_record_{scrape_id}_{timestamp.replace(":", "").replace(" ", "_")}'
            html_data.append((identifier, html_content))
    
    conn.close()
    return html_data

def main():

    # inside varable call argparse to handle powershell arguments
    parser = argparse.ArgumentParser(description='Parse job listings from HTML files (Upwork or generic) and optionally import to DB')
    parser.add_argument('--input', '-i', help='Input HTML file or directory (default: data/data_raw)', default=None)
    parser.add_argument('--import-db', action='store_true', help='Import parsed JSON into SQLite DB')
    parser.add_argument('--direct-db', action='store_true', help='Save jobs directly to database without JSON files')
    parser.add_argument('--from-db', action='store_true', help='Read HTML content from database instead of raw files')
    parser.add_argument('--db-limit', type=int, default=10, help='Limit number of records from database (default: 10)')
    args = parser.parse_args()

    print('🔍 JOB DATA PARSER (Universal)')
    print('==============================')
    print('🌐 Supports: Upwork + Generic job websites')
    if args.from_db:
        print('📊 Reading from database')
    else:
        print('📁 Reading from raw files')
    print()
    # Setup directories
    base_dir = Path(__file__).parent.parent  # Go up to project root
    data_raw_dir = base_dir / 'data' / 'data_raw'
    parsed_dir = base_dir / 'data' / 'data_parsed'
    parsed_dir.mkdir(exist_ok=True)

    # Determine data source
    if args.from_db:
        # Read from database - use new path in data folder
        db_path = base_dir / 'data' / 'jobs.db'
        db = JobDatabase(str(db_path))
        print(f'🗃️  Database path: {db.db_path}')
        html_data = get_html_from_database(db, args.db_limit)
        print(f'🗃️  Found {len(html_data)} HTML records in database')
    else:
        # Read from files
        input_path = Path(args.input) if args.input else data_raw_dir
        html_files = []
        # Check if input path is file or directory
        if input_path.is_file():
            html_files = [input_path]
        elif input_path.is_dir():
            html_files = list(input_path.glob('*.html'))
        else:
            print(f'❌ Input path not found: {input_path}')
            return

        if not html_files:
            print('❌ No HTML files found to parse')
            return

        print(f'📁 Found {len(html_files)} HTML files to parse')
        html_data = [(f, None) for f in html_files]  # Convert to same format

    if not html_data:
        print('❌ No data found to parse')
        return

    total_jobs = 0
    successful_parses = 0
    # inside variable call database manager to handle DB import - use same path
    db_for_import = None
    db_for_direct = None
    
    if args.import_db:
        if args.from_db:
            # Use same database path as reading
            db_path = base_dir / 'data' / 'jobs.db'
            db_for_import = JobDatabase(str(db_path))
        else:
            # Use default path for file imports  
            db_for_import = JobDatabase()
    
    if args.direct_db:
        # Setup direct database insertion
        if args.from_db:
            # Use same database path as reading
            db_path = base_dir / 'data' / 'jobs.db'
            db_for_direct = JobDatabase(str(db_path))
        else:
            db_for_direct = JobDatabase()
    
    # loop through each data source
    for i, (identifier, html_content) in enumerate(html_data):
        # Generate unique timestamp for this parsing session
        session_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if args.from_db:
            print(f'\n📄 Processing database record: {identifier}')
            # Parse HTML content directly from database
            result = parse_html_content(html_content, identifier)
            
            # Update job_uids to be unique for database records
            if 'jobs' in result:
                for j, job in enumerate(result['jobs']):
                    if job.get('job_uid', '').startswith('generic_'):
                        job['job_uid'] = f'db_{session_timestamp}_{i}_{j+1}'
        else:
            # Read from file
            html_file = identifier  # This is a Path object
            print(f'\n📄 Processing: {html_file.name}')
            result = parse_html_file(html_file)
            
        # error handling
        if 'error' not in result:
            jobs_count = result['parsing_stats']['jobs_extracted']
            print(f'✅ Extracted {jobs_count} jobs')
            total_jobs += jobs_count
            successful_parses += 1
            
            # Direct database insertion (skip JSON files)
            if db_for_direct and 'jobs' in result:
                try:
                    # Get or create scrape_id for this HTML source
                    if args.from_db:
                        # For database sources, link to existing scrape_id
                        # Extract scrape_id from identifier if possible
                        scrape_id = 1  # Default fallback
                    else:
                        # For file sources, create new scrape record
                        scrape_id = db_for_direct.add_scraped_data(
                            scrape_type="browser",
                            raw_content=html_content or "File-based scrape",
                            source_url="",
                            file_path=str(identifier) if not args.from_db else identifier,
                            notes=f"Direct import from parser"
                        )
                    
                    # Add jobs directly to database
                    jobs_added = db_for_direct.add_jobs_directly(scrape_id, result['jobs'])
                    print(f'📥 Added directly to DB: {jobs_added} jobs (scrape_id={scrape_id})')
                    
                    # Skip JSON file creation when using direct DB but continue processing
                    
                except Exception as e:
                    print(f'❌ Failed direct DB insertion: {e}')
        else:
            print(f'❌ Error: {result["error"]}')

        # Save parsed data to JSON (only if not using direct DB)
        if not args.direct_db:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            if args.from_db:
                safe_identifier = identifier.replace('/', '_').replace('\\', '_')
                output_filename = f'parsed_db_{safe_identifier}_{timestamp}.json'
            else:
                output_filename = f'parsed_{identifier.stem}_{timestamp}.json'
            output_path = parsed_dir / output_filename
            
            # save to JSON file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            print(f'💾 Saved to: data/data_parsed/{output_filename}')
            
            # Optionally import into DB from JSON
            if db_for_import:
                try:
                    scrape_id, jobs_added = db_for_import.import_from_json_file(str(output_path), scrape_type='browser')
                    print(f'📥 Imported to DB: {jobs_added} jobs (scrape_id={scrape_id})')
                except Exception as e:
                    print(f'❌ Failed to import into DB: {e}')
        else:
            print(f'⏭️  Skipped JSON file creation (direct DB mode)')

    # Summary
    print(f'\n📊 PARSING SUMMARY')
    print(f'================')
    if args.from_db:
        print(f'Database records processed: {len(html_data)}')
    else:
        print(f'Files processed: {len(html_data)}')
    print(f'Successful parses: {successful_parses}')
    print(f'Total jobs extracted: {total_jobs}')
    print(f'Results saved in: data/data_parsed/')

if __name__ == '__main__':
    main()