FROM python:3.10
ENV PYTHONUNBUFFERED 1

# Create directories
RUN mkdir /requirements /code
WORKDIR /code

# Copy and install Python requirements
ADD ./requirements /requirements
RUN pip install --no-cache-dir -r /requirements/versioned.txt

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    apt-transport-https \
    ca-certificates \
    binutils \
    libproj-dev \
    gdal-bin \
    && rm -rf /var/lib/apt/lists/*

# Add Yarn repository using new method
RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg \
    -o /usr/share/keyrings/yarn-archive-keyring.gpg
RUN echo "deb [signed-by=/usr/share/keyrings/yarn-archive-keyring.gpg] https://dl.yarnpkg.com/debian stable main" \
    > /etc/apt/sources.list.d/yarn.list

# Install Yarn
RUN apt-get update && apt-get install -y yarn \
    && rm -rf /var/lib/apt/lists/*

# Optional: Node.js repo (if needed)
# RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && apt-get install -y nodejs
