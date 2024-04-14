# CLO835_FinalProject_G13

**Final Project:** Deployment of 2-tiered web application to managed K8s cluster on Amazon EKS, with pod auto-scaling and deployment automation.

*Description:*  We're setting up a Kubernetes environment to deploy a web application that is runnig on a MySQL database. First we will deploy the MYSQL, followed by the necessary configurations like secrets and config maps. Then, we will deploy web application, by ensuring it can access the MySQL database. Finally, services are created to expose both MySQL and the web application.