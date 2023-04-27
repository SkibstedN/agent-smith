# Dockerfile kali

# Official base image
FROM kalilinux/kali-rolling AS build-image

# Alias
RUN echo "alias l='ls -al'" >> /root/.bashrc

# Install base packages
RUN apt -y update && apt -y upgrade && apt -y autoremove && apt clean
RUN apt install curl python3 python3-pip -y --no-install-recommends

# Set working directory to /root
WORKDIR /root

FROM build-image AS install-metasploit

# Install metasploit
RUN curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall
RUN chmod 755 msfinstall
RUN ./msfinstall
RUN rm msfinstall

RUN export PATH=/bin:$PATH

FROM install-metasploit AS install-packages

# Install packages from file
COPY ./packages.txt ./
RUN xargs -a packages.txt apt install -y --no-install-recommends
RUN rm packages.txt

FROM install-packages AS setup-requirements

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