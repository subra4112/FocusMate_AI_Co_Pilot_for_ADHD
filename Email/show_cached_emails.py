"""Display cached emails from the local database."""

import sys
import io
from pathlib import Path

# Set UTF-8 encoding for console output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent))

from db import load_recent_processed
from pprint import pprint


def show_cached_emails():
    """Display all cached emails organized by classification."""
    print("="*80)
    print("CACHED EMAILS FROM DATABASE")
    print("="*80)
    
    # Load emails from database (limit 10 per category)
    cached = load_recent_processed(limit_per_category=10)
    
    total_count = sum(len(emails) for emails in cached.values())
    print(f"\nTotal cached emails: {total_count}\n")
    
    for category, emails in cached.items():
        print(f"\n{'='*80}")
        print(f"CATEGORY: {category.upper()} ({len(emails)} emails)")
        print('='*80)
        
        if not emails:
            print("  (No emails in this category)")
            continue
        
        for i, email in enumerate(emails, 1):
            print(f"\n{i}. {email.subject}")
            print(f"   From: {email.sender}")
            print(f"   Classification: {email.classification}")
            print(f"   Priority: {email.priority_bucket} (score: {email.priority_score})")
            
            if email.summary:
                summary = email.summary[:150] + "..." if len(email.summary) > 150 else email.summary
                print(f"   Summary: {summary}")
            
            if email.notes:
                print(f"   Notes: {', '.join(email.notes[:3])}")
            
            if email.priority_reasoning:
                reasoning = email.priority_reasoning[:150] + "..." if len(email.priority_reasoning) > 150 else email.priority_reasoning
                print(f"   Reasoning: {reasoning}")
    
    print("\n" + "="*80)
    print("END OF CACHED EMAILS")
    print("="*80)


if __name__ == "__main__":
    show_cached_emails()

