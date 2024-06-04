from flask import Flask, request, jsonify

from flask_cors import CORS
import pytesseract
from pdf2image import convert_from_path
import google.generativeai as genai

import ast
import mysql.connector
from mysql.connector import Error
from flask import Flask, jsonify, render_template_string
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from flask import Flask, render_template, request, jsonify
import os
import mysql.connector
import google.generativeai as genai
from mysql.connector import Error

app = Flask(__name__)
CORS(app)
matplotlib.use('agg')
# Database configuration
DB_HOST = 'localhost'
DB_NAME = 'dummy_database'
DB_USER = 'qti'
DB_PASS = 'qti123'



def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        if conn.is_connected():
            print("Connection to the database established successfully")
            return conn
    except Error as e:
        print(f"Error: {e}")
        return None







# Configure the Google Generative AI API
genai.configure(api_key='AIzaSyBLtQQELnXSqj9v4ULk7IToH9RtaNCwOSc')  # Replace with your actual API key
model = genai.GenerativeModel('gemini-pro')



poppler_path = r"C:\Program Files (x86)\poppler-0.68.0\bin"

# Ensure you have the correct path to the tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_patient_data_from_pdf(pdf_file, poppler_path=None):
    
    # Convert PDF to images
    pages = convert_from_path(pdf_file, 300, poppler_path=poppler_path)  # Adjust the DPI as needed

    # Initialize an empty string to store the extracted text
    extracted_text = ""

    # Iterate through each page image
    for page in pages:
        # Use pytesseract to perform OCR on the image and extract text
        text = pytesseract.image_to_string(page)

        # Append the extracted text to the result
        extracted_text += text + "\n\n"  # Add extra newline for page separation

    return extracted_text

def call_google_gemini_gen_api(extracted_text):
    """
    Call the Google Gemini Generative Model API to process extracted text.
    """
    # Define the medical report schema
    medical_report_schema = {"id":"medical_report","description":"Extracted medical information from a given report.","attributes":[{"id":"patient_name","value":"null"},{"id":"patient_age","value":"null"},{"id":"patient_gender","value":"null"},{"id":"test_date","value":"null"},{"id":"tsh_level","value":"null"},{"id":"t3_level","value":"null"},{"id":"t4_level","value":"null"},{"id":"free_t3_level","value":"null"},{"id":"free_t4_level","value":"null"},{"id":"tpoab_level","value":"null"},{"id":"tgab_level","value":"null"},{"id":"interpretation","value":"null"},{"id":"recommendations","value":"null"},{"id":"additional_notes","value":"null"},{"id":"hospital_name","value":"null"},{"id":"hospital_contact","value":"null"},{"id":"Vitamin B12","value":"null"},{"id":"Calcium","value":"null"},{"id":"Glycated Hemoglobin","value":"null"},{"id":"Fasting Plasma Glucose","value":"null"}]}

    # Create the prompt for the API
    prompt = f"Task: Medical Information Extraction , Description:  You're tasked with developing a system to extract medical information from text obtained by parsing a medical report PDF file. The extracted information needs to be filled into a provided JSON schema{medical_report_schema} please ensure to keep id and values in double inverted comma. \nInput: \n Here is a string representing text extracted from a medical report PDF:\n {extracted_text} \n The text will contain sections such as patient name, patient age, patient gender, test date, TSH level, T3 level, T4 level, free T3 level, free T4 level, TPOAb level, TGAb level, interpretation, recommendations, additional notes, hospital name, hospital contact, vitamin B12, calcium, glycated hemoglobin, fasting plasma glucose.\n\n Output: \n Fill in the schema attributes with the extracted information according to your analysis. If information is available, fill in the value; otherwise, leave it as null. \n {medical_report_schema}. Return the output as JSON."

    # Generate content using the model
    response = model.generate_content(prompt)
    return response.text

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Visualize Thyroid Profile</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f9;
                margin: 0;
                padding: 0;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
            }
            h1 {
                color: #333;
                margin-bottom: 20px;
                font-size: 2em;
                text-align: center;
            }
            .plot-container {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 10px;
                width: 90%;
                max-width: 800px;
                height: auto;
                margin-bottom: 20px;
                padding: 10px;
                border: 1px solid #ccc;
                background-color: #fff;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }
            .plot {
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 200px;
                border: 1px solid #ccc;
                background-color: #fafafa;
            }
            .plot img {
                max-width: 100%;
                height: auto;
            }
            button {
                background-color: #4CAF50;
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                transition: background-color 0.3s;
            }
            button:hover {
                background-color: #45a049;
            }
        </style>
    </head>
    <body>
        <h1>Patient Report</h1>
        <div class="plot-container">
            <div id="plot1" class="plot"><p>No plot to display</p></div>
            <div id="plot2" class="plot"><p>No plot to display</p></div>
        </div>
        <button onclick="fetchData()">Fetch Data and Plot</button>
        <script>
            function fetchData() {
                fetch('/data')
                    .then(response => response.json())
                    .then(data => {
                        ['plot1', 'plot2'].forEach((plotId, index) => {
                            const img = document.createElement('img');
                            img.src = 'data:image/png;base64,' + data[index];
                            img.style.maxWidth = '100%';
                            img.style.height = 'auto';
                            const plotDiv = document.getElementById(plotId);
                            plotDiv.innerHTML = ''; // Clear previous plot
                            plotDiv.appendChild(img);
                        });
                    })
                    .catch(error => console.error('Error fetching data:', error));
            }
        </script>
    </body>
    </html>
    '''

@app.route('/extract-pdf-text', methods=['POST'])
def extract_pdf_text():
    
    # if 'file' not in request.files:
    #     return jsonify({"error": "No PDF file provided"}), 400

    # file = request.files['file']
    # if file.filename == '':
    #     return jsonify({"error": "No selected file"}), 400

    # # Ensure the temporary directory exists
    # temp_dir = os.path.join(os.getcwd(), 'temp')
    # os.makedirs(temp_dir, exist_ok=True)
    data = request.get_json()
    filename = data.get('filename', '')
    basepath = r"E:\Qti\qti\medicare\uploads"
    temp_file_path = basepath + "/" + filename

    try:
        extracted_text = extract_patient_data_from_pdf(temp_file_path, poppler_path)
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    # finally:
    #     # Clean up the temporary file
    #     os.remove(temp_file_path)

    try:
        api_response = call_google_gemini_gen_api(extracted_text)
        print(api_response)
        return ast.literal_eval(api_response)
        
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    
@app.route('/reports', methods=['GET'])
def get_all_reports():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM report")
        reports = cursor.fetchall()

        cursor.close()
        conn.close()

        if not reports:
            return jsonify({"error": "No reports found"}), 404

        return jsonify(reports)

    except Exception as e:
        app.logger.error(f"An error occurred: {e}")
        return jsonify({"error": "An internal server error occurred"}), 500
    
    
    
    
@app.route('/query', methods=['POST'])
def handle_query():
    try:
        data = request.json
        user_query = data.get('query')

        if not user_query:
            return jsonify({"error": "Query is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM report")
        reports = cursor.fetchall()

        cursor.close()
        conn.close()

        if not reports:
            return jsonify({"error": "No reports found"}), 404

        # Construct user_data
        user_data = "\n".join(
    f"""
    Test Date: {report['TestDate']}
    T3 Level: {report['t3_level (ng/mL)']}
    Biological ref interval(t3_level): {report['BIOLOGICAL REFERENCE INTERVAL(t3_level)']}
    TSH Level: {report['tsh_level (µIU/mL)']}
    Biological ref interval(tsh_level): {report['Biological reference interval(tsh_level)']}
    T4 Level: {report['t4_level(µg/dL)']}
    Biological ref interval(T4_level): {report['BIOLOGICAL REFERENCE INTERVAL(T4_level)']}
    Free T3 Level: {report['free_t3_level(pg/mL)']}
    Free T4 Level: {report['free_t4_level(pg/mL)']}
    TPOAb Level: {report['tpoab_level(IU/mL)']}
    VITAMIN_B12: {report['Vitamin_B12(pg/mL)']}
    Biological ref interval(Vitamin_B12): {report['BIOLOGICAL REFERENCE INTERVAL(Vitamin_B12)']}
    CALCIUM: {report['Calcium(mg/Dl)']}
    Biological ref interval(Calcium): {report['BIOLOGICAL REFERENCE INTERVAL(Calcium)']}
    Glycated Hemoglobin: {report['Glycated_haemoglobin(%)']}
    Biological ref interval(glycated haemoglobin): {report['BIOLOGICAL REFERENCE INTERVAL(glycated haemoglobin)']}
    Interpretation: {report['interpretation']}
    Recommendations: {report['recommendations']}
    Additional Notes: {report['additional_notes']}
    """
    for report in reports
)


        # Construct prompt for Gemini Pro
        prompt = f"""
        You are a health assistant specializing in analyzing  medical profile data. Your role is to act as a medical analyst, providing detailed insights, interpretations, and personalized recommendations based on the user's medical profile data. Follow these steps to ensure a comprehensive and accurate response:

        Review the provided medical profile data:

        Test Date
        T3 Level
        Biological ref interval(t3_level)
        TSH Level
        Biological ref interval(tsh_level)
        T4 Level
        Biological ref interval(T4_level)
        Free T3 Level
        Free T4 Level
        TPOAb Level
        VITAMIN_B12
        Biological ref interval(Vitamin_B12)
        CALCIUM
        Biological ref interval(Calcium)
        Glycated Hemoglobin
        Biological ref interval(glycated haemoglobin)
        Fasting plasma glucose
        Biological ref interval(Fasting plasma glucose)
        Interpretation
        Recommendations
        Additional Notes

        Interpret each parameter in the context of  medical health, explaining what typical  levels might indicate.

        Analyze the user's question in relation to their data, providing specific insights based on the values given. Take the user query and give an answer relevant only to the question asked. Limit the answer to 30-50 words.

        Offer personalized recommendations:

        Suggest potential lifestyle or dietary changes.
        Advise on possible medical treatments or follow-ups.
        Highlight any concerning trends or values that should be discussed with a healthcare professional.
        Identify any missing information that might be crucial for a complete analysis and guide the user on what additional data might be needed.

        Encourage professional consultation where appropriate, emphasizing the importance of professional healthcare advice for diagnosis and treatment.

        User Query:
        {user_query}

        User medical profile Data:
        {user_data}

        Generate a comprehensive answer based on the above data.
        """
        # Call the Generative AI model to generate a response
        response = model.generate_content(prompt)
        answer = response.text.strip()

        return jsonify({"answer": answer})

    except Exception as e:
        app.logger.error(f"An error occurred: {e}")
        return jsonify({"error": "An internal server error occurred"}), 500
    
    
    
    
    
    
    
    

    
    
    
@app.route('/data', methods=['GET'])
def get_data():
    user_id = 1  # Default user ID
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Unable to connect to the database"}), 500
    
    try:
        cursor = conn.cursor()
        query = '''
            SELECT TestDate, `Glycated_haemoglobin(%)`, `Fasting_plasma_glucose(mg/dL)`
            FROM report 
            WHERE `User_id` = %s;
        '''
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    
    if not rows:
        return jsonify({"error": "No data found for the specified user-id"}), 404
    
    columns = ['TestDate', 'Glycated_haemoglobin(%)','Fasting_plasma_glucose(mg/dL)']
    df = pd.DataFrame(rows, columns=columns)
    df['TestDate'] = pd.to_datetime(df['TestDate'])
    
    plot_images = []
    for col in columns[1:]:
        buffer = BytesIO()
        plt.figure(figsize=(10, 6))
        plt.plot(df['TestDate'], df[col], label=col, marker='o', linestyle='-', color='b', markersize=8, markerfacecolor='red')
        plt.xlabel('Test Date')
        plt.ylabel(col)
        plt.title(f'Test Date vs {col}')
        plt.xticks(rotation=45)
        plt.legend()
        
        # Add value labels to the markers
        for i, txt in enumerate(df[col]):
            plt.annotate(f'{txt:.2f}', (df['TestDate'].iloc[i], df[col].iloc[i]), textcoords="offset points", xytext=(0,10), ha='center')

        # Add the text box for Fasting Plasma Glucose graph
        if col == 'Glycated_haemoglobin(%)':
            plt.text(0.95, 0.5, 
                     "Non Diabetic             : < 5.6\nPre - Diabetic Range : 5.7 - 6.4\nDiabetic Range          : >= 6.5",
                     fontsize=12, bbox=dict(facecolor='white', alpha=0.5), transform=plt.gca().transAxes, verticalalignment='top', horizontalalignment='right')

        # Add the text box for Glycated Haemoglobin graph
        elif col == 'Fasting_plasma_glucose(mg/dL)':
            plt.text(0.95, 0.5, 
                     "Normal   : 70 - 100\nImpaired Fasting Glucose  : 101 - 125\nDiabetes : >=126",
                     fontsize=12, bbox=dict(facecolor='white', alpha=0.5), transform=plt.gca().transAxes, verticalalignment='top', horizontalalignment='right')

        plt.tight_layout()
        plt.savefig(buffer, format='png')
        plt.close()
        buffer.seek(0)
        plot_images.append(base64.b64encode(buffer.getvalue()).decode('utf-8'))
    
    return jsonify(plot_images)



if __name__ == '__main__':
    app.run(debug=True)