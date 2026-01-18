FROM python:3.9-slim

# Create non-root user with home directory
RUN groupadd -r user && useradd -r -g user -u 1000 -m -d /home/user user

WORKDIR /app

COPY requirements.txt .

RUN apt-get update \
    && apt-get install -y build-essential libssl-dev libffi-dev wget libegl1 libopengl0 libxcb-cursor0 libfreetype-dev qt6-base-dev \
    && wget -q -O- https://download.calibre-ebook.com/linux-installer.sh | sh /dev/stdin version=8.16.2 install_dir=/usr/local \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get remove -y build-essential libssl-dev libffi-dev wget \
    && apt-get autoremove -y \
    && rm -rf /var/cache/apt/* \
    && rm -rf /var/lib/apt/lists/*

COPY . .


# Change ownership and switch to non-root user
RUN chown -R user:user /app && \
    chown -R user:user /home/user

USER user

CMD ["python", "-u", "manga_watchdog.py", "--data-path", "/app/data"]