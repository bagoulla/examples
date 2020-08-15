FROM centos:7
RUN yum install -y epel-release && yum clean all
RUN yum install -y python-zmq && yum clean all
COPY pubsub.py /usr/bin/pubsub

