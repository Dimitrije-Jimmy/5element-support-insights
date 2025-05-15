#!/usr/bin/env python
"""Classify messages using BERT and save results."""
import csv
import pandas as pd
from pathlib import Path
from app.services.bert_classifier import classify

def classify_messages(input_csv: Path, output_csv: Path):
    # Read input CSV
    df = pd.read_csv(input_csv)
    
    print(f"Processing {len(df)} messages...")
    results = []
    for idx, row in df.iterrows():
        if idx % 100 == 0:
            print(f"Progress: {idx}/{len(df)}")
            
        message = row['message']
        # Get classification
        category = classify(message)
        
        # Add to results
        result = row.to_dict()
        result['category'] = category
        results.append(result)
    
    # Save to new CSV
    with output_csv.open('w', newline='', encoding='utf-8') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    
    print(f"\n✅ Classified {len(results)} messages → {output_csv}")
    
    # Print category distribution
    df_results = pd.DataFrame(results)
    print("\nCategory Distribution:")
    print(df_results['category'].value_counts())

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("input_csv", type=Path)
    p.add_argument("output_csv", type=Path)
    args = p.parse_args()
    
    classify_messages(args.input_csv, args.output_csv) 