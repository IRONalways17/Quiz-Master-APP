#!/usr/bin/env python3
"""
Migration script to fix duplicate chapter slugs across subjects
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import Chapter, Subject
from app.database import db
from collections import defaultdict

def fix_duplicate_chapter_slugs():
    """Fix duplicate chapter slugs by making them unique within their context"""
    app = create_app()
    
    with app.app_context():
        print("🔍 Checking for duplicate chapter slugs...")
        print("=" * 60)
        
        # Get all chapters grouped by slug
        chapters_by_slug = defaultdict(list)
        all_chapters = Chapter.query.filter_by(is_active=True).all()
        
        for chapter in all_chapters:
            chapters_by_slug[chapter.slug].append(chapter)
        
        # Find duplicates
        duplicates = {slug: chapters for slug, chapters in chapters_by_slug.items() if len(chapters) > 1}
        
        if not duplicates:
            print("✅ No duplicate chapter slugs found!")
            return
        
        print(f"❌ Found {len(duplicates)} duplicate slugs affecting {sum(len(chapters) for chapters in duplicates.values())} chapters:")
        print()
        
        fixed_count = 0
        
        for slug, chapters in duplicates.items():
            print(f"📝 Fixing duplicate slug: '{slug}'")
            
            # Group chapters by subject for better context
            subjects_info = []
            for chapter in chapters:
                subject_name = chapter.subject.name if chapter.subject else "Unknown"
                subjects_info.append(f"  - {chapter.name} (Subject: {subject_name}, ID: {chapter.id})")
            
            print("  Found in:")
            for info in subjects_info:
                print(info)
            
            # Keep the first chapter with the original slug, modify others
            for i, chapter in enumerate(chapters[1:], 1):  # Start from second chapter
                old_slug = chapter.slug
                
                # Generate new unique slug
                base_slug = Chapter.generate_slug(chapter.name)
                subject_prefix = chapter.subject.slug[:8] if chapter.subject else "subj"
                new_slug = f"{subject_prefix}-{base_slug}"
                
                # Ensure it's unique
                counter = 1
                while Chapter.query.filter(Chapter.slug == new_slug, Chapter.id != chapter.id).first():
                    new_slug = f"{subject_prefix}-{base_slug}-{counter}"
                    counter += 1
                
                chapter.slug = new_slug
                print(f"    ✏️  Updated '{old_slug}' → '{new_slug}' (Chapter ID: {chapter.id})")
                fixed_count += 1
            
            print()
        
        # Commit all changes
        try:
            db.session.commit()
            print("=" * 60)
            print(f"✅ Successfully fixed {fixed_count} duplicate chapter slugs!")
            print()
            print("📊 Summary of changes:")
            
            # Show final state
            for slug, chapters in duplicates.items():
                print(f"  Original slug '{slug}':")
                for chapter in chapters:
                    subject_name = chapter.subject.name if chapter.subject else "Unknown"
                    print(f"    → '{chapter.slug}' (Subject: {subject_name})")
                print()
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error committing changes: {e}")
            return
        
        print("💡 Recommendations:")
        print("  1. Update frontend routes to use /subjects/{subject_slug}/chapters/{chapter_slug}")
        print("  2. Consider avoiding duplicate chapter names across subjects")
        print("  3. Test all chapter quiz navigation to ensure it works correctly")

def check_current_duplicates():
    """Check current state of duplicate chapter names across subjects"""
    app = create_app()
    
    with app.app_context():
        print("🔍 Current duplicate chapter names across subjects:")
        print("=" * 60)
        
        try:
            duplicates = Chapter.check_duplicate_names_across_subjects()
            
            if not duplicates:
                print("✅ No duplicate chapter names found across subjects!")
                return
            
            print(f"❌ Found {len(duplicates)} chapter names used in multiple subjects:")
            print()
            
            for duplicate in duplicates:
                print(f"📝 Chapter name: '{duplicate['name']}'")
                print(f"   Used in {duplicate['subject_count']} different subjects")
                
                # Get details for this name
                chapters = Chapter.query.filter_by(name=duplicate['name'], is_active=True).all()
                for chapter in chapters:
                    subject_name = chapter.subject.name if chapter.subject else "Unknown"
                    print(f"     - Subject: {subject_name} (slug: {chapter.slug})")
                print()
                
        except Exception as e:
            print(f"❌ Error checking duplicates: {e}")

if __name__ == "__main__":
    print("Chapter Slug Duplication Fix Tool")
    print("=" * 60)
    print()
    
    # First, check current duplicates
    check_current_duplicates()
    print()
    
    # Then fix slug duplicates
    fix_duplicate_chapter_slugs()
