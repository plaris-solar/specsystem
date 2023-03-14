FROM nikolaik/python-nodejs:python3.10-nodejs16
ENV APP=/app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN sed -i 's/$/ contrib/' /etc/apt/sources.list \
  && apt-get update \
  && apt-get install -y \
    build-essential \
    libpq-dev \
    gettext \
    libsasl2-dev \
    nginx \
    python-dev \
    libldap2-dev \
    libreoffice \
    openssl \
    ttf-mscorefonts-installer \
    unixodbc-dev \
    unixodbc \
    vim
    
# This block loads the drivers required to make pyodbc and microsoft sql server work
# It came from https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver16
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
  && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
  && apt-get update \
  && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
  && ACCEPT_EULA=Y apt-get install -y mssql-tools18

RUN echo "[ODBC]\n\
Trace = No\n\
TraceFile = /dev/null\n\
ForceTrace = No\n\
Pooling = No\n\
" >> /etc/odbc.ini \
 && echo "[mssql]\n\
Driver = ODBC Driver 18 for SQL Server\n\
Server = sqlexpress\n\
Port = 1433\n\
Database = spec_qa\n\
Encrypt = Yes\n\
TrustServerCertificate = Yes\n\
" >> /etc/odbc.ini

# Set the working directory to /app
WORKDIR $APP

# Copy the current directory contents into the container at /app
COPY . $APP

# Setup nginx
COPY nginx.default /etc/nginx/sites-available/default
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
  && ln -sf /dev/stderr /var/log/nginx/error.log

# Build help files
RUN libreoffice --norestore --safe-mode --view --convert-to pdf --outdir $APP/help $APP/help/user_guide.docx \
  && libreoffice --norestore --safe-mode --view --convert-to pdf --outdir $APP/help $APP/help/admin_guide.docx \
  && libreoffice --norestore --safe-mode --view --convert-to pdf --outdir $APP/help $APP/help/high_level_design.docx

# Install the dependencies; build the ui folder; publish frontend
RUN pip install --upgrade pip \
  && pip install -r requirements.txt \
  && cd $APP/ui \
  && npm install \
  && npm run build \
  && cd $APP \
  && python manage.py collectstatic --noinput \
  && chmod a+x /app/start-server.sh

EXPOSE 8020
STOPSIGNAL SIGTERM
CMD ["/app/start-server.sh"]
