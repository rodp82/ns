import threading
import time
import datetime
import can
import copy
    
########################################################################
class CANListener(can.Listener):
    
    def __init__(self):
        self.messages = []
                 
    def on_message_received(self, msg):
        m = CANMessage(msg)
        #print(msg)
        self.messages.append(m)
        
    def get_messages(self):
        return self.messages[:]
    
    def clear_messages(self):
        self.messages = []
        
########################################################################
class CANReceiver(threading.Thread):
    """CAN Receiver"""

    #----------------------------------------------------------------------
    def __init__(self, channel, event, timer):
        """Constructor"""
        
        threading.Thread.__init__(self)
        
        self.channel = channel
        self.event = event
        self.timer = timer
        self.unique_messages = {}
        
        print("connecting to can interface")
        self.bus = can.interface.Bus(channel=self.channel, bustype='socketcan_native')
        self.a_listener = CANListener() 
        self.notifier = can.Notifier(self.bus, [self.a_listener])
        
    #----------------------------------------------------------------------
    def run(self):
        """Run Function - runs when thread.start() is called"""               
        
        while self.event.is_set():
            
            ##creates a DEEP copy of the message list
            #messages = data_messages[:]
            ##deletes the contents of the recived_messages list so it can be repopulated
            #del(data_messages[:])
            
            buffered_messages = self.a_listener.get_messages()
            self.a_listener.clear_messages()
            
            #grabs the unique ID's
            unique_ids = list({m.arbitration_id for m in buffered_messages})
            
            #iterates through the ID's and gets the first instance of each unique one
            for i in unique_ids:
                loop_msg = next( obj for obj in buffered_messages if obj.arbitration_id == i)
                date_str = loop_msg.timestamp
                if date_str not in self.unique_messages:
                    self.unique_messages[date_str] = []
                    
                self.unique_messages[date_str].append(loop_msg) 
                
                #self.unique_messages.append(loop_msg)            
            
            time.sleep(self.timer)
            
    #----------------------------------------------------------------------
    def read_messages(self):
        """Reads the messages in the array"""
        
        messages = copy.deepcopy(dict(self.unique_messages))
        self.unique_messages.clear()
        return messages
    
        ##creates a DEEP copy of the message list
        #messages = data_messages[:]
        ##deletes the contents of the recived_messages list so it can be repopulated
        #del(data_messages[:])
        
        ##grabs the unique ID's
        #unique_ids = list({m.arbitration_id for m in messages})
        
        ##iterates through the ID's and gets the first instance of each unique one
        #unique_messages = []
        #for i in unique_ids:
            #loop_msg = next( obj for obj in messages if obj.arbitration_id == i)
            #unique_messages.append(loop_msg)
            ##loop_msg.printme()        
        
        #return unique_messages
 
########################################################################
class CANMessage():
    
    def __init__(self,msg):
        self.msg = msg
        self.datetime = datetime.datetime.fromtimestamp(msg.timestamp).strftime('%Y-%m-%d %H:%M:%S')
        self.timestamp = str(msg.timestamp).split(".")[0]
        self.arbitration_id = msg.arbitration_id
        self.data = msg.data
    
    def get_timestamp(self):
        return datetime.datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S')
        
    def print_me(self):
        print(self.msg)
        
    def __str__(self):
        field_strings = []
        if self.msg.id_type:
            # Extended arbitrationID
            arbitration_id_string = "%.8x" % self.arbitration_id
        else:
            arbitration_id_string = "%.4x" % self.arbitration_id
        field_strings.append(arbitration_id_string)

        
        data_strings = []
        if self.data is not None:
            for byte in self.data:
                data_strings.append("%.2x" % byte)
        
        field_strings.append("".join(data_strings))

        return " ".join(field_strings).strip()
            
        
    def __key(self):
        return self.arbitration_id
   
    def __hash__(self):
        return hash(self.arbitration_id)
    
    