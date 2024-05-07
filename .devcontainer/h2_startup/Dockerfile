FROM python:3.11-slim-bullseye

RUN apt-get update 
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get install -y \
    build-essential \
    poppler-utils \
    python3-dev \
    python3-cffi \
    shared-mime-info \
    curl \
    wget \
    vim \
    procps \
    gnupg \
    libpq-dev \
    gcc \
    iputils-ping \
    bash-completion \
    git \
    time \
    lsb-release

RUN curl https://raw.githubusercontent.com/git/git/master/contrib/completion/git-completion.bash -o ~/.git-completion.bash
COPY docker_bashrc_content /root/.bashrc