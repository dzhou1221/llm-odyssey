import os

import streamlit as st
from dotenv import load_dotenv
import psycopg2

from langchain import OpenAI, SQLDatabase, SQLDatabaseChain
from langchain.prompts import PromptTemplate

# streamlit_app.py

import streamlit as st

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True
      
# Connect to the PostgreSQL database
def connect_to_database():
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        user="admin",
        password="password",
        database="public_data"
    )
    return conn

# Execute a sample query
def execute_query(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ev_population LIMIT 5")
    rows = cursor.fetchall()
    cursor.close()
    return rows

# Streamlit app
def main():
  load_dotenv()
  
  # # Connect to the database
  # conn = connect_to_database()

  # # Execute query and display results
  # rows = execute_query(conn)
  # for row in rows:
  #     st.write(row)

  # # Close the database connection
  # conn.close()
  
  db = SQLDatabase.from_uri("postgresql://admin:password@localhost:5432/public_data")

  _DEFAULT_TEMPLATE = """Given an input question, first create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
  Use the following format:

  Question: "Question here"
  SQLQuery: "SQL Query to run"
  SQLResult: "Result of the SQLQuery"
  Answer: "Final answer here"

  Only use the following tables:

  {table_info}

  If someone asks for the table foobar, they really mean the employee table.

  Question: {input}"""
  PROMPT = PromptTemplate(
      input_variables=["input", "table_info", "dialect"], template=_DEFAULT_TEMPLATE
  )
  llm = OpenAI(temperature=0, verbose=True)
  db_chain = SQLDatabaseChain.from_llm(llm, 
                                       db, 
                                       prompt=PROMPT, 
                                       verbose=True, 
                                       use_query_checker=True, 
                                       return_intermediate_steps=True
                                    )
  
  query = st.text_input("Ask a question about the uploaded document:")
  generate_button = st.button("Gnerate Answer")
  
  if generate_button and query:
    with st.spinner("Generating answer ...."):
      res = db_chain(query)
      st.json(res)
      st.text(res['intermediate_steps'])


if __name__ == '__main__':
  
  if check_password():
      st.write("Here goes your normal Streamlit app...")
      main()