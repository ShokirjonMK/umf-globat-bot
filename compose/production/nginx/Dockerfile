FROM nginx

RUN addgroup --system django \
    && adduser --system --ingroup django django

ENV APP_HOME=/home/app
ENV LOGS=/home/app/logs

RUN mkdir $APP_HOME
RUN mkdir -p $LOGS



RUN chown -R django:django $APP_HOME

RUN touch $LOGS/nginx-access.log
RUN chown -R django:django $LOGS/nginx-access.log

RUN touch $LOGS/nginx-error.log
RUN chown -R django:django $LOGS/nginx-error.log


RUN rm /etc/nginx/conf.d/default.conf
COPY ./.envs/.production/nginx.conf /etc/nginx/conf.d
