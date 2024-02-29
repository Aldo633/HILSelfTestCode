#!/bin/bash                                                            
#Get_USB_Devices_Information.sh

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
NB_Devices=$(( ${#Devices_Info[@]} / 2 ))
#echo "NB Devices: $NB_Devices"
#echo "Bus Dev Bus Dev ..."
#echo "${Devices_Info[*]}"

#echo "Device_IDs_Decimal:"
i=0
Devices_Info_Decimal=()

if (($NB_Devices > 0)); then
    for ((i = 0; i < ${#Devices_Info[@]}; i++)); do
        #echo -ne "${Devices_Info[$i]}\t"
        Devices_Info_Decimal[$i]=${Devices_Info[$i]#"${Devices_Info[$i]%%[!0]*}"}
        #echo "${Devices_Info_Decimal[$i]}"
    done

    #echo "Size: $(( ${#Devices_Info_Decimal[@]} / 2 )) "
    #echo "${Devices_Info_Decimal[*]}"

    Array_Ports=()
    Serial_Numbers=()

    for ((i = 0; i < $NB_Devices; i++)); do
            Index=$(( $i * 2 ))
            Dev_Index=$(( ($i * 2) + 1 ))
            #Read Serial Number
            Serial_Numbers[$i]=$(lsusb -s "${Devices_Info[$Index]}":"${Devices_Info[$Dev_Index]}" -v | awk '/iSerial/ {print substr($3, 0, 32)}')
            #echo "Serial Number: ${Serial_Numbers[$i]}"
            #Read Tree Information:
            Bus_To_Search=$(printf "Bus %02d.Port" ${Devices_Info_Decimal[$Index]})
            Dev_To_Search=$(printf "Dev %d" ${Devices_Info_Decimal[$Dev_Index]})
            Bus_Result_String=($(lsusb -t | awk -v var0="$Bus_To_Search" -v var1="$Dev_To_Search" 'sub(var0,""){f=1} f{if (sub(var1,"")) f=0; print($3)}'))
            #echo "${Bus_Result_String[*]}"
            NB_Fields=${#Bus_Result_String[@]}
            #echo "Size: $NB_Fields"
            Index=$(( $NB_Fields - 1 ))
            #echo "$Index"
            #echo "${Bus_Result_String[$Index]}"
            Array_Ports[$i]=$(echo "${Bus_Result_String[$Index]}" | sed 's/[^0-9]*//g')
    done

    #Display Results
    echo -ne "Bus\t"
    echo -ne "Dev\t"
    echo -ne "Port\t"
    echo "Serial_Number"
    for ((i = 0; i < $NB_Devices; i++)); do
        Bus_Index=$(( $i * 2 ))
        Dev_Index=$(( ($i * 2) + 1 ))
        echo -ne "${Devices_Info_Decimal[$Bus_Index]}\t"
        echo -ne "${Devices_Info_Decimal[$Dev_Index]}\t"
        echo -ne "${Array_Ports[$i]}\t"
        echo "${Serial_Numbers[$i]}"
    done
fi

