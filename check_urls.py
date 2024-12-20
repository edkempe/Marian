#!/usr/bin/env python3
import sqlite3
import json

def check_long_urls():
    conn = sqlite3.connect('email_analysis.db')
    cur = conn.cursor()
    
    # Get all URLs from links_found
    cur.execute('SELECT email_id, links_found FROM email_analysis')
    results = cur.fetchall()
    
    long_urls = []
    for email_id, links in results:
        if links:
            urls = json.loads(links)
            for url in urls:
                if len(url) > 100:
                    long_urls.append((email_id, url, len(url)))
    
    if long_urls:
        print(f"Found {len(long_urls)} URLs longer than 100 characters:")
        for email_id, url, length in long_urls:
            print(f"\nEmail ID: {email_id}")
            print(f"URL Length: {length}")
            print(f"URL: {url}")
    else:
        print("No URLs longer than 100 characters found.")
    
    conn.close()

if __name__ == "__main__":
    check_long_urls()
