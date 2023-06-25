import json
import streamlit as st
import sqlite3
import pandas as pd

conn = sqlite3.connect('news_data.db', check_same_thread=False)
cursor = conn.cursor()


def fetch_historical_data():
    cursor.execute("SELECT query,answer FROM savedgraphs")
    return cursor.fetchall()

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

def showallgraph():
    col1 ,col2,col3 = st.columns(3)
    with col1:
        st.markdown("### Bar Chart")
    with col2:
        st.markdown("### Answer")
    with col3:
        st.markdown("### Line graph")
    data = fetch_historical_data()
    if data:
        
        for row in data:
            new_data = row[1]
            new_data = new_data.replace("'",'"')
            data_1 = json.loads(new_data)
            #write_answer(data_1)
            with col1:
                if 'bar' in data_1:
                    st.write(row[0])
                    write_answer(data_1)
        for row in data:
            new_data = row[1]
            new_data = new_data.replace("'",'"')
            data_1 = json.loads(new_data)
            #write_answer(data_1)
            with col2:
                if 'answer' in data_1:
                    st.write(row[0])
                    write_answer(data_1)
        for row in data:
            new_data = row[1]
            new_data = new_data.replace("'",'"')
            print(new_data)
            data_1 = json.loads(new_data)
            #write_answer(data_1)
            if 'line' in data_1:
                with col3:
                    st.write(row[0])
                    write_answer(data_1)
        st.markdown("### Tables")
        for row in data:
            new_data = row[1]
            new_data = new_data.replace("'",'"')
            data_1 = json.loads(new_data)
            #write_answer(data_1)
            if 'table' in data_1:
                    st.write(row[0])
                    write_answer(data_1)