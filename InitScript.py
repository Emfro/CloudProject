import time, os, sys
import inspect
from os import environ as env
import sys
from  novaclient import client
import keystoneclient.v3.client as ksclient
from keystoneauth1 import loading
from keystoneauth1 import session

flavor = 'ACCHT18.normal'
private_net = 'SNIC 2018/10-30 Internal IPv4 Network'
floating_ip_pool_name = None
floating_ip = None
image_name = 'ACC19_airf01l'
worker_id = str(sys.argv[1])
worker_name = 'worker'+str(worker_id)
worker_pwd = 'workerpwd'+str(worker_id)
master_host = 'mastervhost'
server_name = 'ACC19_Project'
ssh_key = 'marcusKey'

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

#secgroup = nova.security_groups.find(name='default')
secgroups = ['default']
if floating_ip_pool_name == None:
    floating_ip = nova.floating_ips.create(nova.floating_ip_pools.list()[0].name)
else:
    sys.exit("Ip pool name not defined")

print("Creating instance ... ")
instance = nova.servers.create(name='ACC19'+worker_name, image=image, flavor=flavor, nics=nics,security_groups=secgroups, key_name = ssh_key)
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
