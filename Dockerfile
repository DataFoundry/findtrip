FROM registry.dataos.io/library/python:2.7

ADD Qua/requirement.txt /Qua/requirement.txt
ADD phantomjs/bin/phantomjs /usr/bin/phantomjs

RUN apt-get install -y libfontconfig gcc 
RUN pip install -r /Qua/requirement.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
ADD Qua/Qua.py /Qua/Qua.py
ENTRYPOINT ["/Qua/Qua.py"]
