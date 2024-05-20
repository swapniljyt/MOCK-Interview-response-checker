import os
import PyPDF2
import json
import re
import warnings
import pandas as pd
import traceback

def read_file(file):
    if file.name.endswith(".pdf"):
        try:
            pdf_reader=PyPDF2.PdfFileReader(file)
            return "".join(page.extract_text() for page in pdf_reader.pages)
        except Exception as e:
            print (e)
            raise Exception ("error reading PDF file") from e
    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")

    else:
        raise Exception(
            "unsupported file format, only pdf and txt are supported"
        )

def get_table_data(quiz_str):
    try:
        clean_output = quiz_str.replace('```json\n', '').replace('\n```', '')
        quiz_list = json.loads(clean_output)
        quiz_table_data = []
        
        for value in quiz_list:
            question_data = {
                "Question": value["Question"],
                "Type": value.get("Type", "Theory"),
                "Response": value.get("Response", "Attempted"),
                "Syntactic Score": value.get("Syntactic Score", None),
                "Semantic Score": value.get("Semantic Score", None),
                "Contextual Score": value.get("Contextual Score", None),
                "FirstStep Score": value.get("FirstStep Score", None),
                "Middle Step Score": value.get("Middle Step Score", None),
                "Last Step Score": value.get("Last Step Score", None),
                "Total Score": value.get("Total Score", None)
            }
            quiz_table_data.append(question_data)
        
        return quiz_table_data
    
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None
    except KeyError as e:
        print(f"Missing key in JSON data: {e}")
        return None

def create_dictionary(content):
    # Remove numeric indices before "Question" and "Answer" words, preserving the colon
    content_without_indices = re.sub(r'(\b\d+\.\s*Question:)', 'Question:', content)
    content_without_indices = re.sub(r'(\b\d+\.\s*Answer:)', 'Answer:', content_without_indices)

    # Tokenize and print each word with punctuation
    words = re.findall(r'\b\w+\b|[.,{};!?:^/−+()=>]', content_without_indices)

    sentence = ""
    my_dic = {}
    n = 0

    for word in words:
        if word == "Answer" and words[n + 1] == ":":
            key = sentence.strip()
            sentence = ""
        if word == "Question" and n > 4 and words[n + 1] == ":":
            my_dic[key] = sentence.strip()
            sentence = ""
        sentence += word
        sentence += " "
        n += 1

    # Check for the last question-answer pair
    if sentence.strip() and key:
        my_dic[key] = sentence.strip()

    return my_dic