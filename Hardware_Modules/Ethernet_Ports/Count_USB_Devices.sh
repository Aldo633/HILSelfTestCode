#!/bin/bash                                                            
#Count_USB_Devices.sh

if [ $# -eq 2 ]
then
    Vendor_ID=$1
    Product_ID=$2
else
    #Ensure it matches the USB->Ethernet adapter.
    Vendor_ID=0930
    Product_ID=1400
fi

#echo "Vendor_ID used: $Vendor_ID, Product_ID used: $Product_ID"
#We want to detect all devices with Vendor_ID and Product_ID:
Devices_Info=($(lsusb -d "$Vendor_ID":"$Product_ID" | awk '/Device/ {print substr($2, 0, 3); print substr($4, 0, 3) }'))

#echo "Devices_Info"
NB_Devices=0
NB_Devices=$(( ${#Devices_Info[@]} / 2 ))
echo "$NB_Devices"

