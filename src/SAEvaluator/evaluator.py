import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv

from src.SAEvaluator.utils import read_file,get_table_data
from src.SAEvaluator.logger import logging

# importing ncessary modules

from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain

load_dotenv()

OPENAI_KEY=os.getenv("KEY")
llm=ChatOpenAI(openai_api_key=OPENAI_KEY,model_name="gpt-4-turbo",temperature=0.5)

TEMPLATE_gpt = """
You are an expert examiner tasked with evaluating a student's response sheet against the answer key:

The student's response sheet is a Python dictionary represented as {student_dic}, and the answer sheet is {eval_dic}. Each dictionary key corresponds to a question, and its value is the respective answer.

First, calculate the total number of questions by counting the keys in the dictionary.

For each question in the student's response dictionary:
- If it's a THEORY type:
  - **Syntactic Score (0 to 100):** Evaluate grammatical structure and arrangement.
  - **Semantic Score (0 to 100):** Assess relatedness in meaning and conceptual understanding.
  - **Contextual Score (0 to 100):** Consider alignment with specific context or scenario.

- If it's a NUMERICAL type:
  - **First Step Score (0 to 100):** Evaluate correctness of the response's foundation and application of formulas.
  - **Middle Step Score (0 to 100):** Assess intermediate steps towards the final answer.
  - **Final Step Score (0 to 100):** Check if the final response aligns with the answer key.
If you get null value for any particular key then the question response is Not Attempted
Output the evaluation scores in a tabular format like {tabular_response}, ensuring to update each metric strictly for all questions. 
Avoid generating extra tokens to ensure a concise and efficient response.
"""

prompt_template_name=PromptTemplate(
    input_variables=["student_dic","eval_dic","RESPONSE"],
    template=TEMPLATE_gpt
)

first_chain = LLMChain(llm=llm, prompt=prompt_template_name, output_key="score_1", verbose=True)   

Review_template="""Remove and clean any extra tokens generated before and after the specified format. 
Provide only the clean output inside the braces [] for {score_1}. 
This is a student's marksheet that will be converted into a data frame.
 If it contains extra tokens, it will cause an error during the conversion."""



review_template_name=PromptTemplate(
    input_variables=["score_1","tabular_response"],
    template=Review_template
)

review_chain = LLMChain(llm=llm, prompt=review_template_name, output_key="Final_score", verbose=True)

score_structure = SequentialChain(
                                chains=[first_chain ,review_chain],
                                input_variables=["student_dic","eval_dic","tabular_response"],
                                output_variables=["score_1","Final_score"],
                                verbose=True
                            )


                                      
