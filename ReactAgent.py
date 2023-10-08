import os
import pandas as pd
# import sys
# sys.path.insert(0, '/Users/azure/Documents/Workspace/llama_index')
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
    adm_pd_query_engine = PandasQueryEngine(pd.read_csv('data/2023院校招生章程.csv'), output_processor = output_processor)
    score_pd_query_engine = PandasQueryEngine(pd.read_csv('data/2022全国大学各省专业录取分数信息.csv'), output_processor = output_processor)


    # Initilized React Agent
    query_engine_tools = [
        QueryEngineTool(
            query_engine=vs_query_engine,
            metadata=ToolMetadata(
                name="knowledgebase",
                description="提供的信息包括：2023年甘肃省普通高等学校招生工作规定,云南省普通高校招生网上填报志愿考生须知，以及安徽师范大学就业质量报告",
            ),
        ),
        QueryEngineTool(
            query_engine=adm_pd_query_engine,
            metadata=ToolMetadata(
                name="regulation_database",
                description="提供了2023年各个学校招生标准和章程。当需要查询某所大学的录取标准时，应该使用此工具",
            ),
        ),
        QueryEngineTool(
            query_engine=score_pd_query_engine,
            metadata=ToolMetadata(
                name="score_database",
                description='''
                这是一份表格，提供了2020年到2022年间，全国各省专业录取分数线。
                输出字段有:最高分,最低分,投档线差,投档位次,专业。
                每个大学，每个年份有很多专业，默认搜索2023年的信息，永远是选取3000条信息。
                比如：问到清华录取分数最高的专业是什么？可以使用的Action input 如下:
                {{"大学名称":"清华大学", "goal":"分数线最高的专业"}}
                ''',
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
