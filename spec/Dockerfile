FROM nikolaik/python-nodejs:python3.10-nodejs16
ENV APP=/app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
  && apt-get install -y \
    build-essential \
    libpq-dev \
    gettext \
    libsasl2-dev \
    nginx \
    python-dev \
    libldap2-dev \
    unixodbc-dev \
    unixodbc \
    vim
    
# This block loads the drivers required to make pyodbc and microsoft sql server work
# It came from https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver16
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql18
RUN ACCEPT_EULA=Y apt-get install -y mssql-tools18

# Set the working directory to /app
WORKDIR $APP

# Copy the current directory contents into the container at /app 
ADD . $APP

# Setup nginx
COPY nginx.default /etc/nginx/sites-available/default
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
  && ln -sf /dev/stderr /var/log/nginx/error.log


# Install the dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


WORKDIR $APP/ui
RUN npm install
RUN npm run build

WORKDIR $APP
RUN python manage.py collectstatic --noinput
RUN chmod a+x /app/start-server.sh

EXPOSE 8020
STOPSIGNAL SIGTERM
CMD ["/app/start-server.sh"]
