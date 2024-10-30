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
from pathlib import PurePath
 
# # Get the current date in YYYY-MM-DD format
# current_date = datetime.now().strftime('%Y-%m-%d')
# #Print the current date
# print("Current date: ", current_date)
 
# BUCKET_NAME='aws-fis-chaos-pipeline-execution'
# BUCKET_PREFIX=f'outputs/{current_date}'
# LOCATION_DIR="C:\\Data\\Chaos\\aws-lambda-chaos-library"
# client = boto3.client('s3')
 
# def download_files_from_s3(bucket_name, prefix_name):    
 
#     # Get back a list of all the objects that exists in bucket
#     # This includes folders and files
#     obj_list = client.list_objects_v2(
#         Bucket=bucket_name,
#         Prefix=prefix_name
#     )
#     #print(obj_list)
 
#     for obj in obj_list['Contents']:
#         response = client.get_object(
#             Bucket=bucket_name,
#             Key=obj['Key']
#         )
#         if 'application/x-directory' not in response['ContentType']:
#             save_file(LOCATION_DIR, obj['Key'], response['Body'])
 
# def save_file(location_dir_path, file_name, content):
#     file_dir_path = PurePath(location_dir_path, file_name)
#     dir_path = os.path.dirname(file_dir_path)
#     #Check if directory pagh exist, if not then create folder
#     if not os.path.exists(dir_path):
#         os.makedirs(dir_path)
#     with open(file_dir_path, 'wb') as f:
#         for chunk in content.iter_chunks(chunk_size=4096):
#             f.write(chunk)
 
# if __name__ == '__main__':
#     download_files_from_s3(BUCKET_NAME, BUCKET_PREFIX)
 
# # Specify the root directory to search for the file
# root_dir = f"C:\\Data\\Chaos\\aws-lambda-chaos-library\\outputs\\{current_date}" # You can update this path as per your requirement
# #root_dir = f'{BUCKET_NAME}/outputs/{current_date}'
# print("Root Directory:", root_dir) # You can update this path as per your requirement
# def merge_json_files(root_dir):
#     merged_data = []
#     #file_paths = glob.glob(os.path.join(root_dir, '**', '*.json'), recursive=True)
#     file_paths = glob.glob(root_dir + '/*.json')
#     for path in file_paths:
#         with open(path, 'r') as file:
#             data = json.load(file)
#             merged_data.append(data)
#     return merged_data
# # directory_path = "C://Data//Chaos//aws-lambda-chaos-library//Files"
# output_file = "formatted_data.json"
# account_id = output_file.split("_")[0]
# merged_data = merge_json_files(root_dir)
# with open(output_file, 'w') as outfile:
#     json.dump(merged_data, outfile)
# print(f"Found JSON file at: {merged_data}")
 
# Load the JSON data from the files
with open("data.json", "r") as result_file:
    result_data = json.load(result_file)
# Create a dataframe for result.json data
result_df = pd.DataFrame(result_data)
 
# Group the data by "Services" and "Experiment" columns
grouped_data = result_df.groupby(['Application', 'Services', 'Experiment', 'Results']).size().reset_index(name='count')
 
# Iterate over each unique service
for application in result_df['Application'].unique():
    # Filter data for the current application
    application_data = grouped_data[grouped_data['Application'] == application]
 
    # Create labels and sizes for the pie chart
    labels = application_data['Experiment'].tolist()
    sizes = application_data['count'].tolist()
    results = application_data['Results'].tolist()
 
    # Create colors for the pie chart based on "PASS" or "FAIL" status
    colors = ['mediumseagreen' if result == 'PASS' else 'tomato' for result in results]
 
    # Create a pie chart
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, colors=colors, startangle=90, wedgeprops={'linewidth': 2, 'edgecolor': 'white'})
 
    # Add title with service name in bold and increased font size
    ax.set_title(f'{application}', weight='bold', fontsize=15)
 
    # Generate legend
    pass_patch = Patch(color='mediumseagreen', label='Pass')
    fail_patch = Patch(color='tomato', label='Fail')
    plt.legend(handles=[pass_patch, fail_patch], loc='best')
 
    # Save the pie chart
    plt.savefig(f'pie_chart_{application}.png')
    plt.close()
 
with open("C:\\Data\\Chaos\\aws-lambda-chaos-library\\params\\dev\\shop\\ITSSREBTSP\\l3experiment.json", "r") as sre_file:
    sre_data = json.load(sre_file)
# Create a dataframe for SRE CHAOS SUMMARY REPORT.json data
sre_df = pd.DataFrame(sre_data)
 
# Generate PDF
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'SRE CHAOS SUMMARY REPORT', 0, 1, 'C')
        self.ln(10)
 
    def add_table(self, sre_data):
        self.set_font('Arial', 'B', 12)
        # Set table columns (Key-Value like structure)
        for row in sre_data:
            self.cell(90, 10, row["APP_NAME"], 1, 0, 'L')
            self.set_font('Arial', '', 12)
            self.cell(90, 10, row["APP_NAME"], 1, 1, 'L')
            self.set_font('Arial', 'B', 12)
 
    def add_results_heading(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Chaos Test Results:', 0, 1)
        self.ln(10)
 
    def add_pie_chart(self):
        self.image(f'pie_chart_{application}.png', x=50, y=None, w=70, h=70)
   
    def add_paragraph(self):
        self.ref_link = 'https://zap.delta.com/ccoe/docs/operations_process_and_tooling/chaos-engineering/overview/'
        #self.ref_run.italic = True
        #self.ref_run.font.size = Pt(14) # Increase font size for the reference section
        #self.ref_run.font.color.rgb = RGBColor(0, 0, 255) # Blue color  
 
# Create PDF
pdf = PDF()
 
# Add a page and the report title
pdf.add_page()
 
# Add the SRE Chaos Summary table
pdf.add_table(sre_data)
 
# Add the results section heading and pie chart
pdf.add_page()  # Create a new page for the results
pdf.add_results_heading()
pdf.add_pie_chart()
pdf.add_paragraph()
 
# Save the PDF
#pdf_output_path = f'./reports/{current_date}/SRE-CHAOS-SUMMARY-REPORT-APPNAME.pdf'
pdf_output_path = 'SRE-CHAOS-SUMMARY-REPORT-APPNAME.pdf'
pdf.output(pdf_output_path)
 
# with open(pdf_output_path, 'rb') as file_data:
#     client.put_object(
#             Bucket=BUCKET_NAME,
#             Key=pdf_output_path,
#             Body=file_data,
#             ContentType='application/pdf'
#     )
print(f"PDF report saved as {pdf_output_path}")
# command = f"echo {pdf_output_path} > reports/SRE-CHAOS-SUMMARY-REPORT-APPNAME.pdf"
# process = subprocess.run(command, shell=True, capture_output=True, text=True)
   
# Output and errors
# print("STDOUT:", process.stdout)
# print("STDERR:", process.stderr)
