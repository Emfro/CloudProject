import time, os, sys
import inspect
from os import environ as env
import sys
from  novaclient import client
import keystoneclient.v3.client as ksclient
from keystoneauth1 import loading
from keystoneauth1 import session

flavor = 'ACCHT18.large'
private_net = 'SNIC 2018/10-30 Internal IPv4 Network'
floating_ip_pool_name = None
floating_ip = None
image_name = 'ACC19_airf01l'
node_name = None
master_host = 'mastervhost'
server_name = 'ACC19_Project'
ssh_key = 'marcusKey'
userdata = None

if len(sys.argv) < 2:
    sys.exit('Usage:\n %s create master/worker nameOfNode \n delete nameOfNode' % sys.argv[0]) 

loader = loading.get_plugin_loader('password')
auth = loader.load_from_options(auth_url=env['OS_AUTH_URL'],
   	                        username=env['OS_USERNAME'],
               	                password=env['OS_PASSWORD'],
                       	        project_name=env['OS_PROJECT_NAME'],
                               	project_id=env['OS_PROJECT_ID'],
                               	user_domain_name=env['OS_USER_DOMAIN_NAME'])

sess = session.Session(auth=auth)
nova = client.Client('2.1', session=sess)

print("user authorization completed.")

if sys.argv[1].lower() == 'create':
	print("Creating " + sys.argv[2] + '...')
	image = nova.images.find(name = image_name)
	flavor = nova.flavors.find(name = flavor)

	if private_net != None:
    		net = nova.networks.find(label = private_net)
    		nics = [{'net-id': net.id}]
	else:
    		sys.exit("private-net not defined.")

#print("Path at terminal when executing this file")
#print(os.getcwd() + "\n")
# cfg_file_path =  os.getcwd()+'/cloud-cfg.txt'
# if os.path.isfile(cfg_file_path):
#     userdata = open(cfg_file_path)
# else:
#     sys.exit("cloud-cfg.txt is not in current working directory")

#	secgroup = nova.security_groups.find(name='default')
	secgroups = ['default']
	if floating_ip_pool_name == None and sys.argv[2].lower() == 'master':
    		floating_ip = nova.floating_ips.create(nova.floating_ip_pools.list()[0].name)

	if sys.argv[2].lower() == 'worker':
		userdata = open('WorkerCloud_config.txt')
		node_name = 'Worker' + sys.argv[3] 
	elif sys.argv[2].lower() == 'master':
		node_name = 'Master'

	instance = nova.servers.create(name='ACC19'+ node_name, image=image, flavor=flavor, nics=nics,security_groups=secgroups, key_name = ssh_key, userdata = userdata)
	inst_status = instance.status
	print("waiting for 10 seconds.. ")
	time.sleep(10)

	while inst_status == 'BUILD':
  	  	print("Instance: "+instance.name+" is in "+inst_status+" state, sleeping for 5 seconds more...")
    		time.sleep(5)
    		instance = nova.servers.get(instance.id)
    		inst_status = instance.status
		print("Instance: "+ instance.name +" is in " + inst_status + "state")

	if floating_ip.ip != None: 
   		instance.add_floating_ip(floating_ip)
   		with open("/home/ubuntu/floating_ip.txt","w") as f:
	       	 	f.write(floating_ip.ip)

if sys.argv[1].lower() == 'delete':
	instances = nova.servers.list()
	for instance in instances:
		if sys.argv[2] in instance.name:
    			print "Killing: " + instance.id
       	 		nova.servers.delete(instance)
    			print "Killed!" 
