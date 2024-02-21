@set ServerIP = "192.168.2.55"

@echo *************************  Analog Input *************************
@cd C:\git\Tesla_BMS_HILTester\examples\nidaqmx
@python -m analog-input_Vincent "192.168.2.55"
@cd ..

@echo ************************  Analog Output *************************
@cd C:\git\Tesla_BMS_HILTester\examples\nidaqmx
@python analog-output_Vincent.py "192.168.2.55"
@cd ..

@echo *************************  DMM Input  ***************************
@cd C:\git\Tesla_BMS_HILTester\examples\nidmm
@python dmm_acquire_multiple-points.py "192.168.2.55"
@cd ..

@echo **************************  DC Power  ***************************
@cd C:\git\Tesla_BMS_HILTester\examples\nidcpower
@python dcpower_measure-record.py "192.168.2.55"
@cd ..

@echo **************************  FPGA RMIO  ***************************
@cd C:\git\Tesla_BMS_HILTester\examples\nifpga
@python fpga_Basic.py "192.168.2.55"
@cd ..

@echo(
@echo -------------------  Measurements Completed  -------------------
@pause