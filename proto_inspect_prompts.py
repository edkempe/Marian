#!/usr/bin/env python3
import sqlite3
import json
from tabulate import tabulate
import pandas as pd

def inspect_prompts_db():
    conn = sqlite3.connect('prompts.db')
    conn.row_factory = sqlite3.Row
    
    # Get all prompts
    cursor = conn.execute('''
        SELECT prompt_id, prompt_text, version_number, created_date, active,
               model_name, max_tokens, description, script_name,
               expected_response_format, required_input_fields,
               token_estimate, times_used, average_confidence_score,
               average_response_time_ms, failure_rate
        FROM prompts
        ORDER BY created_date DESC
    ''')
    
    rows = [dict(row) for row in cursor.fetchall()]
    if not rows:
        print("No prompts found in database")
        return
    
    # Basic info
    basic_info = pd.DataFrame([{
        'ID': row['prompt_id'],
        'Version': row['version_number'],
        'Script': row['script_name'],
        'Model': row['model_name'],
        'Active': row['active'],
        'Created': row['created_date']
    } for row in rows])
    
    print("\n=== Prompts Overview ===")
    print(tabulate(basic_info, headers='keys', tablefmt='pretty'))
    
    # Detailed view of each prompt
    for row in rows:
        print(f"\n=== Prompt Details for Version {row['version_number']} ===")
        print(f"Description: {row['description']}")
        print(f"Script: {row['script_name']}")
        print(f"Model: {row['model_name']}")
        print(f"Max Tokens: {row['max_tokens']}")
        print(f"Token Estimate: {row['token_estimate']}")
        
        print("\nPrompt Text:")
        print("-" * 80)
        print(row['prompt_text'])
        print("-" * 80)
        
        print("\nRequired Input Fields:")
        print(json.loads(row['required_input_fields']))
        
        print("\nExpected Response Format:")
        print(json.dumps(json.loads(row['expected_response_format']), indent=2))
        
        print("\nUsage Statistics:")
        stats = {
            'Times Used': row['times_used'],
            'Avg Confidence': row['average_confidence_score'],
            'Avg Response Time (ms)': row['average_response_time_ms'],
            'Failure Rate': row['failure_rate']
        }
        print(json.dumps(stats, indent=2))
        print("\n" + "="*80)

if __name__ == "__main__":
    inspect_prompts_db()
