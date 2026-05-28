# ==========================================
# SECURITY GROUP
# ==========================================

resource "aws_security_group" "flask_sg" {

  name = "${var.environment}-flask-security-group"

  ingress {

    description = "SSH"

    from_port = 22
    to_port   = 22

    protocol = "tcp"

    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {

    description = "Flask Application"

    from_port = 5000
    to_port   = 5000

    protocol = "tcp"

    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {

    from_port = 0
    to_port   = 0

    protocol = "-1"

    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.environment}-flask-security-group"
  }
}

# ==========================================
# EC2 INSTANCE
# ==========================================

resource "aws_instance" "flask_server" {

  # Ubuntu AMI
  ami = "ami-0f58b397bc5c1f2e8"

  instance_type = var.instance_type

  key_name = "test"

  iam_instance_profile = "ecr-sample"

  security_groups = [
    aws_security_group.flask_sg.name
  ]

  tags = {
    Name = "${var.environment}-flask-server"
  }

  user_data = <<-EOF
              #!/bin/bash

              # ======================================
              # UPDATE SYSTEM
              # ======================================

              sudo apt update -y

              # ======================================
              # INSTALL DOCKER
              # ======================================

              sudo apt install docker.io -y

              sudo systemctl start docker

              sudo systemctl enable docker

              sudo usermod -aG docker ubuntu

              # ======================================
              # INSTALL AWS CLI
              # ======================================

              sudo apt install unzip curl -y

              curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"

              unzip awscliv2.zip

              sudo ./aws/install

              # ======================================
              # CREATE MONITOR SCRIPT
              # ======================================

              cat << 'MONITOR' > /home/ubuntu/monitor.sh
              #!/bin/bash

              while true
              do

              STATUS=$(curl -s -o /dev/null -w "%%{http_code}" http://localhost:5000/health)

              if [ "$STATUS" -ne 200 ]; then

              curl -X POST -H 'Content-type: application/json' \
              --data '{"text":"PRODUCTION API DOWN"}' \
              "https://hooks.slack.com/services"

              fi

              sleep 30

              done
              MONITOR

              # ======================================
              # MAKE SCRIPT EXECUTABLE
              # ======================================

              chmod +x /home/ubuntu/monitor.sh

              # ======================================
              # RUN MONITOR SCRIPT
              # ======================================

              nohup /home/ubuntu/monitor.sh > /home/ubuntu/monitor.log 2>&1 &
              EOF
}
