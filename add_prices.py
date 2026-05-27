import csv
import random

# File names
input_file = 'all_medicine databased.csv'
output_file = 'pharmacy_database_final.csv'

print("Opening CSV and generating prices... Please wait...")

# Open the original CSV to read, and a new CSV to write
with open(input_file, mode='r', encoding='utf-8') as infile:
    with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:

        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        # 1. Read the header row and add our new 'price' column
        header = next(reader)
        header.append('price')
        writer.writerow(header)

        # 2. Loop through all 250,000 rows
        for row in reader:
            # Generate a fake price between ₹15 and ₹850
            fake_price = random.randint(15, 850)

            # Add the price to the end of the row and save it
            row.append(fake_price)
            writer.writerow(row)

print(f"Done! Your new file '{output_file}' is ready for MySQL Workbench.")
