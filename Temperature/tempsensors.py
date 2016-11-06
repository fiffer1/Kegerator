# File Name: tempsensors.py
# Created By: fiffer1 to be used with KS-kegberry.py (Kegerator_1Tap.py) from Kayser-Sosa

# Code modified from - https://www.modmypi.com/blog/ds18b20-one-wire-digital-temperature-sensor-and-the-raspberry-pi
# Some changes include:
#   Using subprocess instead of os.system as this will be depricated
#   Dynamically loop through all available sensors
#   A file with lookup values is used to give a friendly name to known sensors (file is required to exist, but values don't need to be entered)
#   Ex: <Sensor ID>,<Friendly Name>
#        28-03166166ccff,Tower
#   The friendly name is used as the Key for the dictionary, so must be unique
#   If the sensor id is not in the file, the sensor_name will be set as Undefined

# Output is a Dictionary  {SensorName,Temperature(F)}
#   The temp can be displayed as Celcius by changing the variable used when inserting into dictionary (ie temp_c vs temp_f)


#   Imports ===================================================================================================================
import subprocess
import time
import locale

# Thermometer ID & Setup ===========================================================================================================
tempReadings = '/home/pi/Projects/Temperature/SensorTemps_working.txt'
tempReadingsFinal = '/home/pi/Projects/Temperature/SensorTemps.txt'

subprocess.call(['/sbin/modprobe','w1-gpio'])
subprocess.call(['/sbin/modprobe','w1-therm'])

encoding = locale.getdefaultlocale()[1]

#set the delay between temperature updates in seconds
tempDelay = 45

x = 1

while x==1:
    fileMode = 'w'

    p = subprocess.Popen(['ls', '/sys/bus/w1/devices'], stdout=subprocess.PIPE)
    output, err = p.communicate()

    strout = output

    ##print (strout)
    ##print (strout.split('\n'))

	#File contains known sensors and a friendly name to be displayed. 
    myfile = open('/home/pi/Projects/Temperature/ThermometerLookup.txt','r')
    d = {}
    for line in myfile:
        x = line.split(",")
        a = x[0]
        b = x[1]
        c = len(b)-1 ## Remove \n
        b = b[0:c]
        d[a] = b

    myfile.close

    splitstr = strout.decode(encoding).split('\n')

    for vals in splitstr:
        ##print ("Value=>" + vals)
		#Valid sensors start with '28-'  Everything else is ignored
        if vals.startswith('28-') == True:
			#Open the w1_slave file for the sensor to retrieve the status and temp reading
            sensor_path = '/sys/bus/w1/devices/' + vals + '/w1_slave'

            if vals in d:
                sensor_name = d[vals]
            else:
                sensor_name = 'Undefined'
                
            ##print sensor_name                
            
            def temp_raw():
                f = open(sensor_path,'r')
                lines = f.readlines()
                f.close()
                return lines

            def read_temp():
                lines = temp_raw()

				#YES at the end of the first line means a successful reading was achieved
				#t=xxxx at the end of the second line is the temp in Celcius with no decimal
				#Temp is converted to Fahrenheit and inserted into the Dictionary
                if lines[0].strip()[-3:] != 'YES':
                    temp_f = 999
                else:
                    temp_output = lines[1].find('t=')

                    if temp_output != -1:
                        temp_string = lines[1].strip()[temp_output+2:]
                        temp_c = float(temp_string)/1000.0
                        temp_f = round((temp_c * 9.0 / 5.0 + 32.0),2)
                    else:
                        temp_f = 990

                return temp_f

			# fileMode is first set to write for the first sensor, then append for each additional sensor
            with open(tempReadings,fileMode) as f:
                f.write(sensor_name +' ') 
                f.write(str(round(read_temp(),2)) + '\n') 

            fileMode = 'a'

            #print(sensor_name + ' ' + str(read_temp()))
            
    #When writing to the tempReadings file, there is a delay between sensors.
    #This causes the temp readings in the calling display to blank and change color before populating.
    #Writing to a final file separately, which the Kegerator file uses, the blanking won't occur.
    cmd = ['cp',tempReadings,tempReadingsFinal]
    subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    
    time.sleep(tempDelay)
    x=1
