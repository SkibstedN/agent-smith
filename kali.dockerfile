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
    # Add necessary tools above
    -y --no-install-recommends

# Alias
RUN echo "alias l='ls -al'" >> /root/.bashrc
RUN echo "alias nse='ls /usr/share/nmap/scripts | grep '" >> /root/.bashrc
RUN echo "alias scan-range='nmap -T5 -n -sn'" >> /root/.bashrc
RUN echo "alias http-server='python3 -m http.server 8080'" >> /root/.bashrc
RUN echo "alias php-server='php -S 127.0.0.1:8080 -t .'" >> /root/.bashrc
RUN echo "alias ftp-server='python -m pyftpdlib -u \"admin\" -P \"S3cur3d_Ftp_3rv3r\" -p 2121'" >> /root/.bashrc

# Set working directory to /root
WORKDIR /root

FROM build-image AS setup-requirements

# Get the requirements script
COPY ./requirements.txt ./

RUN pip3 install -r requirements.txt

FROM setup-requirements AS run

# Copy the files to the working directory in the container
COPY ./app ./

# Run main python script
CMD ["python3", "./main.py"]