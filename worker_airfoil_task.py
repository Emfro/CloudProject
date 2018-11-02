import time
import subprocess
import os
import re
import sys
import swiftclient
from celery import Celery

with open('floating_ip.txt', 'r') as float_ip:
	floating_ip = float_ip.readline()
app = Celery('tasks',backend='amqp://',broker='amqp://none:none@'+floating_ip+'/nonevhost')

#Reads the values in drag_ligit.m which has three columns: time, lift, drag. Calculates the mean values of the columns lift and drag and returns them in a dict.
def convert(file_name,angle):
     convertedList = list()
     Lift = 0
     Drag = 0
     i = 0
     with open('/home/ubuntu/code/test_celery/'+file_name+'results/drag_ligt.m') as input_file:
          for _ in xrange(30):
	       next(input_file)
	  for line in input_file:
               a = line.split()
               Lift +=float(a[1])
               Drag +=float(a[2])
               i += 1
     Lift = Lift/i
     Drag = Drag/i
     return {'Angle': angle, 'Lift': Lift, 'Drag': Drag}


@app.task
def airfoilCalc(file_name, samples=10, viscosity=0.0001, speed=10.,airtime=1):

		swift_conn = swiftclient.client.Connection(OS_AUTH_URL='https://uppmax.cloud.snic.se:5000/v3', user='snic', key='marcusKey', 'OS_PROJECT_NAME': 'SNIC 2018/10-30', auth_version='3', os_options={'OS_PROJECT_ID': '2344cddf33a1412b846290a9fb90b762', 'region_name': 'UPPMAX'})
		(headers, containers) = swift_conn.get_account()
		#container_name = 'Container'
	        dicti = {}
		listOfResults = []
		pathToXmls = '/home/ubuntu/naca_airfoil/msh_files/'

		os.system('sudo chmod 777 -R /home/ubuntu/code/')
		
                obj_tuple = swift_conn.get_object(container_name, file_name)
                with open(pathToXmls+file_name, 'w') as xmlfile:
 	             xmlfile.write(obj_tuple[1])
               	print "Doing airfoil on: " + file_name
		time.sleep(2)
		os.system('sudo chmod 777 -R ' + pathToXmls)
                subprocess.call(['sudo', '/home/ubuntu/naca_airfoil/navier_stokes_solver/./airfoil', str(samples), str(viscosity), str(speed), str(airtime), pathToXmls+file_name])
	        os.system('sudo mkdir /home/ubuntu/code/test_celery/'+file_name+'results')
		os.system('sudo chmod 777 -R /home/ubuntu/code/test_celery/results/')
         	os.system('sudo mv /home/ubuntu/code/test_celery/results/drag_ligt.m /home/ubuntu/code/test_celery/'+file_name+'results')
		angle = re.search('a(.+?)n', file_name)
		if angle:
		     angle = angle.group(1)
	             dicti = convert(file_name,int(angle))			
			  #listOfResults.append(dicti)

				
		#for data in swift_conn.get_container(container_name)[1]:
                #     print '{0}\t{1}\t{2}'.format(data['name'], data['bytes'], data['last_modified'])
		#listOfResults = sorted(listOfResults, key=lambda k: k['Angle'])     
		#for dicti in listOfResults:
                 #    print dicti                                                                                                               

                return str(dicti)
