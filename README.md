## Introduction
This project is an implementation of question answering sql rag in InfluxDB and langgraph.

## Graph
![DAG](static/influxdb-rag-white.png)

## Prerequisites
- Docker installed.
- An account in Langsmith.

## Models
- llama3.2
- llama3-groq-tool-use

## DEVELOPMENT
1. Clone the repository.
2. Copy the `.env.example` to `.env` and update the values as per your environment.
3. Start the OLLAMA server `ollama serve`.
4. Up the docker containers `docker-compose up -d --build`.

***InfluxDB***
1. Run `docker-compose exec -it influxdb3 bash`.
2. Create the database:
```
influxdb3 create database students
```
3. Write into the database:
```
influxdb3 write \
  --database students \
  'attendance,name=abc present=1 1742256000
attendance,name=xyz present=0 1742256000
attendance,name=abc present=0 1742342400
attendance,name=xyz present=1 1742342400
attendance,name=abc present=1 1742428800
attendance,name=xyz present=1 1742428800'
```
```
influxdb3 write \
  --database students \
  'home,room=Living\ Room temp=21.1,hum=35.9,co=0i 1736323200
home,room=Kitchen temp=21.0,hum=35.9,co=0i 1736323200
home,room=Living\ Room temp=21.4,hum=35.9,co=0i 1736326800
home,room=Kitchen temp=23.0,hum=36.2,co=0i 1736326800
home,room=Living\ Room temp=21.8,hum=36.0,co=0i 1736330400
home,room=Kitchen temp=22.7,hum=36.1,co=0i 1736330400
home,room=Living\ Room temp=22.2,hum=36.0,co=0i 1736334000
home,room=Kitchen temp=22.4,hum=36.0,co=0i 1736334000
home,room=Living\ Room temp=22.2,hum=35.9,co=0i 1736337600
home,room=Kitchen temp=22.5,hum=36.0,co=0i 1736337600
home,room=Living\ Room temp=22.4,hum=36.0,co=0i 1736341200
home,room=Kitchen temp=22.8,hum=36.5,co=1i 1736341200'
```
OR you can use file:
```
influxdb3 write --database students  --file /home/docker/attendance.txt
```
4. Verify:
```
influxdb3 query --database=students "SHOW TABLES"
```
5. Delete if needed:
```
influxdb3 delete table --database students attendance
```

***Ollama***
1. Run `docker-compose exec -it ollama bash`.
2. Install models: `ollama pull llama3.2` `ollama pull llama3-groq-tool-use`.
3. Start the server: `ollama serve`.

***Langgraph***
1. Run `docker-compose exec -it langgraph bash`.
2. Run `langgraph dev --host 0.0.0.0 --port 2024`.
3. [Studio UI](https://smith.langchain.com/studio/?baseUrl=http://0.0.0.0:2024). On failure, browse to `Langgraph Platform > Langgraph Studio`.
4. [Langsmith UI](https://smith.langchain.com).

***CLI***
1. Run `docker-compose exec -it langgraph bash`.
2. Run `python rag.py`.
3. To end the chat type `exit` or `quit`.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
