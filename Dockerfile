# Base image pull 
FROM python:3.9.2

# Copy source code to container
COPY . /upbit-trader

# Set working directory
WORKDIR /upbit-trader/src

# Set timezone
RUN sudo ln -sf /usr/share/zoneinfo/Asiz/Seoul /etc/localtime

# Set Pip mirror server & upgrade
RUN mkdir ~/.pip && printf "[global]\nindex-url=http://mirror.kakao.com/pypi/simple\ntrusted-host=mirror.kakao.com" > ~/.pip/pip.conf
RUN /usr/local/bin/python -m pip install --upgrade pip && pip install --upgrade -r ../requirements.txt 

# Run command ex) python server.py
CMD [ "python", "server.py" ]