CrewAI is undebugable :(  I have not seen just obtusity since my Assembly Language days, or maybe beta Java.  Nevertheless, it (so far) seems worth slogging through... but my patience is wearing thin.  Maybe I am just getting to old to put up with meaningless, obtuse, and undecipherable error messages, or may because it's 2024!

With that off my chest, this is an attempt to get CrewAI working.  For the record, I have yet to get a single example, demo or tutorial to work locally, and I have tried about 7 so far.  I assume it can be done, as most of examples I have been using were for local servers, but maybe they only work with specific versions of the 84,006 packages ands files in my environment.

## Status:

### Problem 1: 

(posted as an issue: https://github.com/joaomdmoura/crewAI/issues/602 )


When running local, I can't get past coworker errors. When I run the exact same workflow on OpenAI (using the last Exa example, below), it works fine.

On local Ollama or LM-Studio, it seems to be sensitive to the search tool.

With `search_tool = DuckDuckGoSearchRun()` I get errors like this:

> Action 'Delegate work to Internet Research' don't exist, these are the only available Actions:

With  `search_tool = SerperDevTool()`

>Action 'None (I will think of potential improvements without using any tools)' don't exist

With `search_tool = ExaSearchTool.search`

> Action Input: "epigenetics site:.edu OR site:.gov" I encountered an error while trying to use the too

With 
- `search_tool = ExaSearchTool.search` AND 
- `find_similar_tool = ExaSearchTool.find_similar` AND
- `search_and_contents_tool = ExaSearchTool.search_and_contents`

>Error executing tool. Co-worker mentioned not found, it must to be one of the following options:
- internet research

`internet research` definitely exists...

CrewAI does not seem to play nice with anything local, and I have tried dozens of different configs :/

Presumably, the tools are working the same, so perhaps the OpenAI API is not as compatible as claimed for Ollama and LMS? Or, it is something related to CrewAI?

The very simple code I am using to test is at https://github.com/tholonia/crewai-blogger/blob/main/blogger_v0.py

The log outputs are
https://github.com/tholonia/crewai-blogger/blob/main/output_ddgs.log
https://github.com/tholonia/crewai-blogger/blob/main/output_exa.log
https://github.com/tholonia/crewai-blogger/blob/main/output_openai.md
https://github.com/tholonia/crewai-blogger/blob/main/output_serper.log

### Problem 2

There are too many ways to do the same thing, each with their own issues.  This is not so much a technical issues, but it makes the docs and the attempt to fix any issues with the particular way the problem code has followed next to impossible.

### Problem 3

The 'dynamic' arguments are a nightmare to deal with.  I have yet to discover where the argument object is.  For example, if I have

```python
search_tool = ExaSearchTool.search
find_similar_tool = ExaSearchTool.find_similar
search_and_contents_tool = ExaSearchTool.search_and_contents
```
and 
```python
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
        find_similar_tool,
        search_and_contents_tool
    ],
)
```

Where/how can i see/change the arguments that are being passed?  Where are they coming from? This couls be an issue with me just not knowing enough about the horrors and ugliness of OOP.  I am a big fan of encapsulation, abstraction, and polymorphism, but Classes just make everything less transparent, way too obtuse to read and a nightmare to debug.

### Problem 4

It's this non-transparent, impossible-to-find-code that does stuff like the following...

DuckDuckGo search requires an array

```python
{'query': term}
```
but SerperSearch requires
```python
{'search_query': term}
```
Nowhere do I build that query.  I assume the AI is building the query, but somewhere along the line, something decided to escape the '_', turning `search_query` into `search\_query`, thereby breaking the API call.

In the same fashion, the code/AI is creating wild co-workers that don't exist, like ''Ask question to Internet Research", but there is no such coworker, so, it fails

```
Action 'Ask question to Internet Research' don't exist, these are the only available Actions:
```









This work is based on...

## CrewAI Blog examples
This code base has various exmaples that I have used in my blog series on Multi-Agent Systems and CrewAI

### Refer to the blog here

[Mutli Agent Systems - CrewAI blog Series](https://abvijaykumar.medium.com/list/multiagent-systems-1284ee465659)
