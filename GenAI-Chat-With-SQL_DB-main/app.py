import streamlit as st
from pathlib import Path
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents import AgentType

from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.callbacks import StreamlitCallbackHandler
from sqlalchemy import create_engine
import sqlite3
from langchain_groq import ChatGroq

st.set_page_config(page_title="LangChain: Chat with SQL DB", page_icon="🐦")

st.title(" LangChain: Chat with SQL DB")

LOCALDB = "USE_LOCALDB"
MYSQL = "USE_MYSQL"

radio_opt = ["USe SQLLite 3 Database- Student.db", "Connect to you SQL Database"]
selected_opt = st.sidebar.radio(label="Choose the DB which you want to ", options=radio_opt)

if selected_opt == "Connect to you SQL Database":
    db_uri = MYSQL
    mysql_host = st.sidebar.text_input("Provide mysql host name")
    mysql_user = st.sidebar.text_input("Provide user name")
    mysql_password = st.sidebar.text_input("Enter your password", type="password")
    mysql_database = st.sidebar.text_input("Provide mysql database name")
else:
    db_uri = LOCALDB

api_key = st.sidebar.text_input(label="Groq API key", type="password")

if not db_uri:
    st.info("Please enter your db_uri")

if not api_key:
    st.info("Please enter your API key")
    st.stop()  # STOP if no api_key

# LLM Model
llm = ChatGroq(groq_api_key=api_key, model_name="Llama3-8b-8192", streaming=True)

# Configure
@st.cache_resource(ttl="2h")
def Configure(db_uri, mysql_host=None, mysql_user=None, mysql_password=None, mysql_database=None):
    if db_uri == LOCALDB:
        dbfilepath = (Path(__file__).parent / "student.db").absolute()
        print(dbfilepath)
        creator = lambda: sqlite3.connect(f"file:{dbfilepath}?mode=ro", uri=True)
        return SQLDatabase(create_engine("sqlite:///", creator=creator))
    elif db_uri == MYSQL:
        if not (mysql_host and mysql_user and mysql_database and mysql_password):
            st.error("Please provide all MySQL details")
            st.stop()
        return SQLDatabase(
            create_engine(f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_database}")
        )

# Configure the DB
if db_uri == MYSQL:
    db = Configure(db_uri, mysql_host, mysql_user, mysql_password, mysql_database)
else:
    db = Configure(db_uri)


## Toolkit 

toolkit = SQLDatabaseToolkit(db=db,llm=llm)

agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
)
if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state.messages = [{"role": "assistant", "content": "How can I help you?"}]

# Display message history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Handle user query input
user_query = st.chat_input(placeholder="Ask anything from the database")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
     streamlit_callback = StreamlitCallbackHandler(st.container())
     response = agent.run(user_query, callbacks=[streamlit_callback])
     st.session_state.messages.append({"role": "assistant", "content": response})
     st.write(response)  # <-- just use st.write() here


