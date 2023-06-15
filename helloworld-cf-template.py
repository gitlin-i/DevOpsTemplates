"""클라우드 포메이션 템플릿 생성"""
from troposphere import (
    Base64,
    ec2,
    GetAtt,
    Join,
    Output,
    Parameter,
    Ref,
    Template,
    
    
)
from ipaddress import ip_network
import requests
def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        data = response.json()
        public_ip = data['ip']
        return public_ip
    except requests.RequestException:
        return "110.8.204.148/32"

ApplicationPort = "3000"
PublicCidrIp = get_public_ip()

t = Template()

t.set_description("Effective DevOps in Aws : HelloWorld web application")
t.add_parameter(Parameter(
    "KeyPair",
    Description="Name of an existing EC2 KeyPair to SSH",
    Type="AWS::EC2::KeyPair::KeyName",
    ConstraintDescription="must be the name of an existing EC2 KeyPair.",
))
t.add_resource(ec2.SecurityGroup(
    "SecurityGroup",
    GroupDescription="Allow SSH and TCP/{} acess".format(ApplicationPort),
    SecurityGroupIngress=[
        ec2.SecurityGroupRule(
            IpProtocol="tcp",
            FromPort="22",
            ToPort="22",
            CidrIp=PublicCidrIp,
        ),
        ec2.SecurityGroupRule(
            IpProtocol="tcp",
            FromPort=ApplicationPort,
            ToPort=ApplicationPort,
            CidrIp="0.0.0.0/0",
        ),
    ]
))

ud = Base64(Join('\n',[
    "#!/bin/bash",
    "sudo curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash",
    ". ~/.nvm/nvm.sh",
    "nvm install --lts",
    "wget http://bit.ly/2vESNuc -O /home/ec2-user/helloworld.js",
    "sudo wget https://raw.githubusercontent.com/gitlin-i/DevOpsTemplates/main/helloworld.txt -O /etc/systemd/system/helloworld.service",
    "sudo systemctl enable helloworld.service",
    "sudo systemctl start helloworld.service",
]))

t.add_resource(ec2.Instance(
    "instance",
    ImageId="ami-0462a914135d20297",
    InstanceType="t2.micro",
    SecurityGroups=[Ref("SecurityGroup")],
    KeyName=Ref("KeyPair"),
    UserData=ud,
))

t.add_output(Output(
    "InstancePublicIp",
    Description="Public IP of our instance.",
    Value=GetAtt("instance","PublicIp"),
))

t.add_output(Output(
    "WebUrl",
    Description="Application endpoint",
    Value=Join("",[
        "http://", GetAtt("instance","PublicDnsName"),
        ":",ApplicationPort
    ]),
))

print(t.to_json())