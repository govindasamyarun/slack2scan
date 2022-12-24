FROM python:3.9.1

# Create application user 
RUN useradd -ms /bin/bash s2s && \
    usermod -aG sudo s2s

# Copy the source code to application home directory 
ADD . /usr/src/app/

# Limit the application user privilege 
RUN chown -R s2s:s2s /usr/src/app && \
    chmod -R 764 /usr/src/app

# Run the container as non-root user 
USER s2s

# Create empty directories 
RUN mkdir -p /usr/src/app/gitleaks/ && \
    mkdir -p /usr/src/app/downloads/ && \
    mkdir -p /usr/src/app/reports/

# Download gitleaks 
WORKDIR /usr/src/app/gitleaks/
RUN wget https://github.com/zricethezav/gitleaks/releases/download/v8.11.2/gitleaks_8.11.2_linux_x64.tar.gz && \
    tar -xvzf gitleaks_8.11.2_linux_x64.tar.gz

# Set the working directory 
WORKDIR /usr/src/app/

# Install python dependencies 
RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host=files.pythonhosted.org --no-cache-dir -r /usr/src/app/requirements.txt

CMD ["python","-u","/usr/src/app/src/app.py"]