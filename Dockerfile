FROM alpine:3.14

WORKDIR /home/alpine

COPY . .

RUN apk --no-cache add linux-headers musl-dev libc-dev gcc curl zip python3 python3-dev py3-pip
RUN apk add mysql-client
RUN pip3 install -r requirements.txt
RUN (crontab -l ; echo "0 */8 * * * /usr/bin/python3.9 /home/alpine/main.py") | crontab -

ENTRYPOINT ["tail"]
CMD ["-f","/dev/null"]