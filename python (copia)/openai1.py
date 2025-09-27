from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key="...",  
    # base_url="...",
    # organization="...",
    # other params...
)
messages = [
    (
        "system",
        "Eres un asistente útil que traduce del inglés al español. Traduce la oración del usuario.",
    ),
    ("human", "Hello world from Langchain with Python."),
]
#ai_msg = llm.invoke(messages)
ai_msg = llm.invoke(messages)
print(ai_msg.content)