import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
from  src.SAEvaluator.utils import read_file,get_table_data,create_dictionary
import streamlit as st
from langchain.callbacks import get_openai_callback
from  src.SAEvaluator.evaluator import score_structure
from  src.SAEvaluator.logger import logging

#loading jason file
with open(r'C:\Users\Swapnil Jyot\SAE_system\Response.json', 'r') as file:
    tabular_response = json.load(file)
 

#creating a title
st.title("SUBJECTIVE ANSWERSHEET EVALUATION SYSTEM")

#create a form using st.form
with st.form("user_inputs"):
    # file
    Student_file=st.file_uploader("Upload Student Response")
    Answer_file=st.file_uploader("Upload Answer Key")
    button = st.form_submit_button("Create MCQs")


    if (button and Student_file is not None )and (Answer_file is not None) :
            with st.spinner("Loading..."):
                try:
                    Student_file= read_file(Student_file) 
                    Answer_file  = read_file(Answer_file )
                    std_dic=create_dictionary(Student_file)
                    eval_dic=create_dictionary(Answer_file)
                    # call the llm while getting the token metrics
                    with get_openai_callback() as cb:
                        response=score_structure(
                            {
                                "student_dic": std_dic,
                                "eval_dic": eval_dic,
                                "tabular_response": json.dumps(tabular_response) 
                            }
                        )
                except Exception as e:
                    traceback.print_exception(type(e), e, e.__traceback__)
                    st.error("Error")

                else:
                    print (f"Total Tokens: {cb.total_tokens}")
                    print (f"Prompt Tokens: {cb.prompt_tokens}")    
                    print (f"Completion Tokens: {cb.completion_tokens}")
                    print (f"Total Cost: {cb.total_cost}")
                    if isinstance(response, dict):
                        # extract the quiz data from the response
                        quiz = response.get("Final_score", None)
                        if quiz is not None:
                            table_data=get_table_data(quiz)
                            if table_data is not None:
                                df = pd.DataFrame(table_data)
                                df.index=df.index+1
                                st.table(df)
                                
                            else:
                                st.error("Error in the table data")
                    else:
                        st.write(response)