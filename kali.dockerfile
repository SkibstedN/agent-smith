# Dockerfile kali

# Official base image
FROM kalilinux/kali-rolling AS build-image

# Apt
RUN apt -y update && apt -y upgrade && apt -y autoremove && apt clean

# Tools
RUN apt install \
    sqlmap \
    curl \
    wfuzz \
    nmap \
    python3 \
    python3-pip \
    iputils-ping \
    sudo \
    # Add necessary tools above
    -y --no-install-recommends

# Alias
RUN echo "alias l='ls -al'" >> /root/.bashrc

# Set working directory to /root
WORKDIR /root

FROM build-image AS setup-requirements

# Get the requirements script
COPY ./requirements.txt ./

RUN pip3 install -r requirements.txt

RUN rm requirements.txt

FROM setup-requirements AS run

# Copy environment file
COPY ./.env ./

# Source the environment variables from .env file
RUN export $(grep -v '^#' .env | xargs)

# Run main python script
ENTRYPOINT ["tail", "-f", "/dev/null"]