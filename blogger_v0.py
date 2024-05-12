#!/bin/env python
# from https://github.com/abvijaykumar/crewai-blogs/tree/main, 
# https://abvijaykumar.medium.com/multi-agent-system-crew-ai-3773356b8c3e
# https://abvijaykumar.medium.com/
import os
import sys
import dotenv
import time
from textwrap import dedent as dd
from pprint import pprint

import gvars as g  # storage space for global vars

from crewai import Agent, Task, Crew, Process
from crewai_tools import WebsiteSearchTool
from crewai_tools import SerperDevTool
from langchain_community.tools import DuckDuckGoSearchRun

from model_select import ModelSelect
from exa_search_tool import ExaSearchTool
from file_writer_tool import FileWriterTool

# ╔═════════════════════════════════════════════════════════════ !r
# ║ Serper Search Tools Class
# ╚═════════════════════════════════════════════════════════════
class SerperSearch():
    def search(query: str):
        """Search the web for information on a given topic"""
        try:
            rs = SerperDevTool(api_key=os.environ["SERPER_API_KEY"]).run(query)
            return rs
        except Exception as e:
            raise e

web_tool = WebsiteSearchTool()
exa = ExaSearchTool._exa()  # alt search when DDGS fails
file_writer = FileWriterTool()

# search_tool = DuckDuckGoSearchRun()  # always get rate-limit errors, final output file empty !r
# search_tool = SerperDevTool(api_key=os.environ["SERPER_API_KEY"]) !r

# This is the only set of search tools that work, but that all be activated.  !g
# You can't use exa search with websitelookup.
search_tool = ExaSearchTool.search
find_similar_tool = ExaSearchTool.find_similar
search_and_contents_tool = ExaSearchTool.search_and_contents

# use_llm_config = "OLLAMA"
use_llm_config = "LMS"
use_llm_config = "OPENAI"
this_model = ModelSelect(use_llm_config)
# this_model = ModelSelect("LMS")
# this_model = ModelSelect("OPENAI")
llm = this_model.llm_server()


dotenv.load_dotenv(g.crew_env_file)

task_names = {}




def kickoff_crew(topic):
    researcher = Agent(
        role="Internet Research",
        goal=f"Perform research on the {topic}, and find and explore about {topic} ",
        verbose=True,
        llm=llm,
        backstory=dd(f"""
            You are an expert Internet Researcher
            Who knows how to search the internet for detailed content on {topic}
            Include any code examples with documentation
        """)
    )
    blogger = Agent(
        role='Blogger',
        goal="Write engaging and interesting blog in maximum 2000 words. Add relevant emojis",
        verbose=True,
        allow_delegation=True,  
        llm=llm,         
        backstory=dd(f"""
            You are an Expert Blogger on Internet.  
            Include code examples, and provide tutorial type instructions for the readers.
        """),
    )

    task_search = Task(
        description=dd(f"""
            Search for all the details about the {topic}.
            Your final answer MUST be a consolidated content that can be used for blogging.
            This content should be well organized, and should be very easy to read.  
        """),
        expected_output=f'A comprehensive 10000 words information about {topic}.',
        max_inter=1,  # 1 just for testing.  3 is preferred.
        agent=researcher,
        tools=[
            search_tool,
            web_tool,
            # file_writer,
            find_similar_tool,
            search_and_contents_tool
        ],
    )
    # update outer ary for printing stats later
    task_names['task_search'] = ['ExaSearchTool.search', 'web_tool']

    task_post = Task(
        description=dd("""
            Write a well structured blog and at max 10000 words. 
            The Blog should also include images, diagrams, sample programs and codes, tutorials, 
            and all the content that is useful for the readers. 
            Also explain the concepts, theory and/or architecture in detail. 
            Once the blog is created, create a new file called 'blog.md', and save the blog in that file.
        """),
        expected_output=f'A comprehensive 20 paragraph blog on {topic}',  # in Markdown format',
        agent=blogger)
    
    crew = Crew(
        agents=[researcher, blogger],
        tasks=[task_search, task_post],
        verbose=2,
        process=Process.sequential
    )

    crew_result = crew.kickoff()
    return crew_result


if len(sys.argv) == 2:
    _topic = sys.argv[1]

    start_timer = time.time()
    result = kickoff_crew(_topic)
    end_timer = time.time()
    runtime = int(end_timer - start_timer)
    print(result)

    # get current run details
    current_model_name = dict(this_model.llm_server())['model_name']
    current_server = dict(this_model.llm_server())['openai_api_base']
    # current_search_tool = dict(search_tool)['name']
    # current_web_tool = dict(web_tool)['args_schema']

    from importlib.metadata import version
    import platform
    print(f"""
┌────────────────────────────────────────────────────────────
│ Runtime Stats
└────────────────────────────────────────────────────────────
        LLM_config: {use_llm_config}
        Server:     {current_server}
        Model:      {current_model_name} (only valid for 'OPENAI' config)
        Runtime:    {runtime} secs

    Current versions
        langchain           {version('langchain')}
        langchain_community {version('langchain_community')}
        crewai              {version('crewai')}
        crewai_tools        {version('crewai_tools')}
        Python              {sys.version}
        System              {platform.system()} {platform.release()}

    Env vars
        OPENAI_API_KEY      {os.environ['OPENAI_API_KEY']}
        OPENAI_API_BASE_URL {os.environ['OPENAI_API_BASE_URL']}
        OPENAI_MODEL_NAME   {os.environ['OPENAI_MODEL_NAME']}

    """)
else:
    print("Please pass topic as parameter. Usage python3 `blogger.py <topic-or-keyword>`")
