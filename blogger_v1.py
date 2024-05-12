#!/bin/env python
# from https://github.com/abvijaykumar/crewai-blogs/tree/main, 
# https://abvijaykumar.medium.com/multi-agent-system-crew-ai-3773356b8c3e
# https://abvijaykumar.medium.com/
# https://github.com/HomunMage/AI_Agents/blob/main/crewAI/local/filewrite.py

# standard imports
import os
import sys
import gvars as g
import time
from colorama import Fore,Back
from pprint import pprint
import dotenv
from textwrap import dedent
from pathlib import Path
import getopt
import datetime
# from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

# crewai imports
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import tool, WebsiteSearchTool
from langchain_openai import ChatOpenAI as OpenAI
# for logging
from langsmith.wrappers import wrap_openai
from langsmith import traceable

# for debugging
import traceback
import functools

# my class for selecting the model (in ~/src/crewai/lib)
from model_select import ModelSelect
from exa_search_tool import ExaSearchTool
from file_writer_tool import FileWriterTool

# create a unique project name for tracing.  default .env in ~/src/crewai/lib
dotenv.load_dotenv(g.crew_env, override=True)

# assign vars
web_tool = WebsiteSearchTool()
exa = ExaSearchTool._exa()
file_writer = FileWriterTool()



llm         = False


# ╔═════════════════════════════════════════════════════════════ !c
# ║ Exa Search Tools Class
# ╚═════════════════════════════════════════════════════════════
def run_crew(topic):
    # ┌──────────────────────────────────────────────────────────── !g
    # │ AGENT: researcher
    # └────────────────────────────────────────────────────────────
    try:
        researcher = Agent(
            # config = loadyaml('researcher',"agents"),
            role = "Internet Researcher",
            goal = f"Perform research on {topic}, and find and explore about {topic}.",
            memory = g.memory,
            verbose = g.verbose,
            # output_file = "k-researcher.md",
            backstory = dedent(f"""
                You are an expert Internet Researcher. Who knows how to search the internet for 
                detailed content on {topic}. Include any code examples with documentation.
            """),
            llm = llm,
            tools=[file_writer],
        )
    except Exception as e:

        print(f"An error occurred while creating the AGENT |researcher|: [{str(e)}]")
        exit()
    # ┌──────────────────────────────────────────────────────────── !g
    # │ AGENT: blogger
    # └────────────────────────────────────────────────────────────

    try:
        blogger = Agent(
            role = "Blogger",
            goal = "Write engaging and interesting blog in maximum 10000 words. Add relevant emojis.",
            verbose = g.verbose,
            memory = g.memory,
            allow_delegation = True,
            output_file = "k-blogger.md",
            backstory = dedent(f"""
                You are an Expert Blogger on Internet. Include code examples, and provide tutorial 
                type instructions for the readers.
            """),
            llm=llm,
        )
    except Exception as e:
        print(f"An error occurred while creating the AGENT |blogger|: [{str(e)}]")
        exit()            


    # ┌──────────────────────────────────────────────────────────── !m
    # │ TASK: task_search
    # └────────────────────────────────────────────────────────────
    try:
        task_search = Task(
            description = dedent(f"""
                Search for all the details about {topic}. Your final answer MUST be a consolidated 
                content that can be used for blogging. This content should be well organized, and 
                should be very easy to read. Set the input parameter as:search_query
            """),
            expected_output = "A comprehensive 10000 words information about {topic}.",
            max_inter = 3,
            output_file = "k-task-search.md",
            agent = researcher,
            # tools=[file_writer, web_tool,search,find_similar,get_contents]
            tools=[
                file_writer, 
                web_tool,
                ExaSearchTool.search, 
                ExaSearchTool.find_similar, 
                ExaSearchTool.search_and_contents
            ],
        )            
    except Exception as e:
        print("An error occurred while creating the TASK |task_search|:", str(e))
        exit()  
            
    # ┌──────────────────────────────────────────────────────────── !m
    # │ TASK: task_post
    # └────────────────────────────────────────────────────────────
    try:
        task_post = Task(
            description = dedent(f""" 
                Write a well structured blog and at max 2000 words. The Blog should also include 
                sample programs and codes, tutorials, and all the content that is useful for the 
                readers. Also explain the concepts, architecture in detail. Once the blog is created, 
                create a new file called blog.md, and save the blog in that file.
            """),
            expected_output = "A comprehensive 20 paragraph blog on {topic} in markdown format.",
            output_file = "k-task-post.md",
            agent = blogger,
        )
    except Exception as e:
        print("An error occurred while creating the TASK |task_post|:", str(e))
        exit()  
            
    # ┌──────────────────────────────────────────────────────────── !c
    # │ CREW
    # └────────────────────────────────────────────────────────────
    try:
        crew = Crew(
            agents=[researcher, blogger],
            tasks=[task_search, task_post],
            verbose=g.verboseN,
            process=Process.sequential,
            # output_json = True,
        )
    except Exception as e:
        print("An error occurred while creating the CREW:", str(e))
        exit()  

    # crew_result = crew.kickoff(inputs={'search_query': f"data on {topic} between {g.from_date} to {to_date}"})
    crew_result = crew.kickoff()
    return crew_result


def getdates(xstr:str):
    def get_past_date(str_days_ago:str):
        """from https://stackoverflow.com/questions/28268818/how-to-find-the-date-n-days-ago-in-python """
        TODAY = datetime.date.today()
        splitted = str_days_ago.split()
        if len(splitted) == 1 and splitted[0].lower() == 'today':
            return str(TODAY.isoformat())
        elif len(splitted) == 1 and splitted[0].lower() == 'yesterday':
            date = TODAY - relativedelta(days=1)
            return str(date.isoformat())
        elif splitted[1].lower() in ['hour', 'hours', 'hr', 'hrs', 'h']:
            date = datetime.datetime.now() - relativedelta(hours=int(splitted[0]))
            return str(date.date().isoformat())
        elif splitted[1].lower() in ['day', 'days', 'd']:
            date = TODAY - relativedelta(days=int(splitted[0]))
            return str(date.isoformat())
        elif splitted[1].lower() in ['wk', 'wks', 'week', 'weeks', 'w']:
            date = TODAY - relativedelta(weeks=int(splitted[0]))
            return str(date.isoformat())
        elif splitted[1].lower() in ['mon', 'mons', 'month', 'months', 'm']:
            date = TODAY - relativedelta(months=int(splitted[0]))
            return str(date.isoformat())
        elif splitted[1].lower() in ['yrs', 'yr', 'years', 'year', 'y']:
            date = TODAY - relativedelta(years=int(splitted[0]))
            return str(date.isoformat())
        else:
            return "Wrong Argument format"

    if xstr.find("-") == -1:  # not YYYY/MM/DD:YYYY/MM/DD format
        # today = str(date.today())

        ft = xstr.split(":")
        dfrom = get_past_date(ft[0])
        dto   = get_past_date(ft[1])

        return dfrom,dto
def showhelp():
    print("help")
    rs = """
    -h, --help          show help (this file)
    -t, --topic         "search term, keywords"
    -v, --verbose       verbose switch (default in g.vars)
    -m, --memory        memory switch (default in g.vars)
    -s, --server        select server (assume it is running are all vars are set)
                        options are "OLLAMA", "LMS", "OPENAI" (default in g.vars)
    -r, --daterange     'from:to' range ex: 'yyyy/mm/dd:yyyy/mm/dd'
    
                        also supports the format "<n> <units>|'yesterday'|'today ago:<n> <units>|'yesterday'|'today' ago
                            examples:
                                today:today 
                                5 hours ago:today
                                yesterday:today
                                32 days ago:10 days ago
                                4 months ago:1 month ago
                                1 years ago:today (default)
                                2 years ago:today
                        
    """
    print(rs)
    exit()

if __name__ == "__main__":
    os.environ['LANGCHAIN_PROJECT'] = g.set_project_name("BLO")

    topic = False
    today = False
    verbose = False
    memory = False
    server = False
    daterange = "1 years ago:today"
    from_date, to_date = getdates(daterange)
    PROJECT_NAME = ""
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv,"ht:vms:r:",["help","topic=","verbose","memory","server=","daterange="],)
    except Exception as e:
        print(str(e))

    for opt, arg in opts:
        if opt in ("-t", "--topic"):
            topic = arg
        if opt in ("-v", "--verbose"):
            g.verbose = True
            g.verboseN = 2
        if opt in ("-m", "--memory"):
            g.memory = True
        if opt in ("-s", "--server"):
            g.server = arg
            thismodel = ModelSelect(g.server)
            llm = thismodel.llm_server()
            PROJECT_NAME = f"{g.server}_{os.environ['LANGCHAIN_PROJECT']}"
        if opt in ("-r", "--daterange"):
            from_date, to_date = getdates(arg)
        if opt in ("-h", "--help"):
            showhelp()

    g.from_date = from_date
    g.to_date = to_date
    print(f"""
       ┌──────────────────────────────────────────────────────────── 
       │ PROJECT: {PROJECT_NAME}
       │ verbose: {g.verbose}
       │ verboseN:{g.verboseN}
       │ crew_env:{g.crew_env}
       │ memory:  {g.memory}
       │ server:  {g.server}
       │ date range:  From: {g.from_date} to {g.to_date}
         OPENAI_API_BASE_URL: {os.environ['OPENAI_API_BASE_URL']}
         OPENAI_MODEL_NAME:   {os.environ['OPENAI_MODEL_NAME']}
       └────────────────────────────────────────────────────────────
    """)

    if topic == False:
        print("Missing '-t, --topic' arg")
        showhelp()

    today = datetime.date.today()
    datestr = today.strftime("%B %d, %Y")

    start = time.time()
    result = run_crew(topic)
    end = time.time()
    print(f"Elapsed time: [{end - start}]")
    print(result)


