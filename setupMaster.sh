cd /home/ubuntu/

sudo pip install Celery
sudo apt-get install rabbitmq-server -y

git clone https://github.com/marcusfroling/CloudProject.git
sudo mkdir /home/ubuntu/naca_airfoil/geo_files/
sudo mkdir /home/ubuntu/naca_airfoil/msh_files/

sudo chmod 755 -R CloudProject

sudo service rabbitmq-server start

sudo rabbitmqctl add_user none none
sudo rabbitmqctl add_vhost nonevhost
sudo rabbitmqctl set_permissions -p nonevhost none ".*" ".*" ".*"
cd /home/ubuntu/CloudProject
screen -d -m python run_airfoil_tasks.py