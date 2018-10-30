import time, os, sys
import inspect
from os import environ as env
import sys
from  novaclient import client
import keystoneclient.v3.client as ksclient
from keystoneauth1 import loading
from keystoneauth1 import session

flavor = "ACCHT18.normal"
private_net = 'g2015034-net_2'
floating_ip_pool_name = 'public'
floating_ip = None
image_name = 'ACC19_airf01l'
worker_id = str(sys.argv[1])
worker_name = 'worker'+str(id)
worker_pwd = 'workerpwd'+str(id)
master_host = "mastervhost"

loader = loading.get_plugin_loader('password')

auth = loader.load_from_options(auth_url=env['OS_AUTH_URL'],
                                username=env['OS_USERNAME'],
                                password=env['OS_PASSWORD'],
                                project_name=env['OS_PROJECT_NAME'],
                                project_domain_name=env['OS_USER_DOMAIN_NAME'],
                                project_id=env['OS_PROJECT_ID'],
                                user_domain_name=env['OS_USER_DOMAIN_NAME'])

sess = session.Session(auth=auth)
nova = client.Client('2.1', session=sess)
print "user authorization completed."

image = nova.glance.find_image(image_name)

flavor = nova.flavors.find(name=flavor)

if private_net != None:
    net = nova.neutron.find_network(private_net)
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

secgroup = nova.security_groups.find(name='default')
secgroups = [secgroup.id]
if floating_ip_pool_name != None:
    floating_ip = nova.floating_ips.create(floating_ip_pool_name)
else:
    sys.exit("Ip pool name not defined")

print "Creating instance ... "
instance = nova.servers.create(name='ACC19'+worker_name, image=image, flavor=flavor, nics=nics,security_groups=secgroups, key_name = 'acc19')
inst_status = instance.status
print "waiting for 10 seconds.. "
time.sleep(10)

while inst_status == 'BUILD':
    print "Instance: "+instance.name+" is in "+inst_status+" state, sleeping for 5 seconds more..."
    time.sleep(5)
    instance = nova.servers.get(instance.id)
    inst_status = instance.status

print "Instance: "+ instance.name +" is in " + inst_status + "state"