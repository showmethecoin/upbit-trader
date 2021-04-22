# Base image pull 
FROM python:3.9.2

# Set timezone
ENV TZ=Asia/Seoul

    # Set debian apt mirror server
RUN sed -i 's/deb.debian.org/mirror.kakao.com/g' /etc/apt/sources.list \
    # LLVM installation
    && apt update \
    && apt install -y software-properties-common \
    && wget --no-check-certificate -O - https://apt.llvm.org/llvm-snapshot.gpg.key | apt-key add - \
    && add-apt-repository 'deb http://apt.llvm.org/bionic/   llvm-toolchain-bionic-10  main' \
    && apt update \
    && apt install -y llvm-10* \
    && ln -s /usr/bin/llvm-config-10 /usr/bin/llvm-config \
    && rm -rf /var/lib/apt/lists/* \
    # Set Pip mirror server
    && mkdir ~/.pip \
    && printf "[global]\nindex-url=http://mirror.kakao.com/pypi/simple\ntrusted-host=mirror.kakao.com" > ~/.pip/pip.conf \
    # Pip version upgrade
    && /usr/local/bin/python -m pip install --upgrade pip \
    # Python module installation
    && pip install --upgrade -r ../../../requirements.txt --no-cache-dir
