FROM python:3.11-slim

WORKDIR /app

COPY ./src/ /app

COPY ./pyproject.toml /code/pyproject.toml

RUN pip install /code/.
# dbms.security.allow_csv_import_from_file_urls=TRUE
CMD ["sh","entrypoint.sh"]