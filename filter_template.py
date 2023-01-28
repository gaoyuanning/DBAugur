# Filter the templates in "Combined_Templates" directory whose total workload is too small
import shutil
import csv
import os

cnt = 0
input_path = 'Combined_Templates/'
output_path = 'Combined_Templates_Compact/'

if os.path.exists(output_path):
    shutil.rmtree(output_path)
os.makedirs(output_path)

for csv_file in sorted(os.listdir(input_path)):
    with open(input_path + "/" + csv_file, 'r') as f:
        reader = csv.reader(f)
        queries, template = next(reader)

        if int(queries) > 1000:
            shutil.copyfile(input_path + "/" + csv_file, output_path + "/" + csv_file)
            cnt += 1

print(cnt)