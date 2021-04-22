# Base image pull 
FROM codejune/smtc-base:v0.1

# Copy source code to container
COPY ../../../* /upbit-trader

# Set working directory
WORKDIR /upbit-trader/src

# Set timezone
ENV TZ=Asia/Seoul

# Run command ex) python server.py
CMD [ "python", "server.py" ]