import pandas as pd
import json
import matplotlib.pyplot as plt
from fpdf import FPDF
import subprocess
from matplotlib.patches import Patch
import re
import glob
import os
import boto3
from datetime import datetime
 
# Get the current date in YYYY-MM-DD format
current_date = datetime.now().strftime('%Y-%m-%d')
#Print the current date
print("Current date: ", current_date)
 
BUCKET_NAME='aws-fis-chaos-pipeline-execution'
#BUCKET_PREFIX='outputs/2024-10-17/'
BUCKET_PREFIX=""
#LOCATION_DIR = "./result/"
LOCATION_DIR="C:\\Data\\Chaos\\aws-lambda-chaos-library"
 
def download_files_from_s3(bucket_name, prefix_name):
    client = boto3.client('s3')
 
    # Get back a list of all the objects that exists in bucket
    # This includes folders and files
    obj_list = client.list_objects_v2(
        Bucket=bucket_name,
        Prefix=prefix_name
    )
    print(obj_list)
 
    for obj in obj_list['Contents']:
        response = client.get_object(
            Bucket=bucket_name,
            key=obj['Key']
        )
 
        if 'application/x-directory' not in response['ContentType']:
            save_file(LOCATION_DIR, obj['Key'], response['Body'])
 
def save_file(location_dir_path, file_anme, content):
    file_dir_path = PursePath(location_dir_path, file_name)
    dir_path = os.path.dirname(file_dir_path)
    #Check if directory pagh exist, if not then create folder
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    with open(file_dir_path, 'wb') as f:
        for chunk in content.iter_chunks(chunk_zise=4096):
            f.write(chunk)
 
if __name__ == '__main__':
    download_files_from_s3(BUCKET_NAME, BUCKET_PREFIX)
 
# # Create S3 client
# client = boto3.client('s3')
# response = client.list_objects_v2(Bucket=BUCKET_NAME,
#     Prefix=)
# print(response)
 
# # Iterate over every object in bucket
# for obj in response['Contents']:
#     key = obj['Key']
#     file_name = key.split('/')[-1]
#     print(key)
#     print(file_name)
 
# # Get JSON file content
# s3_response = client.get_object(Bucket=BUCKET_NAME, Key=key)
# result_data = json.load(s3_response)
# # Create a dataframe for result.json data
# result_df = pd.DataFrame(result_data)
 
# with open("./scripts/Report/SRE CHAOS SUMMARY REPORT.json", "r") as sre_file:
#     sre_data = json.load(sre_file)
# # Create a dataframe for SRE CHAOS SUMMARY REPORT.json data
# sre_df = pd.DataFrame(sre_data)
 
# # Generate Pie Chart from the 'Results' field in result.json
# result_counts = result_df.groupby('Experiment')['Results'].count()
# plt.figure(figsize=(6, 6))
# plt.pie(result_counts, labels=result_counts.index, autopct='%1.1f%%', colors=['#ff6666', '#66b3ff', '#99ff99'], startangle=90)
# plt.title('WEB', fontweight='bold')
 
# # Position the legend to the upper right outside the pie chart
# plt.legend(result_counts.index, title="Experiment", loc="upper left", bbox_to_anchor=(1, 1))
 
# # Save the pie chart as an image
# plt.savefig('./scripts/Report/pie_chart.png', bbox_inches="tight")
# plt.close()
 
# # Generate PDF
# class PDF(FPDF):
#     def header(self):
#         self.set_font('Arial', 'B', 16)
#         self.cell(0, 10, 'SRE CHAOS SUMMARY REPORT', 0, 1, 'C')
#         self.ln(10)
 
#     def add_table(self, sre_data):
#         self.set_font('Arial', 'B', 12)
#         # Set table columns (Key-Value like structure)
#         for row in sre_data:
#             self.cell(90, 10, row["Requirments"], 1, 0, 'L')
#             self.set_font('Arial', '', 12)
#             self.cell(90, 10, row["Details"], 1, 1, 'L')
#             self.set_font('Arial', 'B', 12)
 
#     def add_results_heading(self):
#         self.set_font('Arial', 'B', 12)
#         self.cell(0, 10, 'Chaos Test Results:', 0, 1)
#         self.ln(10)
 
#     def add_pie_chart(self):
#         self.image('./scripts/Report/pie_chart.png', x=50, y=None, w=110, h=110)
 
# # Create PDF
# pdf = PDF()
 
# # Add a page and the report title
# pdf.add_page()
 
# # Add the SRE Chaos Summary table
# pdf.add_table(sre_data)
 
# # Add the results section heading and pie chart
# pdf.add_page()  # Create a new page for the results
# pdf.add_results_heading()
# pdf.add_pie_chart()
 
# # Save the PDF
# pdf_output_path = './scripts/Report/SRE-CHAOS-SUMMARY-REPORT-APPNAME.pdf'
# pdf.output(pdf_output_path)
 
# print(f"PDF report saved as {pdf_output_path}")
# command = f"echo {pdf_output_path} > report/SRE-CHAOS-SUMMARY-REPORT-APPNAME.pdf"
# process = subprocess.run(command, shell=True, capture_output=True, text=True)
   
# # Output and errors
# print("STDOUT:", process.stdout)
# print("STDERR:", process.stderr)
 
# # Bucket = 'aws-fis-chaos-pipeline-execution',
# # Prefix = 'outputs/2024-10-17/'
 
# # # Use glob to search for the .json file recursively
# # json_file = glob.glob(os.path.join(Prefix, '**', '*.json'), recursive=True)
# # # If at least one JSON file is found, proceed
 
# # if json_file:
# #    # Assuming you want the first JSON file found
# #    json_file_path = key[0]
# #    print(f"Found JSON file at: {json_file_path}")
 
 
 
has context menu
