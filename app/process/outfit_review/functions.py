from data.neontech.functions import get_metas_from_neon

from langchain.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
)
from langchain_community.callbacks import get_openai_callback
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel


llm = ChatOpenAI(model="gpt-3.5-turbo")
print("executed till here")
vectorstore = Chroma(persist_directory="chromadb",
                     embedding_function=OpenAIEmbeddings())
retriever = vectorstore.as_retriever()

def format_docs(docs):
    print(len(docs))
    return "\n\n".join(doc.page_content for doc in docs)


def format_chat_history(history_array):
    formatted_history = ""
    for message in history_array:
        role = message['role']
        content = message['content']

        if role == "assistant":
            content = content.replace("{", "").replace("}", "").strip()  # Remove extra curly braces and strip whitespace for consistency with the front-end formatting
        
        formatted_history += f"{role}: {content}\n"
    
    # Remove trailing newline
    return formatted_history.strip()

import requests

def get_latlong_weather_description(lat,long):
    latitude = lat  # Approximate latitude of Bhopal
    longitude = long  # Approximate longitude of Bhopal

    base_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max",
        "timezone": "Asia/Kolkata"  # Use the correct timezone for Bhopal (IST)
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        daily = data['daily']
        today = daily['time'][0]

        weather_code = daily['weathercode'][0]
        max_temp = daily['temperature_2m_max'][0]
        min_temp = daily['temperature_2m_min'][0]
        precipitation = daily['precipitation_sum'][0]
        max_wind = daily['windspeed_10m_max'][0]

        description = f"Today, the weather is expected to be "

        if weather_code == 0:
            description += "clear skies with "
        elif 1 <= weather_code <= 3:
            description += "mainly clear skies with "
        elif 45 <= weather_code <= 48:
            description += "foggy with "
        elif 51 <= weather_code <= 67:
            description += "drizzle with "
        elif 71 <= weather_code <= 82:
            description += "snowfall with "
        elif 85 <= weather_code <= 86:
            description += "snow showers with "
        elif 95 <= weather_code <= 99:
            description += "thunderstorms with "

        description += f"a high of {max_temp}°C and a low of {min_temp}°C."
        if precipitation > 0:
            description += f" There is a chance of {precipitation} mm of precipitation."
        if max_wind > 15:
            description += f" Winds may gust up to {max_wind} km/h."
        return description
    
    else:
        return "Error fetching weather data."

def generate_review(prompts_dict, query, dress_description, chat_history, user_metas, geo_metas):
    review_prompt = ChatPromptTemplate.from_messages([
            ("system","""{0}
Your task is to analyze the following information:
1. Dress Description: "{1}" (This is a detailed description of the user's outfit for today.)
2. User Metadata: "{2}"
3. Weather data for today: "{3}"
{4}
Following is the chat history between you and the user: "{5}" Now continue:
         """.format(
             prompts_dict["runner_system"],
             dress_description,
             user_metas,
             geo_metas,
             prompts_dict["output_template"],
             format_chat_history(chat_history))),
        ("user", "{question}"),
        ("user", "{context}"),
    ])
    review_rag_chain_from_docs = (
        RunnablePassthrough.assign(
            context=(lambda x: format_docs(x["context"])),
            )
        | review_prompt
        | llm
        | StrOutputParser()
    )
    review_rag_chain_with_source = RunnableParallel(
        {"context":retriever, "question":RunnablePassthrough()}
    ).assign(answer=review_rag_chain_from_docs)
    with get_openai_callback() as cb:
        answer = review_rag_chain_with_source.invoke(query)['answer']
        print(cb)
    return({"answer":answer})

def get_review_from_user_id(prompts_dict, query, dress_description, chat_history, user_id, lat_long):
    user_metas = get_metas_from_neon(user_id)
    geo_metas = get_latlong_weather_description(lat_long["lat"],lat_long["long"])
    response = generate_review(prompts_dict, query, dress_description, chat_history, user_metas, geo_metas)
    return response