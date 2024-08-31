# What ?? 
- This is a sample application that acts as a RAG pipeline using State of Art (RAPTOR) framework. 

## Flow ??
- A Research Agent on top of evo.ninja (AutoGPT) 
	- Takes a goal as an input 
		Example : (Crawl all the web and figure out the pain points of Apple using Analytics Products) 
	- Outputs : 
		1. Crawls the web and downloads all the metadata around the goal.
		2. We have an ingestion pipeline that pulls data and puts into a redis / mysql datastores.
		3. Rapotor creates a NRT tree on top of it / have to think about deletion of info from the Tree. 
		4. We have a QA / Retriever Agent that takes a LLM Context and asks Tree to give Real Time info around questions.
		5. We summarise the outputs using a LLM and then output data.

## Tech Stack 
- FastApi : Web / Rest Api <br/>
- Redis / Mysql : DataStores <br/>
- Langchain : Chaining <br/>

## Want to see it in action ? 
```
1. you would need a OPEN_API_KEY env var, see docker-compose.yml for details. 
2. do a docker compose -f docker-compose.yml up 
3. goto localhost:5001 to see frontend. 
```
![front_end_demo](./images/frontend_app_example.png)

Future Improvements : 
- Add KGs as well (Knowledge Graphs) <br/> 
- Think about E2E flow. <br/> 
