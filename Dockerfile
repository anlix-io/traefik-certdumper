FROM python:alpine

ENV ACME_PATH "/root/acme.json"
ENV CERT_DIR "/certs" 

ADD acme_converter.py /
ADD monitor.sh /

RUN apk add --update inotify-tools

CMD /monitor.sh ${ACME_PATH} ${CERT_DIR}

