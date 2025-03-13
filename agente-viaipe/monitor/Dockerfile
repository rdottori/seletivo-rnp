FROM python:3.10
WORKDIR /monitor
COPY requirements.txt ./

RUN apt-get update && apt-get upgrade -y \
  && apt-get install --no-install-recommends -y \
    bash \
    build-essential \
    curl \
    git

RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "-u", "./main.py"]
