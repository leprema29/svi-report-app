#!/usr/bin/env python3
"""
Test script to extract KPIs from the uploaded PDF and generate Word document
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from reports.services.pdf_extractor import extract_kpis_from_pdf
from reports.services.word_generator import generate_word_report
import json


def test_extraction(pdf_path: str, output_dir: str = '.'):
    """Test PDF extraction and Word generation"""
    
    print("=" * 60)
    print("SURVEILLANCE REPORT EXTRACTION TEST")
    print("=" * 60)
    print(f"\nInput PDF: {pdf_path}")
    
    # Check if file exists
    if not os.path.exists(pdf_path):
        print(f"ERROR: File not found: {pdf_path}")
        return
    
    print("\n1. Extracting KPIs from PDF...")
    print("-" * 60)
    
    try:
        extracted_data = extract_kpis_from_pdf(pdf_path)
        
        # Display extracted data
        print("\n📊 EXTRACTED DATA:")
        print(f"\nTitle: {extracted_data.get('title', 'N/A')}")
        
        period = extracted_data.get('period', {})
        print(f"Period: {period.get('start', 'N/A')} to {period.get('end', 'N/A')}")
        
        volume = extracted_data.get('volume', {})
        print(f"\nVolume: {volume.get('mentions', 0):,} mentions")
        print(f"Change: {volume.get('change_percent', 0):+.2f}%")
        
        reach = extracted_data.get('reach', {})
        print(f"\nReach: {reach.get('reach', 0):,}")
        print(f"Change: {reach.get('change_percent', 0):+.2f}%")
        
        sentiment = extracted_data.get('sentiment', {})
        if sentiment:
            print(f"\nSentiment:")
            for key, value in sentiment.items():
                print(f"  - {key.capitalize()}: {value}")
        
        emotion = extracted_data.get('emotion', {})
        if emotion:
            print(f"\nEmotion (top 3):")
            sorted_emotions = sorted(emotion.items(), key=lambda x: x[1], reverse=True)[:3]
            for key, value in sorted_emotions:
                print(f"  - {key.capitalize()}: {value}")
        
        sources = extracted_data.get('sources', {})
        if sources:
            print(f"\nSources:")
            for key, value in sources.items():
                print(f"  - {key}: {value}")
        
        topics = extracted_data.get('topics', [])
        if topics:
            print(f"\nTop 5 Topics:")
            for idx, topic in enumerate(topics[:5], 1):
                print(f"  {idx}. {topic.get('name', 'N/A')} ({topic.get('count', 0)})")
        
        hashtags = extracted_data.get('hashtags', [])
        if hashtags:
            print(f"\nTop 5 Hashtags:")
            for idx, hashtag in enumerate(hashtags[:5], 1):
                print(f"  {idx}. {hashtag.get('hashtag', 'N/A')} ({hashtag.get('count', 0)})")
        
        influencers = extracted_data.get('influencers', [])
        if influencers:
            print(f"\nTop 5 Influencers:")
            for idx, influencer in enumerate(influencers[:5], 1):
                print(f"  {idx}. {influencer.get('name', 'N/A')} (Score: {influencer.get('influence_score', 0)}/100)")
        
        # Save extracted data to JSON
        json_path = os.path.join(output_dir, 'extracted_data.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Extracted data saved to: {json_path}")
        
        print("\n2. Generating Word document...")
        print("-" * 60)
        
        # Generate Word document
        docx_path = os.path.join(output_dir, 'surveillance_report.docx')
        generate_word_report(extracted_data, docx_path)
        
        print(f"\n✅ Word document generated: {docx_path}")
        
        print("\n" + "=" * 60)
        print("TEST COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
        print("\nFiles created:")
        print(f"  1. {json_path} - Extracted data (JSON)")
        print(f"  2. {docx_path} - Formatted report (Word)")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return


if __name__ == '__main__':
    # Default to the uploaded PDF file
    pdf_file = '/mnt/user-data/uploads/Dashboard_-_Candidat_Paul_Biya.pdf'
    output_directory = '/home/claude'
    
    # Allow command-line arguments
    if len(sys.argv) > 1:
        pdf_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_directory = sys.argv[2]
    
    test_extraction(pdf_file, output_directory)
