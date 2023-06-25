from langchain import OpenAI
from langchain.agents import create_pandas_dataframe_agent
import pandas as pd
from dotenv import load_dotenv
import json
import streamlit as st
import sqlite3
#import altair as alt
#import seaborn as sns
from showallthedb import showallgraph
conn = sqlite3.connect('news_data.db')
cursor = conn.cursor()
st.set_page_config(page_title="👨‍💻 Talk with your CSV",layout = 'wide')
load_dotenv()


# Render the custom CSS styles
st.markdown(
    """
    <style>
    /* Add custom CSS styles here */
    body {
        margin: 0;
        padding: 0;
    }
    
    .full-width {
        width: 100%;
    }
    
    .stApp {
        padding-top: 0 !important;
    }
    
    .stTab {
        margin-top: 0 !important;
    }
    
    </style>
    """,
    unsafe_allow_html=True
)


def csv_tool(filename : str):

    df = pd.read_csv(filename)
    return create_pandas_dataframe_agent(OpenAI(temperature=0), df, verbose=True)

def ask_agent(agent, query):
    """
    Query an agent and return the response as a string.

    Args:
        agent: The agent to query.
        query: The query to ask the agent.

    Returns:
        The response from the agent as a string.
    """
    # Prepare the prompt with query guidelines and formatting
    prompt = (
        """
        Let's decode the way to respond to the queries. The responses depend on the type of information requested in the query. 

        1. If the query requires a table, format your answer like this:
           {"table": {"columns": ["column1", "column2", ...], "data": [[value1, value2, ...], [value1, value2, ...], ...]}}

        2. For a bar chart, respond like this:
           {"bar": {"columns": ["A", "B", "C", ...], "data": [25, 24, 10, ...]}}

        3. If a line chart is more appropriate, your reply should look like this:
           {"line": {"columns": ["A", "B", "C", ...], "data": [25, 24, 10, ...]}}

        Note: We only accommodate two types of charts: "bar" and "line".

        4. For a plain question that doesn't need a chart or table, your response should be:
           {"answer": "Your answer goes here"}

        For example:
           {"answer": "The Product with the highest Orders is '15143Exfo'"}

        5. If the answer is not known or available, respond with:
           {"answer": "I do not know."}

        Return all output as a string. Remember to encase all strings in the "columns" list and data list in double quotes. 
        For example: {"columns": ["Products", "Orders"], "data": [["51993Masc", 191], ["49631Foun", 152]]}

        Now, let's tackle the query step by step. Here's the query for you to work on: 
        """
        + query
    )

    # Run the prompt through the agent and capture the response.
    response = agent.run(prompt)

    # Return the response converted to a string.
    return str(response)

def decode_response(response: str) -> dict:
    """This function converts the string response from the model to a dictionary object.

    Args:
        response (str): response from the model

    Returns:
        dict: dictionary with response data
    """
    response = response.replace('`','"')
    response = response.replace("'",'"')
    print(response)
    return json.loads(response)

def write_answer(response_dict: dict):
    """
    Write a response from an agent to a Streamlit app.

    Args:
        response_dict: The response from the agent.

    Returns:
        None.
    """

    # Check if the response is an answer.
    if "answer" in response_dict:
        st.write(response_dict["answer"])

    # Check if the response is a bar chart.
    # Check if the response is a bar chart.
    if "bar" in response_dict:
        data = response_dict["bar"]
        try:
            df_data = {
                    col: [x[i] if isinstance(x, list) else x for x in data['data']]
                    for i, col in enumerate(data['columns'])
                }       
            df = pd.DataFrame(df_data)
            print(df)
            #df.set_index("Products", inplace=True)
            # sns.set_palette("gray")
            st.bar_chart(df)
            #chart = alt.Chart(df).mark_bar(color='gray')
            #st.altair_chart(chart)


        except ValueError:
            print(f"Couldn't create DataFrame from data: {data}")

# Check if the response is a line chart.
    if "line" in response_dict:
        data = response_dict["line"]
        try:
            df_data = {col: [x[i] for x in data['data']] for i, col in enumerate(data['columns'])}
            df = pd.DataFrame(df_data)
            
            st.line_chart(df)
        except ValueError:
            print(f"Couldn't create DataFrame from data: {data}")


    # Check if the response is a table.
    if "table" in response_dict:
        data = response_dict["table"]
        df = pd.DataFrame(data["data"], columns=data["columns"])
        st.table(df)


def save_to_database():
    query = st.session_state.get('query','')
    answer = st.session_state.get('response','')
    cursor.execute("CREATE TABLE IF NOT EXISTS savedgraphs (query TEXT, answer TEXT)")
    cursor.execute("INSERT INTO savedgraphs (query, answer) VALUES (?, ?)",(query, answer))
    conn.commit()

def fetch_historical_data():
    cursor.execute("SELECT query,answer FROM savedgraphs")
    return cursor.fetchall()
def welcome():
    st.title("👨‍💻 Talk with your CSV")
    st.write("### An application which lets you analyze your csv")
    st.write("#### How it works")
    st.write("Upload your CSV file and input a query what analysis you want from csv")
    st.write("Query can also be as to draw a bar chart or line chart or table it can also be QnA")
    st.write("If the result want to be stored or added to the dashboard then a button is provided which is Add to canva which will add result to the dashboard")
    st.write("A dashborad is available which is used to display the chart stored by the user")

    if st.button("Take me to site"):
        st.session_state['authentication_status'] = True


def login():
    tab1, tab2 = st.tabs(["👨‍💻 Talk with CSV", "🗃 Dashboard"])

    #st.title("👨‍💻 Talk with your CSV")
    tab1.subheader("👨‍💻 Talk with your CSV")
    #st.write("Please upload your CSV file below.")
    tab1.write("Please upload your CSV file below")
    data = tab1.file_uploader("Upload a CSV" , type="csv",accept_multiple_files=False, key="fileUploader")

    query = tab1.text_area("Send a Message")

    if tab1.button("Submit Query"):
        # Create an agent from the CSV file.
        agent = csv_tool(data)

        # Query the agent.
        response = ask_agent(agent=agent, query=query)


        # Decode the response.
        decoded_response = decode_response(response)
        #decoded_response = {"bar": {"columns": ["Price"], "data": [20.04, 16.94, 15.77]}}

        # Write the response to the Streamlit app.
        write_answer(decoded_response)
        st.session_state['query'] = query
        st.session_state['response'] = str(decoded_response)
        if st.button("Exit",args=(st.session_state.query,st.session_state.response)):
                print("Removed element")
                print("Removed element finally removed")


    if tab1.button("Add this to Canva"):
        save_to_database()
    with tab2:
        tab2.subheader("All the graphs")
        showallgraph()


def main():
    if 'authentication_status' not in st.session_state:
        st.session_state['authentication_status'] = False
    if st.session_state['authentication_status']:
        login()
    else:
        welcome()
if __name__ == "__main__":
    main()
