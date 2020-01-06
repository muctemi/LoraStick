'''
Ryan Winters
3-5-19
Library for RN2903

This library can be used to send messages between two LoRa devices P2P style,
and to connect end devices to a LoRa gateway.

See README for more details.


command and command_response can send commands to the rn2903
command just sends the command
command_response sends the command and checks for the correct response
'''

import time
import serial
import sys
import glob

def list_serial_ports():
    """ Lists serial port names
https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python
        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    print(result)
    sys.stdout.flush()
    return result
    
def open(name):
    # Configure the serial connection for RN2903. Make sure to check which COM port the device is on!
    ser = serial.Serial(
        #port='/dev/ttyUSB0',#use this format on mac or linux
        #port='COM3',
        port=name,
        baudrate=57600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        xonxoff=False,
        timeout=1
    )
    #print("hi")
    #print(ser.isOpen())
    return ser

#Prints the Status of the Connection, basically just to check that the ser variable is working
def status(ser):
    #print(ser.isOpen())
    #print(ser.name)
    if ser.isOpen():
        return(ser.name, " is connected")
    else:
        return(ser.name, " is not connected")
    
    return

# send the command to the device and print the response
def raw_command(ser,myinput ):
    # (I append a \r\n carriage return and line feed to the characters - this is requested by my device)
    myinput = str(myinput) + '\r\n'
    print("command = " + str(myinput.encode('ascii')))
    ser.write(myinput.encode('ascii'))
    #out = ''
    line1 = ''
    #print (myinput)
    line1 = ser.readline()
    if line1 != '':
        line1 = str(line1)
        line1 = line1[:-5]
        line1 = line1[2:100]
        #print ("RN2903>>"+str(line1))
        #sys.stdout.flush()
        return line1
    return;
    
    
# send the command to the device do nothing with response 
def command(ser,myinput ):
    # (I append a \r\n carriage return and line feed to the characters - this is requested by my device)
    myinput = myinput + '\r\n'
    ser.write(myinput.encode('ascii'))
    #out = ''
    line1 = ''
    #print (myinput)
    line1 = ser.readline()
    if line1 != '':
        line1 = str(line1)
        line1 = line1[:-5]
        line1 = line1[2:100]
        #print ("RN2903>>"+str(line1))
        #sys.stdout.flush()
        #print(line1)
        
    return;

#same as command but it also checks for correct response
def command_response(ser,myinput, resp):
    # (I append a \r\n carriage return and line feed to the characters - this is requested by my device)
    myinput = myinput + '\r\n'
    ser.write(myinput.encode('ascii'))
    #out = ''
    line1 = ''
    #print (myinput)
    line1 = ser.readline()
    if line1 != '':
        line1 = str(line1)
        line1 = line1[:-5]
        line1 = line1[2:100]
        if (line1 != resp):
            print ("Bad Response from RN2903: ",end="")
            print (line1)
            sys.stdout.flush()
            return False
        else:
            return True
        #print(line1)
    return;

def startRX(ser):
    wdt = 60*60*24*1000 #one day in ms
    command(ser,"sys reset")
    command_response(ser,"mac pause", "4294967245")
    command_response(ser,"radio set pwr 14", "ok")
    command_response(ser,"radio set wdt "+str(wdt), "ok")
    return True#TODO add in false case

def startTX(ser):
    wdt = 60*60*24*1000 #one day in ms
    command(ser,"sys reset")
    if(command_response(ser,"mac pause", "4294967245")):
        if(command_response(ser,"radio set pwr 14", "ok")):
            if(command_response(ser,"radio set wdt "+str(wdt), "ok")):
                return True
    return False


def receive(ser):
    #wdt = 60*60*24*1000 #one day in ms
    command_response(ser,"radio rx 0", "ok")
    line1 = ''
    while 1:
        line1 = ser.readline()
        line1 = str(line1)
        line1 = line1[:-5]
        line1 = line1[2:100] 
        #if line1 != '':
        if len(str(line1)) > 0:
            #sys.stdout.write("RN2903>>"+str(line1)+"\n")
            #print("SNR: ")#print out SNR(signal to noise ratio)
            #command("radio get snr")
            command_response(ser,"radio rx 0", "ok")#need to refresh the reciever after every reception
            #sys.stdout.flush()
            #time.sleep(1)
            if(str(line1)=="radio_err"):#if the rx timer ended, then reset it
                command_response(ser,"radio rx 0", "ok")
                return("Radio Timed Out")
                sys.stdout.flush()
            elif ("radio_rx" in line1):#if we recieved data clean it and print it
                line1 = line1[10:1000]
                #print ("Hex: ",line1)#print raw hex values
                line2 = bytes.fromhex(line1).decode('utf-8')
                return("Received: ",line2)
                #command("radio get snr")
                sys.stdout.flush()
                if line2 == 'shutdown':
                    ser.close()
                    return
                #return line2
            else:#placeholder for if something else shows up
                return("Uhh hey not sure what we get here:")
                sys.stdout.write("RN2903>>"+str(line1)+"\n")
            
            sys.stdout.flush()
#ser.isOpen()

def send(ser, myinput):
    command(ser,"radio tx "+myinput.encode('ascii').hex())
    '''if (command_response(ser,"radio tx "+myinput.encode('utf-8').hex(), "radio_tx_ok")):
        return True
    else:
        return False
    '''
    return
    
####################Parameter Functions#####################
def setFreq(ser, myinput):
    if (command_response(ser,"radio set freq "+str(myinput), "ok")):
        return True
    else:
        return False
    return

def setPwr(ser, myinput):
    if (command_response(ser,"radio set pwr "+str(myinput), "ok")):
        return True
    else:
        return False
    return

def setWDT(ser, myinput):
    if (command_response(ser,"radio set wdt "+str(myinput), "ok")):
        return True
    else:
        return False
    return


def setSpr(ser, myinput):
    if (command_response(ser,"radio set sf "+str(myinput), "ok")):
        return True
    else:
        return False
    return


def setBW(ser, myinput):
    if (command_response(ser,"radio set bw "+str(myinput), "ok")):
        return True
    else:
        return False
    return

###########MAC Layer Commands################
    
def getDevEUI(ser):
    return raw_command(ser, "mac get deveui")#use raw_command because it return result
    

def macRecBuf(ser):
    line1 = ""
    #print (myinput)
    line1 = ser.readline()
    if line1 != '':
        line1 = str(line1)
        line1 = line1[:-5]
        line1 = line1[2:100]
        #print ("RN2903>>"+str(line1))
        #sys.stdout.flush()
        return(line1)

def joinOTAA(ser,appEui,appKey):
    print("Attempting to Join OTAA may take up to 30 seconds")
   # command_response(ser,"mac set appeui "+str(appEui), "ok")
   # command_response(ser,"mac set appkey "+str(appKey), "ok")
   # for i in range(8,16):
   #     command_response(ser,"mac set ch status " + str(i) + " on", "ok")
    
    for x in range(25):
        print("OTAA Connection Try # " + str(x+1) )
        line = ''
        line = raw_command(ser,"mac join otaa")
        #line = macRecBuf(ser)
        print(line)
        while(line != "accepted" and line != "denied" and line != "no_free_ch"):
            #keep calling macRecBuf()
            line = macRecBuf(ser)
            #print("Rec: " + line)
            time.sleep(0.25)
            sys.stdout.flush()
        
        #print("here")
        if(line == "accepted"):
            print(line)
            return True
    
    return False


def joinABP(ser,devAddr,nwkSKey,appSKey):
    command_response(ser,"mac set devaddr "+str(devAddr), "ok")
    
    command_response(ser,"mac set nwkskey "+str(nwkSKey), "ok")
    
    command_response(ser,"mac set appskey "+str(appSKey), "ok")
    
    
    for i in range(8,16):
        command_response(ser,"mac set ch status " + str(i) + " on", "ok")
    
    #print(raw_command(ser,"mac join abp"))
    command_response(ser,"mac join abp", "ok")
    if(macRecBuf(ser) != "accepted"):
        return "Error: Not Accepted"
    
    return True


def macSend(ser,msg):
    #print("Here")
    sys.stdout.flush()
    line = ""
    line1 = ""
    line = raw_command(ser, "mac tx uncnf 1 " + str(msg))
    time.sleep(1) #give gateway some time to respond
    #line = line + " " + str(macRecBuf(ser))
    while(line!=line1): #keep adding to line string until macRecBuf returns " mac rx"
        line1 = line + " "
        line = line + " " + str(macRecBuf(ser))
        sys.stdout.flush()
        time.sleep(1)

    return(line)
    #time.sleep(2)
    #print(macRecBuf(ser))


def macReceive(ser):#Note that to receive from gateway we need to send it a msg first
    line = macSend(ser,"01")
    if('mac_rx 1 ' in line):
        print("RX Filter Step")
        line.replace('mac_rx 1 ', '')
    
    return(line)
    
    


