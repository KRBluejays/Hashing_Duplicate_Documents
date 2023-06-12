# Duplicate Document Detection Tool

This repository contains Python script to detect duplicate documents in a MongoDB database by hashing the contents of the documents. The hashes are then compared to identify the duplicates. This can be especially useful in situations where you have large amounts of data and need to ensure that there are no duplicates.

## Code Overview

This Python script consists of various functions and the main block that accesses MongoDB database and identifies duplicates in the documents:

- **get_hash(text)**: This function calculates and returns the MD5 hash of the input text.
- **get_text_from_html(html)**: This function reads an HTML file, parses it using BeautifulSoup, and returns the text contained in the HTML.
- **seconds_to_hms(seconds)**: This function converts a time given in seconds into hours, minutes, and seconds.
- **Main Loop**: The main loop begins by reading from a MongoDB collection and measures the time taken to process all the documents. It skips over documents that are not found or already processed. For the remaining documents, it processes them and keeps track of the unique hashes.
- **After the Main Loop**: Once the loop finishes, the code calculates the elapsed time and prints it. It also prints the total number of unique hashes found during the processing of the documents.
- **Identifying Duplicates**: This part of the code identifies the hashes that correspond to more than one document, these are considered as duplicates. It calculates and prints the time taken for this operation and the total number of duplicate hashes found.
- **Finalizing**: The total execution time for the script is calculated and printed out.
- **Sorting Duplicates**: This code sorts the duplicates into 'multiples_data' and 'singles_data'.
- **Saving Results**: The 'multiples_data' and 'singles_data' are saved to an Excel file named 'duplicate_documents.xlsx' in separate sheets.

## Requirements

The Python script uses several libraries that you will need to install:

- hashlib
- pandas
- beautifulsoup4
- pymongo
- json
- re
- tqdm
- os

You can install these libraries using pip:

```
pip install beautifulsoup4 pandas pymongo tqdm
```

## How to run

To run the script, you need to set up your MongoDB database and update the 'db_meta.json' file with your database information such as host, port, username, and password.

```json
{
    "host": "your-host",
    "port": your-port,
    "username": "your-username",
    "password": "your-password"
}
```

Make sure that the 'db_meta.json' file and 'saved_list2.txt' file are in the same directory as the script. 

Now, you can run the script with the following command:

```
python your-script.py
```

## Output

The script will print the progress and results in the terminal, such as the time taken for each process and the number of unique and duplicate hashes.

The identified duplicate documents are saved to an Excel file named 'duplicate_documents.xlsx'. This Excel file contains two sheets, 'Multiples' and 'Singles', each containing the corresponding duplicate documents.

## Error Handling

The script contains a try-except block to catch and print any errors that occur during the execution.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change. 

## License

[MIT](https://choosealicense.com/licenses/mit/)
