import os
import csv
from openpyxl import Workbook

# ====== CONFIGURATION ======
experiments_folders = [
    r"./experiment_results/concurrent", 
    r"./experiment_results/countThenMove",
]
output_excel = "results.xlsx"   # Output Excel file
header =  "threads,hash bits,mean[ms],run1[ms],run2[ms],run3[ms],run4[ms],run5[ms],run6[ms],run7[ms],run8[ms],run9[ms],run10[ms]" 
# ============================

def csvs_to_excel(output_file):
    # Create a new Excel workbook
    wb = Workbook()
    
    # Remove the default sheet created by openpyxl
    default_sheet = wb.active
    wb.remove(default_sheet)

    # Loop through all CSV files in the directory
    for experiment in experiments_folders:
        ws = wb.create_sheet(title=experiment.split("/")[-1])
        ws.append(header.split(","))
        for filename in os.listdir(experiment):
            if filename.lower().endswith(".csv"):
                file_path = os.path.join(experiment, filename)

                # Read CSV and write to Excel
                with open(file_path, newline='', encoding="utf-8") as csvfile:
                    reader = csv.reader(csvfile)
                    for i, row in enumerate(reader):
                        if i == 0:
                            continue
                        else:
                            ws.append(list(map(int, row)))

                print(f"Added: {filename}")

    # Save the workbook
    wb.save(output_file)
    print(f"\nExcel file created: {output_file}")

if __name__ == "__main__":
    csvs_to_excel(output_excel)