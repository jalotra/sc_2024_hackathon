FROM python:3.12
WORKDIR /app

# Copy all dependencies to $WORKDIR

# Rest is needed by UMAP 
RUN curl --proto '=https' --tlsv1.2 https://sh.rustup.rs > rustup.sh && sh rustup.sh -y
ENV PATH="/root/.cargo/bin:${PATH}"

RUN apt-get update && apt-get install -y \
  libffi-dev libcurl4-openssl-dev bash git gcc build-essential curl \ 
  libmariadb-dev python3-mysqldb pkg-config libmagic1

COPY ./requirements.txt .
RUN pip3 install --upgrade pip 
RUN pip3 install -r requirements.txt
COPY . .
RUN chmod 777 app.py
RUN chmod 777 docker-entrypoint.sh 

EXPOSE 5000:5000
EXPOSE 5001:5001
EXPOSE 5002:5002
RUN curl -L https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh -o /usr/local/bin/wait-for-it && \
    chmod +x /usr/local/bin/wait-for-it

ENTRYPOINT ["sh", "-c", "/app/docker-entrypoint.sh"]







