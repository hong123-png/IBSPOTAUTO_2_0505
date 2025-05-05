import csv
import os

def read_csv_data(filename, start_row, end_row, column):
    result = []
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'UpLoadData', filename)
    with open(csv_path, 'r', encoding='utf-8', errors='ignore') as file:
        reader = csv.reader(file)
        for i, row in enumerate(reader):
            if start_row <= i <= end_row:
                selected_values = row[column]
                result.append(selected_values)
    return result

def get_g2lb(item_weight):
    return round(float(item_weight) * 0.0022, 2)

def get_cm2inch(cm):
    return round(float(cm) * 0.394, 2)
