import os
import pandas as pd
from llama_index import (ServiceContext, StorageContext, 
                        VectorStoreIndex, SimpleDirectoryReader, load_index_from_storage)
from llama_index.query_engine import PandasQueryEngine
from llama_index.llms import OpenAI
from llama_index.embeddings import HuggingFaceEmbedding

from llama_index.agent import ReActAgent
from llama_index.tools import QueryEngineTool, ToolMetadata

# Initilize Query Engine
def create_react_agent():
    persist_dir = 'storage'
    data_dir = 'data'
    llm = OpenAI(model="gpt-3.5-turbo")
    embed_model = HuggingFaceEmbedding(model_name='moka-ai/m3e-base')
    service_context = ServiceContext.from_defaults(llm=llm, embed_model=embed_model)

    if os.path.exists(persist_dir):
        print('load existing stroage')
        storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
        vs_index = load_index_from_storage(storage_context, service_context=service_context)
    else:
        documents = SimpleDirectoryReader(data_dir, exclude=['*.csv']).load_data()
        vs_index = VectorStoreIndex.from_documents(documents, service_context=service_context)
        vs_index.storage_context.persist(persist_dir)
    vs_query_engine = vs_index.as_query_engine()

    from customization.pandas_query_engine.pandas_query_engine import output_processor
    pd_query_engine = PandasQueryEngine(pd.read_csv('data/2023院校招生章程.csv'), output_processor = output_processor)


    # Initilized React Agent
    query_engine_tools = [
        QueryEngineTool(
            query_engine=vs_query_engine,
            metadata=ToolMetadata(
                name="knowledgebase",
                description="2023 年甘肃省普通高等学校招生工作规定",
            ),
        ),
        QueryEngineTool(
            query_engine=pd_query_engine,
            metadata=ToolMetadata(
                name="database",
                description="提供了2023院校招生章程的表格,给定学校名称,输出学校的章程",
            ),
        ),
    ]

    # initialize ReAct agent
    from customization.react_agent.formatter import ReActChatFormatter
    return ReActAgent.from_tools(query_engine_tools, llm=llm,
                                 react_chat_formatter=ReActChatFormatter(tools=query_engine_tools),
                                 verbose=True)

if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()

    agent = create_react_agent()
    while(1):
        prompt = input('\n==> 问我些大学招生问题：\n|->')
        print(agent.query(prompt))