import os
import sys
import select
import paramiko
import time
import SelfTest_CF

pidof_ni_grpc_device_server=None

class Commands:
    start_command=('cd /home/admin/grpc-device/cmake/build;export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$(pwd)/grpc-sideband;./ni_grpc_device_server')    
    pidof_gprc_device_server_command=('pidof ni_grpc_device_server')    

    def __init__(self, retry_time=0):
        self.retry_time = retry_time
        pass

    def Start_cmd(self, host_ip, gRPC_ServerMachine_UserName, gRPC_ServerMachine_Password):
        i = 0
        while True:
            SelfTest_CF.Display_Debug_Info("[gRPC Server] Trying to connect to %s (%i/%i)" % (host_ip, i, self.retry_time))
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                #ssh.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
                ssh.connect(host_ip, username=gRPC_ServerMachine_UserName, password=gRPC_ServerMachine_Password, port=22)
                break
            except paramiko.AuthenticationException:
                SelfTest_CF.Display_Debug_Info("[gRPC Server] Authentication failed when connecting to %s" % host_ip)
                sys.exit(1)
            except paramiko.SSHException:
                SelfTest_CF.Display_Debug_Info("[gRPC Server] SSH Exception. It failed when connecting to %s" % host_ip)
                sys.exit(1)
            except:
                SelfTest_CF.Display_Debug_Info("[gRPC Server] Could not SSH to %s, waiting for it to start" % host_ip)
                i += 1
                time.sleep(2)

            # If we could not connect within time limit
            if i >= self.retry_time:
                SelfTest_CF.Display_Debug_Info("[gRPC Server] Could not connect to %s. Giving up" % host_ip)
                sys.exit(1)

        # Send the pidof command, we want to check, first that there is no instance running.
        SelfTest_CF.Display_Debug_Info('[gRPC Server] >pidof ni_grpc_device_server')
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("pidof ni_grpc_device_server")
        exit_code = ssh_stdout.channel.recv_exit_status() # handles async exit error 
        if exit_code==0:
            pidof_ni_grpc_device_server=''
            for line in ssh_stdout:
                    pidof_ni_grpc_device_server= line.strip()
                    SelfTest_CF.Display_Debug_Info('[gRPC Server] >'+pidof_ni_grpc_device_server)
            
            if pidof_ni_grpc_device_server!='':
                # Send the kill command
                kill_command="kill "+str(pidof_ni_grpc_device_server)
                SelfTest_CF.Display_Debug_Info('[gRPC Server] >kill '+pidof_ni_grpc_device_server)
                ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(kill_command)
                exit_code = ssh_stdout.channel.recv_exit_status() # handles async exit error 

                for line in ssh_stdout:
                        SelfTest_CF.Display_Debug_Info(line.strip())
        SelfTest_CF.Display_Debug_Info(f'[gRPC Server] >{self.start_command}')
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(self.start_command)
        time.sleep(1.0)
        SelfTest_CF.Display_Debug_Info(f'[gRPC Server] >{self.pidof_gprc_device_server_command}')
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(self.pidof_gprc_device_server_command)
        exit_code = ssh_stdout.channel.recv_exit_status() # handles async exit error 
        for line in ssh_stdout:
            SelfTest_CF.Display_Debug_Info('[gRPC Server] >'+line.strip())            
        # Close SSH connection
        ssh.close()

      
    def Stop_cmd(self, host_ip, gRPC_ServerMachine_UserName, gRPC_ServerMachine_Password):
        i = 0
        while True:
            SelfTest_CF.Display_Debug_Info("[gRPC Server] Trying to connect to %s (%i/%i)" % (host_ip, i, self.retry_time))
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                #ssh.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
                ssh.connect(host_ip, username=gRPC_ServerMachine_UserName, password=gRPC_ServerMachine_Password, port=22)
                break
            except paramiko.AuthenticationException:
                SelfTest_CF.Display_Debug_Info("[gRPC Server] Authentication failed when connecting to %s" % host_ip)
                sys.exit(1)
            except:
                SelfTest_CF.Display_Debug_Info("[gRPC Server] Could not SSH to %s, waiting for it to start" % host_ip)
                i += 1
                time.sleep(2)

            # If we could not connect within time limit
            if i >= self.retry_time:
                SelfTest_CF.Display_Debug_Info("[gRPC Server] Could not connect to %s. Giving up" % host_ip)
                sys.exit(1)
        # After connection is successful
        # Send the pidof command
        SelfTest_CF.Display_Debug_Info('[gRPC Server] >pidof ni_grpc_device_server')
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("pidof ni_grpc_device_server")
        exit_code = ssh_stdout.channel.recv_exit_status() # handles async exit error 
        if exit_code==0:
            for line in ssh_stdout:
                    pidof_ni_grpc_device_server= line.strip()
                    SelfTest_CF.Display_Debug_Info('[gRPC Server] >'+pidof_ni_grpc_device_server)
            
            # Send the kill command
            kill_command="kill "+str(pidof_ni_grpc_device_server)
            SelfTest_CF.Display_Debug_Info('[gRPC Server] >kill '+pidof_ni_grpc_device_server)
            ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(kill_command)
            exit_code = ssh_stdout.channel.recv_exit_status() # handles async exit error 

            for line in ssh_stdout:
                    SelfTest_CF.Display_Debug_Info(line.strip())
        else:
           SelfTest_CF.Display_Debug_Info('[gRPC Server] PID not found. Server doesn''t seem to be running.') 
        # Close SSH connection
        ssh.close()

        return


def Start_gRPC_Server(ServerIP, gRPC_ServerMachine_UserName, gRPC_ServerMachine_Password):
    MyCommands = Commands()
    MyCommands.Start_cmd(ServerIP,gRPC_ServerMachine_UserName, gRPC_ServerMachine_Password)
    #MyCommands.Start_cmd(ServerIP,gRPC_ServerMachine_UserName, gRPC_ServerMachine_Password,'ls -l')
    #print "This method is not meant to be used directly"
    return

def Stop_gRPC_Server(ServerIP, gRPC_ServerMachine_UserName, gRPC_ServerMachine_Password):
    MyCommands = Commands()
    #MyCommands.run_cmd(ServerIP,gRPC_ServerMachine_UserName, gRPC_ServerMachine_Password,'bash StartServer.sh')
    MyCommands.Stop_cmd(ServerIP,gRPC_ServerMachine_UserName, gRPC_ServerMachine_Password)
    #print "This method is not meant to be used directly"
    return
