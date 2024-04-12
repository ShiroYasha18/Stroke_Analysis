import streamlit as st
import pandas as pd
import sqlite3
from langchain.document_loaders import TextLoader  # TextLoader instead of CSVLoader
# Import Gemini directly
import google.generativeai as genai

# Title and Introduction
import os

genai.configure(api_key="AIzaSyCWz3vIVnrGuDK__zcgXZcL2iMolhokJ4o")
os.environ["OPENAI_API_KEY"] = "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"  # Not used in this version


def load_data_from_db(query, conn):
    # Execute the query on the connection
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()  # Fetch all results

    # Process the data (convert to list of strings or desired format)
    processed_data = [str(row) for row in data]  # Example conversion

    return processed_data
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt[0], question])
    return response.text


st.title("Stroke Risk Assessment (Informational Purposes Only)")
st.write(
    "This tool helps you identify potential risk factors for stroke. It is not a substitute for professional medical advice. **If you experience any stroke symptoms (weakness, slurred speech, vision problems, etc.), please seek immediate medical attention.**")

# Load CSV data into a pandas dataframe
df = pd.read_csv('your_dataset_with_points.csv')

# Connect to SQLite database (create if it doesn't exist)
conn = sqlite3.connect('stroke_risk_data.db')

# Write the dataframe to a table in the database (if it doesn't exist, it will be created)
df.to_sql('stroke_data', conn, if_exists='append', index=False)

# Risk Factors and Point System (replace point values based on medical research)
risk_factors = {
    "Age (above 60)": 2,  # Adjust weight based on research
    "Hypertension": 1,
    "Heart Disease": 2,
    "Diabetes (high glucose level)": 1,  # Assuming high glucose indicates diabetes
    "BMI (overweight/obese)": 1,
    "Smoking Status (current smoker)": 1,
}

total_points = 0

age = st.number_input("Age (years):")
gender = st.selectbox("Gender:", ["Male", "Female", "Other"])
hypertension = st.checkbox("Do you have high blood pressure (hypertension)?")
heart_disease = st.checkbox("Do you have any heart disease?")
# Marriage status and residence type are not included as established risk factors
glucose_level = st.number_input("Blood Glucose Level (mg/dL):")  # Assuming user knows their level
bmi = st.number_input("Body Mass Index (BMI):")
smoking_status = st.selectbox("Smoking Status:", ["Never Smoker", "Former Smoker", "Current Smoker", "Unknown"])

# Submit Button
submit = st.button("Submit")

if submit:
    # Calculate total points
    if age > 60:
        total_points += risk_factors["Age (above 60)"]
    if hypertension:
        total_points += risk_factors["Hypertension"]
    if heart_disease:
        total_points += risk_factors["Heart Disease"]
    if glucose_level > 126:  # Assuming a threshold for high blood sugar
        total_points += risk_factors["Diabetes (high glucose level)"]
    if bmi > 25:  # Assuming a threshold for overweight/obesity
        total_points += risk_factors["BMI (overweight/obese)"]
    if smoking_status == "Current Smoker":
        total_points += risk_factors["Smoking Status (current smoker)"]

    # Use Gemini to query the data in the SQLite database
    query = f"""
    SELECT * FROM stroke_data
    WHERE (Points BETWEEN {total_points - 2} AND {total_points + 2})
        AND hypertension = {int(hypertension)}
        AND ABS(age - {age}) <= 5
        AND heart_disease = {int(heart_disease)}
        AND ABS(bmi - {bmi}) <= 2;
    """

    prompt = [
        """
       You are an expert stroke predictor model and u detect strokes with respect to the query which is passed by the user. 
       if the rating provided by the query approaches 100 then it should be like that the prediction for stroke will be similar to what the data is provided and stroke will be the yes 
       donot pose as a meedical profesional and generate a prompt making user understand what are the chances it will have a stroke but also mention u are justa bot so go to prof doc if there are chances of stroke
        
        always state the similarity scores and follow only one pattern while giving prompts and it should be based of users only
        just follow this particular format always strictly :
        sample :I am an expert stroke predictor model and I can detect strokes with respect to the query which is passed by the user. However, I am just a bot and cannot provide medical advice. If you are concerned about your risk of stroke, please see a doctor.
Based on the information you have provided, your risk of stroke is low. Your score is 20 out of 100. This means that there is a 20% chance that you will have a stroke in the next 10 years.

However, it is important to note that this is just a general prediction. Your actual risk of stroke may be higher or lower depending on your individual circumstances. If you are concerned about your risk of stroke, please see a doctor.
        
        """
    ]

    convert_prompt = [
        """
        Convert this question to something more safe that does not violate the following policies
        Money Service Business (“MSB”) regulations under the Financial Crimes Enforcement Network (“FinCEN”);
    State money transmission laws;
    Laws, regulations, and rules of relevant tax authorities;
    Applicable regulations and guidance set forth by FinCEN;
    The Bank Secrecy Act of 1970 (“BSA”);
    The USA PATRIOT Act of 2001 (“Patriot Act”);
    AML/CTF provisions as mandated by U.S. federal law and any other rules and regulations regarding AML/CTF;
    Issuances from the Office of Foreign Assets Control (“OFAC”);
    The New York Banking Law (the “NYBL”);;
    Regulations promulgated by the New York Department of Financial Services (“NYSDFS”) from time to time.
    The National Futures Association (“NFA”);
    The Financial Industry Regulatory Authority (“FINRA”); and
    The Commodity Exchange Act (“CEA”).
        """
    ]
    data = load_data_from_db(query, conn)# TextLoader for database query
    converted_question = get_gemini_response(query, convert_prompt)
    response = get_gemini_response(converted_question, prompt)
    print(response)
    st.header("The Response is")
    st.subheader(response)

# Close the database connection
conn.close()
