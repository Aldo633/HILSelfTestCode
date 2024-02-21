#!/bin/bash
echo "*************************  Analog Input *************************  "
cd /home/admin/grpc-device/examples/nidaqmx
python -m analog-input_Vincent
cd ..

echo "*************************  Analog Output *************************  "
cd /home/admin/grpc-device/examples/nidaqmx
python analog-output_Vincent.py
cd ..

echo "*************************  DMM Input  *************************  "
cd /home/admin/grpc-device/examples/nidmm
python dmm_acquire_multiple-points.py
cd ..

echo "*************************  DC Power  *************************  "
cd /home/admin/grpc-device/examples/nidcpower
python dcpower_measure-record.py
cd ..

echo "************************  FPGA RMIO  *************************  "
cd /home/admin/grpc-device/examples/nifpga
python fpga_Basic.py
cd ..