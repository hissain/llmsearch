import os
import time
import pandas as pd
import streamlit as st
from prompts import prompt_keywords, prompt_query
from duckduckgo_search import DDGS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

from dotenv import load_dotenv
load_dotenv()

# Define LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    google_api_key=os.getenv('GEMINI_API_KEY'),
    temperature=0.1
)

def generate_keywords(topic):
    prompt = PromptTemplate.from_template(prompt_keywords)
    chain = prompt | llm
    result = chain.invoke({"topic": topic})
    keywords = [keyword.strip() for keyword in result.content.split(',')]
    return keywords

def generate_queries(topic, keywords):
    prompt = PromptTemplate.from_template(prompt_query)
    chain = prompt | llm
    result = chain.invoke({"topic": topic, "keywords": keywords})
    queries = [q.strip() for q in result.content.split(',')]
    return queries

def search_duckduckgo(query):
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=10)
    return results

def parse_results_to_dataframe(results):
    data = [
        {
            'Title': result.get('title'),
            'URL': result.get('href'),
            'Description': result.get('body')
        }
        for result in results
    ]
    df = pd.DataFrame(data)
    df_filtered = df[df['URL'].str.startswith('https://patents.google.com/patent/')]
    return df_filtered

def search_prior_art(queries):
    full_result = []
    for query in queries:
        full_query = f"site:patents.google.com {query}"
        results = search_duckduckgo(full_query)
        full_result.extend(results)
        time.sleep(2)
    return parse_results_to_dataframe(full_result)

# Streamlit app
st.title("Patent Search and Analysis Tool")
st.write("Use this app to search for prior art related to your idea using DuckDuckGo and Google Patents.")

# User input
topic = st.text_area("Enter a description of your idea or topic:", "A new method for efficient solar energy conversion using nanotechnology.")

# Sidebar configuration
st.sidebar.header("Settings")
top_k_results = st.sidebar.number_input("Number of Results per Query", min_value=1, max_value=20, value=10, step=1)
api_key_input = st.sidebar.text_input("Google Gemini API Key", type="password")

# Update environment variable if the API key changes
if api_key_input and api_key_input != os.getenv('GEMINI_API_KEY'):
    os.environ['GEMINI_API_KEY'] = api_key_input

# Search functionality
if st.button("Search for Patents"):
    if not topic.strip():
        st.error("Please enter a valid topic description.")
    else:
        try:
            st.info("Generating keywords...")
            keywords = generate_keywords(topic)
            st.success("Keywords generated successfully!")
            st.write(keywords)

            st.info("Generating search queries...")
            queries = generate_queries(topic, keywords)
            st.success("Queries generated successfully!")
            st.write(queries)

            st.info("Searching for prior art...")
            prior_arts = search_prior_art(queries)
            st.success("Search completed!")

            if not prior_arts.empty:
                st.subheader("Search Results")
                for _, row in prior_arts.iterrows():
                    st.write(
                        f"### [{row['Title']}]({row['URL']})\n{row['Description']}"
                    )
            else:
                st.warning("No results found for the given queries.")

        except Exception as e:
            st.error(f"An error occurred: {e}")
