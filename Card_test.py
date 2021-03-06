import os
from smartcard.CardMonitoring import CardMonitor, CardObserver
import RPi.GPIO as GPIO
import time
import datetime
import signal
#this is to demonstrate git
#SELECT = [0x00, 0xA4, 0x00, 0x00, 0x02, 0x3F, 0x05]
#SELECTF = [0x00, 0xA4, 0x00, 0x00, 0x02, 0x3F, 0x08]
#COMMAND = [0x00, 0xB0, 0x00, 0x00, 0xA0]
#COMMANDF = [0x00, 0xB0, 0x00, 0x00, 0x20]
class getDetails(object):
	"""docstring for getDetails"""
	def __init__(self, connection):
		self.SELECT = [0x00, 0xA4, 0x00, 0x00, 0x02, 0x3F, 0x05]
		self.READ_BINARY = [0x00, 0xB0, 0x00, 0x00, 0xE8]
		self.data = self.send(self.SELECT, self.READ_BINARY, connection)
		#print self.data

	def send(self, SELECT, COMMAND, connection):
		#print "Sending Commands"
		out, sw1, sw2 = connection.transmit(SELECT)
		#print sw1, sw2, out
		out, sw1, sw2 = connection.transmit(COMMAND)
		#print sw1, sw2, out
		return out

	def Prt(self):
		print self.data

	def format(self, tag_index):
		#print "Problem with format??"
		return "".join(map(lambda x : chr(x), self.data[tag_index+2:tag_index+self.data[tag_index+1]+2]))

	def getRollno(self):
		rollno = "".join(map(lambda x :chr(x), self.data[2:self.data[1]+2]))
		return rollno

	def getName(self):
		#print "Running getName"
		nlist = []
		try:
			tag_index = self.data.index(194)
            nlist.append(self.format(tag_index))
        except ValueError:
            pass
		try:
			tag_index = self.data.index(195)
			nlist.append(self.format(tag_index))
        except ValueError:
            pass
		try:
			tag_index = self.data.index(193)
			nlist.append(self.format(tag_index))
        except ValueError:
            pass
		name = " ".join(nlist)
		return name
	
	def getCity(self):
		tag_index = self.data.index(196)
		return self.format(tag_index)

	def getBloodGroup(self):
		return self.format(self.data.index(197))

	def getCaste(self):
		return self.format(self.data.index(198))

	def getGuardianName(self):
		return self.format(self.data.index(199))

	def getunknown1(self):
		return self.format(self.data.index(203))

	def getunkown2(self):
  		return self.format(self.data.index(204))
  	
  	def getStream(self):
  	   	return self.format(self.data.index(206))

  	def getBranch(self):
  		return self.format(self.data.index(207))

  	def getExpiryDate(self):
  		info = self.format(self.data.index(218))
  		year = int(info[0:4])
  		month = int(info[4:6])
  		day = int(info[6:8])
  		return year, month, day
  	
  	def getEmail(self):
  		return self.format(self.data.index(216))

def create_log(logfilename, rollno, name):
    logfile = open(logfilename, 'a+')
    logfile.write(rollno)
    logfile.write(" ")
    logfile.write(name)
    logfile.write("\n")
    logfile.close()

def get_rollnos(logfilename):
    logfile = open(logfilename)
    roll_list = logfile.read()
    rollnos = roll_list.split(",")
    logfile.close()
    return rollnos

def check_roll(in_roll, list_roll):
    if in_roll in list_roll:
        return True
    else:
        return False

def check_date(day, month, year):
	now = datetime.datetime.now()
	sysyear = int(now.year)
	sysmonth = int(now.month)
	sysday = int(now.day)
	if year > sysyear:
		return True
	elif year == sysyear:
		if month > sysmonth:
			return True
		elif month == sysmonth:
			if day >= sysday:
				return True
			else :
				return False
		else :
			return False
	else :
		return False

class Card_Read(CardObserver):
    """docstring for Card_Read"""
    def update(self, observable, (addedcards, removedcards)):
        print "Callback update"
        #print addedcards
        for card in addedcards:
            print "Running update"
            connection = card.createConnection()
            connection.connect()
            gdetails = getDetails(connection)
            rollno = gdetails.getRollno()
            print rollno
            name = gdetails.getName()
            print name
            year, month, day =gdetails.getExpiryDate()	
            #print gdetails.getDOB()
            #print gdetails.getNationalityCode()
            #print gdetails.getGender()
            #print gdetails.getPrintDate()
            roll_list = get_rollnos("Roll_list.txt")
            #fingerprint_read(connection)
            #eadEF5(connection)
            if check_roll(rollno, roll_list) and check_date(day, month, year):
                create_log("Entry_log.txt", rollno, name)
                GPIO.output(16,GPIO.LOW)
		os.system("echo 1 | sudo tee /sys/class/leds/led0/brightness")
                print "Access Granted"
                time.sleep(5)
                GPIO.output(16,GPIO.HIGH)
		os.system("echo 0 | sudo tee /sys/class/leds/led0/brightness")
                print "Access Closed"
            else:
                create_log("No_entry log.txt", rollno, name)
                print "Access Denied"

# print "Script is active"
GPIO.setmode(GPIO.BCM)
GPIO.setup(16,GPIO.OUT)
GPIO.output(16,GPIO.HIGH)
MONITOR = CardMonitor()
OBSERVER = Card_Read()
MONITOR.addObserver(OBSERVER)
signal.pause()
