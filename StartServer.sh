#!/bin/bash
echo -e "\n***********************  Start gRPC Device Server ***************************\n"
cd /home/admin/grpc-device/cmake/build
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$(pwd)/grpc-sideband
./ni_grpc_device_server

