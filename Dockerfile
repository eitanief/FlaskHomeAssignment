FROM python:3.6
LABEL maintainer="eitaniefrat@gmail.com"
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 7080
ENTRYPOINT ["python"]
CMD ["app/app.py"]
