import os
import requests
import json

# URL of the deployed Google Apps Script Web App
WEBAPP_URL = "https://script.google.com/macros/s/AKfycbwTTA-I2kowyC4EAei01ZSJBdZowDOKv1zJQQD7Fthm6kXgIdT3K9DzweOzJVbrBhyDhw/exec"
SYNC_URL = f"{WEBAPP_URL}?action=sync"

# Directory to save the summaries
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SUMMARIES_DIR = os.path.join(SCRIPT_DIR, "summaries")

def append_to_master(category, content, original_filename):
    # Save all business meeting summaries into the central all_meetings_business.md in parent D-Dialog folder
    # while D-Dialog / general educational summaries go to all_meeting_summaries.md
    if category == "D-Dialog":
        master_path = os.path.join(os.path.dirname(SCRIPT_DIR), "all_meeting_summaries.md")
    else:
        master_path = os.path.join(os.path.dirname(SCRIPT_DIR), "all_meetings_business.md")
        
    # Append content with a separator
    with open(master_path, "a", encoding="utf-8") as f:
        f.write(f"\n\n---\n\n## מקור: {original_filename} (קטגוריה: {category})\n\n")
        f.write(content)

def sync_summaries():
    print(f"Connecting to cloud to fetch MD files...")
    
    if not os.path.exists(SUMMARIES_DIR):
        os.makedirs(SUMMARIES_DIR)
        
    try:
        response = requests.get(SYNC_URL)
        response.raise_for_status()
        
        try:
            files = response.json()
        except json.JSONDecodeError:
            print("Error decoding JSON response. The link might be incorrect or there is an authorization issue.")
            return
            
        if 'error' in files:
            print(f"Error from server: {files['error']}")
            return

        new_files = 0
        print(f"Found {len(files)} files in cloud. Syncing...")
        
        for file_data in files:
            file_name = file_data.get('name')
            file_content = file_data.get('content')
            category = file_data.get('category', 'D-Dialog')
            
            if not file_name or not file_content:
                continue
                
            file_path = os.path.join(SUMMARIES_DIR, file_name)
            
            # Save only if the file doesn't already exist locally
            if not os.path.exists(file_path):
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(file_content)
                print(f"Downloaded new file: {file_name} (Category: {category})")
                new_files += 1
                
                # Append to the category master file
                append_to_master(category, file_content, file_name)
                print(f" -> Appended to master file for {category}")
                
        if new_files == 0:
            print("Everything is up to date! No new files found.")
        else:
            print(f"Sync complete! {new_files} new files were processed.")
            
    except Exception as e:
        print(f"Error during sync: {e}")

if __name__ == "__main__":
    sync_summaries()
