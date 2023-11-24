#! bin/bash
sudo yum install git -y
sudo -u ec2-user git clone https://github.com/Karan9861/AdmissionPro.git /home/ec2-user/AdmissionPro
#sudo -u ec2-user git clone -b Supraja_1 https://github.com/Karan9861/AdmissionPro.git /home/ec2-user/AdmissionPro
sudo yum install pip -y
sudo pip install flask
sudo pip install flask_sqlalchemy
sudo pip install mysql-connector-python
sudo python3 /home/ec2-user/AdmissionPro/app.py
