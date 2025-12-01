#!/usr/bin/env python3
"""
ORCID to YAML Exporter
Fetches publications from ORCID and generates a publications.yaml file
Usage: python orcid_exporter.py YOUR_ORCID_ID
Example: python orcid_exporter.py 0000-0003-0647-2634
"""

import requests
import sys
import re
from datetime import datetime
import time

def clean_text(text):
    """Remove HTML tags and clean text"""
    if not text:
        return ""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    # Escape quotes for YAML
    text = text.replace('"', '\\"')
    return text

def safe_get(obj, *keys, default=''):
    """Safely get nested dictionary values"""
    for key in keys:
        if obj is None:
            return default
        if isinstance(obj, dict):
            obj = obj.get(key)
        else:
            return default
    return obj if obj is not None else default

def get_orcid_publications(orcid_id):
    """Fetch publications from ORCID public API"""
    print(f"Fetching publications for ORCID: {orcid_id}")
    
    url = f"https://pub.orcid.org/v3.0/{orcid_id}/works"
    headers = {'Accept': 'application/json'}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching ORCID data: {e}")
        return None

def get_crossref_data(doi):
    """Fetch additional metadata from CrossRef"""
    if not doi:
        return None
    
    # Clean DOI
    doi = doi.strip()
    
    url = f"https://api.crossref.org/works/{doi}"
    try:
        response = requests.get(url, timeout=10)
        if response.ok:
            return response.json()['message']
    except Exception as e:
        pass
    return None

def format_authors(crossref_data):
    """Format author list from CrossRef data"""
    if not crossref_data or 'author' not in crossref_data:
        return None
    
    authors = []
    for author in crossref_data['author']:
        family = author.get('family', '')
        given = author.get('given', '')
        if family and given:
            # Format as "Last, F."
            given_initial = given[0] + '.' if given else ''
            authors.append(f"{family}, {given_initial}")
        elif family:
            authors.append(family)
    
    if not authors:
        return None
    
    # Limit to 10 authors
    if len(authors) > 10:
        return ', '.join(authors[:10]) + ', et al.'
    return ', '.join(authors)

def categorize_type(work_type):
    """Map ORCID work type to our categories"""
    if not work_type:
        return 'other'
    
    work_type = work_type.lower()
    
    if any(x in work_type for x in ['journal', 'article']):
        return 'journal'
    elif 'workshop' in work_type:
        return 'workshop'
    elif any(x in work_type for x in ['conference', 'proceedings']):
        return 'conference'
    elif any(x in work_type for x in ['book', 'chapter']):
        return 'book-chapter'
    elif 'preprint' in work_type:
        return 'preprint'
    else:
        return 'other'

def generate_id(title, year, authors):
    """Generate a publication ID"""
    # Get first author's last name
    first_author = "author"
    if authors:
        # Extract first last name
        first_part = authors.split(',')[0].strip()
        # Remove any non-letters
        first_author = re.sub(r'[^a-zA-Z]', '', first_part).lower()
    
    # Get first meaningful word from title (at least 4 letters)
    title_words = re.findall(r'\b[a-zA-Z]{4,}\b', title.lower())
    keyword = title_words[0] if title_words else "paper"
    
    # Combine
    pub_id = f"{first_author}{year}{keyword}"
    
    return pub_id

def extract_abstract_summary(abstract):
    """Extract first 1-2 sentences from abstract as summary"""
    if not abstract:
        return None
    
    # Split by sentence
    sentences = re.split(r'[.!?]\s+', abstract)
    
    if not sentences:
        return None
    
    # Take first sentence, or first two if first is very short
    summary = sentences[0]
    if len(summary) < 50 and len(sentences) > 1:
        summary = sentences[0] + '. ' + sentences[1]
    
    # Limit length
    if len(summary) > 200:
        summary = summary[:200].rsplit(' ', 1)[0] + '...'
    
    return summary

def process_publications(orcid_data):
    """Process ORCID data and extract publication info"""
    if not orcid_data or 'group' not in orcid_data:
        return []
    
    publications = []
    total = len(orcid_data['group'])
    
    print(f"\nProcessing {total} publications...\n")
    
    for i, group in enumerate(orcid_data['group'], 1):
        try:
            work = group['work-summary'][0]
            
            # Basic info with safe extraction
            title = safe_get(work, 'title', 'title', 'value', default='Untitled')
            year = safe_get(work, 'publication-date', 'year', 'value', default='Unknown')
            work_type = safe_get(work, 'type', default='other')
            category = categorize_type(work_type)
            
            # Get DOI
            doi = None
            external_ids = safe_get(work, 'external-ids', 'external-id', default=[])
            if external_ids:
                for ext_id in external_ids:
                    if ext_id.get('external-id-type') == 'doi':
                        doi = ext_id.get('external-id-value')
                        break
            
            # Venue - handle None case
            journal_title = work.get('journal-title')
            if journal_title and isinstance(journal_title, dict):
                venue = journal_title.get('value', 'Unknown Venue')
            else:
                venue = 'Unknown Venue'
            
            # Try to get more info from CrossRef
            authors = None
            abstract = None
            summary = None
            paper_url = None
            
            print(f"[{i}/{total}] {title[:60]}...")
            
            if doi:
                print(f"    Fetching metadata from CrossRef...")
                crossref = get_crossref_data(doi)
                
                if crossref:
                    # Get authors
                    authors = format_authors(crossref)
                    
                    # Get venue (might be better than ORCID)
                    if 'container-title' in crossref and crossref['container-title']:
                        venue = crossref['container-title'][0]
                    
                    # Get abstract
                    if 'abstract' in crossref:
                        abstract = clean_text(crossref['abstract'])
                        summary = extract_abstract_summary(abstract)
                    
                    # Get URL
                    if 'URL' in crossref:
                        paper_url = crossref['URL']
                
                # Small delay to be nice to CrossRef API
                time.sleep(0.5)
            else:
                print(f"    No DOI found")
            
            # If still no authors, use a placeholder
            if not authors:
                authors = "Authors not available"
            
            # Generate ID
            pub_id = generate_id(title, str(year), authors)
            
            # Create publication entry
            pub = {
                'id': pub_id,
                'title': clean_text(title),
                'authors': authors,
                'venue': clean_text(venue),
                'year': year,
                'type': category,
                'doi': doi,
                'paper_url': paper_url,
                'summary': summary
            }
            
            publications.append(pub)
            
        except Exception as e:
            print(f"    ⚠️  Error processing publication {i}: {e}")
            continue
    
    # Sort by year (most recent first), then by title
    publications.sort(key=lambda x: (
        -int(x['year']) if str(x['year']).isdigit() else 0,
        x['title']
    ))
    
    return publications

def write_yaml(publications, filename='publications.yaml'):
    """Write publications to YAML file"""
    print(f"\n{'='*60}")
    print(f"Writing {len(publications)} publications to {filename}...")
    print(f"{'='*60}\n")
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("# publications.yaml\n")
        f.write("# Edit this file to manage your publications\n")
        f.write("# The website will automatically read and display them\n")
        f.write(f"# Generated from ORCID on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("publications:\n")
        
        for pub in publications:
            f.write(f"\n  # {pub['type'].upper()} - {pub['year']}\n")
            f.write(f"  - id: {pub['id']}\n")
            f.write(f"    title: \"{pub['title']}\"\n")
            f.write(f"    authors: \"{pub['authors']}\"\n")
            f.write(f"    venue: \"{pub['venue']}\"\n")
            f.write(f"    year: {pub['year']}\n")
            f.write(f"    type: {pub['type']}  # journal, conference, workshop, book-chapter, preprint, other\n")
            
            if pub['doi']:
                f.write(f"    doi: \"{pub['doi']}\"\n")
            
            if pub['paper_url']:
                f.write(f"    paper_url: \"{pub['paper_url']}\"\n")
            else:
                f.write(f"    # paper_url: \"\"  # Add direct link to paper if available\n")
            
            if pub['summary']:
                f.write(f"    summary: \"{pub['summary']}\"\n")
            else:
                f.write(f"    # summary: \"\"  # Add a one-sentence summary of the paper\n")
            
            f.write(f"    # image: \"{pub['id']}.jpg\"  # Optional - add image file to images/papers/\n")
        
        # Add template
        f.write("\n\n# --------------------------------------------------\n")
        f.write("# TEMPLATE: Copy this to add a new publication\n")
        f.write("# --------------------------------------------------\n")
        f.write("#\n")
        f.write("#  - id: lastname2024keyword\n")
        f.write("#    title: \"Your Paper Title\"\n")
        f.write("#    authors: \"Last, F., Last, F., Last, F.\"\n")
        f.write("#    venue: \"Journal or Conference Name\"\n")
        f.write("#    year: 2024\n")
        f.write("#    type: journal  # journal, conference, workshop, book-chapter, preprint, other\n")
        f.write("#    doi: \"10.xxxx/xxxxx\"\n")
        f.write("#    paper_url: \"https://...\"\n")
        f.write("#    summary: \"One sentence summary of the paper.\"\n")
        f.write("#    image: \"lastname2024keyword.jpg\"  # Optional\n")
    
    print(f"✅ Successfully created {filename}\n")

def print_summary(publications):
    """Print summary statistics"""
    print(f"{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}\n")
    
    type_counts = {}
    for pub in publications:
        t = pub['type']
        type_counts[t] = type_counts.get(t, 0) + 1
    
    print(f"Total publications: {len(publications)}\n")
    
    type_names = {
        'journal': 'Journal Articles',
        'conference': 'Conference Papers',
        'workshop': 'Workshop Papers',
        'book-chapter': 'Book Chapters',
        'preprint': 'Preprints',
        'other': 'Other'
    }
    
    for type_key, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        name = type_names.get(type_key, type_key.title())
        print(f"  {name}: {count}")
    
    # Check for missing data
    missing_summary = sum(1 for p in publications if not p['summary'])
    missing_doi = sum(1 for p in publications if not p['doi'])
    
    print(f"\n📋 Data completeness:")
    print(f"  Publications with DOI: {len(publications) - missing_doi}/{len(publications)}")
    print(f"  Publications with summary: {len(publications) - missing_summary}/{len(publications)}")
    
    print(f"\n✏️  Next steps:")
    print(f"  1. Review publications.yaml and edit as needed")
    print(f"  2. Add summaries for publications missing them")
    print(f"  3. Remove duplicates if any")
    print(f"  4. Add images to images/papers/ (optional)")
    print(f"  5. Move to data/: mv publications.yaml data/publications.yaml")
    print(f"  6. Test website: python -m http.server 8000\n")

def main():
    if len(sys.argv) != 2:
        print("Usage: python orcid_exporter.py YOUR_ORCID_ID")
        print("Example: python orcid_exporter.py 0000-0003-0647-2634")
        sys.exit(1)
    
    orcid_id = sys.argv[1]
    
    # Validate ORCID format
    if not re.match(r'\d{4}-\d{4}-\d{4}-\d{3}[0-9X]', orcid_id):
        print("❌ Error: Invalid ORCID ID format")
        print("Should be like: 0000-0003-0647-2634")
        sys.exit(1)
    
    # Fetch data
    orcid_data = get_orcid_publications(orcid_id)
    if not orcid_data:
        print("❌ Failed to fetch ORCID data")
        sys.exit(1)
    
    # Process publications
    publications = process_publications(orcid_data)
    
    if not publications:
        print("❌ No publications found")
        sys.exit(1)
    
    # Write to file
    write_yaml(publications)
    
    # Print summary
    print_summary(publications)

if __name__ == '__main__':
    main()