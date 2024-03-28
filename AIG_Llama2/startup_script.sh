#!/bin/bash
cd /home/ec2-user/AIG_Llama2
source environment/bin/activate
echo "starting application" >> /home/ec2-user/startup.log
nohup uvicorn main:app --reload --port 8000 >> /home/ec2-user/startup.log 2>&1 &

