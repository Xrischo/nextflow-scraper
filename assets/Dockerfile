FROM ubuntu:22.04

# install python and pip
RUN apt-get update && apt-get install -y \
    openjdk-21-jdk \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# install nextflow
RUN curl -fsSL https://get.nextflow.io | bash && \
    mv nextflow /usr/local/bin/

# # copy assets // USING VOLUME
# WORKDIR /app
# COPY assets/ .

WORKDIR /app
COPY ./requirements.txt .

# install dependencies
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# CMD ["python3", "scraper.py"]
CMD ["/bin/sh", "-c", "bash"]
