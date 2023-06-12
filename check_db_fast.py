import hashlib
import pandas as pd
from bs4 import BeautifulSoup
from pymongo import MongoClient
from collections import defaultdict
import json
import time
import re
from tqdm.auto import tqdm
import os

with open("db_meta.json") as f:
    db_info = json.load(f)

client = MongoClient(host=db_info['host'], port=db_info['port'], username=db_info['username'], password=str(db_info['password']))

def get_hash(text):
    """
    This function calculates and returns the MD5 hash of the input text.

    Parameters:
    text (str): A string for which the MD5 hash is to be calculated.

    Returns:
    str: The MD5 hash of the input text.
    """
    return hashlib.md5(text.encode()).hexdigest()

def get_text_from_html(html):
    """
    This function reads an HTML file, parses it using BeautifulSoup, and returns the text contained in the HTML.

    Parameters:
    html (str): Path to the HTML file to be read.

    Returns:
    str: Text contained in the HTML file.
    """
    with open(html, 'r') as f:
        contents = f.read()
    soup = BeautifulSoup(contents, 'html.parser')
    return soup.get_text()

def seconds_to_hms(seconds):
    """
    This function converts a time given in seconds into hours, minutes, and seconds.

    Parameters:
    seconds (int or float): The amount of time in seconds.

    Returns:
    tuple: A tuple containing hours, minutes, and seconds.
    """
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return hours, minutes, seconds
        
try:
    # Database Setup
    db = client['kind_data']
    collection = db['report']
    documents = collection.find()
    collection_data = [document for document in documents]

    # Initialization of Variables
    hash_to_numerical_paths = defaultdict(set)
    hash_to_documents = defaultdict(list)
    bad_hashes = set()
    saved_list = set()

    # Populating the 'saved_list' Set
    with open('saved_list2.txt', 'r') as file:
        for line in file:
            saved_list.add(line.strip())

    """
    Main Loop:
    Here the main loop begins. It iterates over each document in 'collection_data'. 
    tqdm' is a library that provides a progress bar for long-running operations. 
    The loop measures the time it took to process all documents.
    """
    start_time = time.time()
    for i, document in enumerate(tqdm(collection_data, desc=f"Hashing Documents", total=collection.count_documents({}))):

        # Skipping Documents
        excel_path = document['excel_path']
        if not excel_path or not os.path.exists(excel_path):
            with open('not_found2.txt', 'a') as fout:
                fout.write(str(document.get("_id")) + '\n')
                continue
        if excel_path in saved_list:
            continue
        with open('saved_list2.txt', 'a') as fout:
            fout.write(excel_path+'\n')

        # Processing Documents
        numerical_path = ''.join(re.findall(r'\d+', excel_path))
        text = get_text_from_html(excel_path)
        hash_value = get_hash(text)

        document_data = {
            "_id": document['_id'],
            "company": document['company'],
            "title": document['title'],
            "url": document['url'],
            "excel_path": document['excel_path'],
            "hash": hash_value,
        }

        hash_to_documents[hash_value].append(document_data)
        hash_to_numerical_paths[hash_value].add(numerical_path)

        if len(hash_to_numerical_paths[hash_value]) > 1:
            bad_hashes.add(hash_value)

    """
    After the Main Loop: 
    Once the loop finishes, the code calculates the elapsed time and prints it in a human-readable format (hours, minutes, seconds). 
    It also prints the total number of unique hashes found during the processing of the documents.
    """
    loop_end_time = time.time()
    hash_loop_time = loop_end_time - start_time
    new_hash_loop_time = seconds_to_hms(hash_loop_time)
    print(f"For loop ended at: {new_hash_loop_time[0]:.0f} hours {new_hash_loop_time[1]:.0f} minutes {new_hash_loop_time[2]:.2f} seconds")

    print("Number of hashes:", len(hash_to_documents))

    """
    Identifying Duplicates:
    This code identifies the hashes that correspond to more than one document and are in the set of bad_hashes, and stores these as duplicates. 
    It calculates and prints the time taken for this operation and the total number of duplicate hashes found.
    """
    start_time_duplicates = time.time()
    duplicates = {k: v for k, v in hash_to_documents.items() if len(v) > 1 and k in bad_hashes}
    end_time_duplicates = time.time()

    time_taken_duplicates = end_time_duplicates - start_time_duplicates
    new_time_taken_duplicates = seconds_to_hms(time_taken_duplicates)

    print(f"Time taken to generate duplicates: {new_time_taken_duplicates[0]:.0f} hours {new_time_taken_duplicates[1]:.0f} minutes {new_time_taken_duplicates[2]:.2f} seconds")
    print("Number of Bad hashes:", len(duplicates))

    """
    Finalizing:
    The total execution time for the script is calculated by adding the time taken for duplicate detection and the time for processing the documents. 
    This is then printed out in a human-readable format.
    """
    total_execution_time = time_taken_duplicates + hash_loop_time
    new_total_execution_time = seconds_to_hms(total_execution_time)

    print(f"Total execution time: {new_total_execution_time[0]:.0f} hours {new_total_execution_time[1]:.0f} minutes {new_total_execution_time[2]:.2f} seconds")

    """
    Sorting Duplicates:
    This code iterates over all duplicate hashes. 
    For each hash, if there are more than two corresponding documents, these are added to a list named 'multiples_data'. 
    If there are exactly two corresponding documents, these are added to a list named 'singles_data'.
    """
    multiples_data = []
    singles_data = []

    for hash_value, documents in duplicates.items():
        if len(documents) > 2:
            multiples_data.extend(documents)
        else:
            singles_data.extend(documents)

    """
    Saving Results:
    The lists 'multiples_data' and 'singles_data' are converted to pandas DataFrames. 
    Then, using the 'pd.ExcelWriter' context manager, both DataFrames are saved in an Excel file called 'duplicate_documents.xlsx' in separate sheets.
    """
    multiples_df = pd.DataFrame(multiples_data)
    singles_df = pd.DataFrame(singles_data)

    # Save dataframes to Excel
    with pd.ExcelWriter('duplicate_documents.xlsx') as writer:
        multiples_df.to_excel(writer, sheet_name='Multiples', index=False)
        singles_df.to_excel(writer, sheet_name='Singles', index=False)

except Exception as e:
    print(f"An error occurred: {str(e)}")