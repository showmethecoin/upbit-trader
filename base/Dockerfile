# Base image pull 
FROM python:3.9.2

# Set timezone
ENV TZ=Asia/Seoul

    # Set debian apt mirror server
RUN sed -i 's/deb.debian.org/mirror.kakao.com/g' /etc/apt/sources.list \
    && sed -i 's/security.debian.org/ftp.kaist.ac.kr/g' /etc/apt/sources.list \
    # Set Pip mirror server
    && mkdir ~/.pip \
    && printf "[global]\nindex-url=http://mirror.kakao.com/pypi/simple\ntrusted-host=mirror.kakao.com" > ~/.pip/pip.conf \
    # LLVM installation
    && wget --no-check-certificate -O - https://apt.llvm.org/llvm-snapshot.gpg.key | apt-key add - \
    && printf "deb http://apt.llvm.org/bionic/ llvm-toolchain-bionic-10 main" >> /etc/apt/sources.list \
    && apt update \
    && apt install -y llvm-10* \
    && ln -s /usr/bin/llvm-config-10 /usr/bin/llvm-config \
    && apt autoremove -y \
    && rm -rf /var/lib/apt/lists/* 
