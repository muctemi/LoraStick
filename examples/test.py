import rn2903
import time
import sys

def test(ser,count, sf,testMethod):
  rn2903.setSpr(ser,"sf"+str(sf))
  strsf = str(sf)
  start = int(time.time_ns() // 1000000 )
  if ( sf < 10 ):
    strsf = "0"+strsf
 
  for i in range(count):
    str_i = str(i)
    if ( i < 10 ):
      str_i = "0"+str_i
      payload = str_i + strsf + "AA" +str(int(time.time_ns() // 1000000 ))
    if (testMethod == 'ChallangeResp' ):
      simChallangeResp(ser,payload)
    elif(testMethod == '0RTT'):
      sim0RTT(ser,payload)
    
  end = int(time.time_ns() // 1000000 )
  print ("TEST" + sys.argv[1] + ","+ sys.argv[5] +"," + str(count)+ "," +testMethod + "," + "sf"+str(sf) +  ","+str(start) +"," + str(end) +","+ str(end-start)) 
  return
		
def simChallangeResp(ser,payload):
  print("size = " + str(sys.getsizeof(payload.encode('ascii'))))
  rn2903.macSend(ser,payload) #operation command
  rn2903.macReceive(ser) # challange
  rn2903.macSend(ser,payload) # response
  rn2903.macReceive(ser) # ack
  return

def sim0RTT(ser,payload):
  print("size = " + str(sys.getsizeof(payload.encode('ascii'))))
  rn2903.macSend(ser,payload) #operation command with MAC
  #rn2903.macReceive(ser) # response
  return

print("Connect Device")
ser = rn2903.open(sys.argv[1])
#print("Done")
rn2903.joinOTAA(ser,"","")
#count = int(sys.argv[2])
sf = int (sys.argv[2])
#test(ser,count, sf,'ChallangeResp')
while(1):
  #print ("epoch "+ str(int(time.time())) + " " + str(int(sys.argv[3])) )
  if ( int(time.time()) % int(sys.argv[3]) == 0 ):
     test(ser,1, sf,sys.argv[4])
  time.sleep(1)

#dumy="AABBCC"
#ct = "100A"+dumy+str(int(time.time_ns() // 1000000 ))
#print("size = " + str(sys.getsizeof(ct.encode('ascii'))))
#print(ct)
#rt = rn2903.macSend(ser,ct)
#print(rt)
#rt = rn2903.macSend(ser,ct)
#print(rt)
#rt = rn2903.macReceive(ser)
#print(rt)

