# Base image pull 
FROM codejune/smtc-base:v0.1

# Copy source code to container
COPY . /upbit-trader

# Set working directory
WORKDIR /upbit-trader

# Pip version upgrade
RUN /usr/local/bin/python -m pip install --upgrade pip \
    # Python module installation
    && pip install --upgrade -r ./requirements.txt --no-cache-dir
    
# Run command ex) python server.py
CMD [ "python", "src/server.py" ]