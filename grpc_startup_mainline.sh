#!/bin/bash

NAME="MainlineGrpcServerStartup"
DAEMON=/home/admin/mainline-grpc-device/ni_grpc_device_server
ARGS="/home/admin/mainline-grpc-device/server_config.json"
USER=admin
PIDFILE=/var/run/mainline-grpc-device-startup.pid

do_start() {
    /usr/sbin/start-stop-daemon --start --pidfile $PIDFILE \
    --make-pidfile --background \
    --chuid $USER --exec $DAEMON $ARGS
}

do_stop() {
    /usr/sbin/start-stop-daemon --stop --pidfile $PIDFILE --verbose
}
case "$1" in
    start)
        echo "Starting $NAME"
        do_start
        ;;
    stop)
        echo "Stopping $NAME"
        do_stop
        ;;
    restart)
        echo "Restarting $NAME"
        do_stop
        do_start
        ;;
    *)
        echo "Usage: $0 {start|stop|restart}"
        exit 1
        ;;
    esac
    exit 0