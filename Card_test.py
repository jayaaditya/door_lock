from smartcard.CardMonitoring import CardMonitor, CardObserver
import time
import signal

SELECT = [0x00, 0xA4, 0x00, 0x00, 0x02, 0x3F, 0x05]
SELECTF = [0x00, 0xA4, 0x00, 0x00, 0x02, 0x3F, 0x08]
COMMAND = [0x00, 0xB0, 0x00, 0x00, 0x19]
COMMANDF = [0x00, 0xB0, 0x00, 0x00, 0x20]

def create_log(logfilename, rollno):
    logfile = open(logfilename, 'a+')
    logfile.write(rollno)
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

def fingerprint_read(card):
    connection = card.createConnection()
    connection.connect()
    out, sw1, sw2 = connection.transmit(SELECTF)
    print "%02x %02x" % (sw1, sw2)
    out, sw1, sw2 = connection.transmit(COMMANDF)
    print "%02x %02x" % (sw1, sw2)
    print out


class Card_Read(CardObserver):
    """docstring for Card_Read"""
    def update(self, observable, (addedcards, removedcards)):
        print "Callback update"
        #print addedcards
        for card in addedcards:
            print "Running update"
            rollno = Read_Roll(card)
            print rollno
            roll_list = get_rollnos("Roll_list.txt")
            fingerprint_read(card)
            if rollno in roll_list:
                create_log("Entry_log.txt", rollno)
                print "Access Granted"
                time.sleep(2)
                print "Access Closed"
            else:
                create_log("No_entry log.txt", rollno)
                print "Access Denied"

def Read_Roll(card):
    connection = card.createConnection()
    connection.connect()
    out, _, _ = connection.transmit(SELECT)
    #print "%02x %02x" %(sw1, sw2)
    out, _, _ = connection.transmit(COMMAND)
    #print "%02x %02x" %(sw1, sw2)
    #print out
    data = map(lambda i: chr(i), out[2:out[1]+2])
    #print data
    rollno = "".join(data)
#    print rollno
    return rollno

# print "Script is active"
MONITOR = CardMonitor()
OBSERVER = Card_Read()
MONITOR.addObserver(OBSERVER)
signal.pause()
