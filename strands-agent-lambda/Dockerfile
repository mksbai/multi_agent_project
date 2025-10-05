FROM public.ecr.aws/lambda/python:3.11

WORKDIR /var/task

COPY pyproject.toml ./
COPY app ./app
COPY event.sample.json ./event.sample.json

RUN pip install --no-cache-dir .

COPY . .

CMD ["app.handler.handler"]
