# How to dock the application
	Run the following commands:
	1.	docker login
	2.	docker build . -t trading-application:1.0

# How to deploy the application with Kubernetes
	1. To deploy an application with Kubernetes inside the cloud IDE, we first need to set our current Namespace. Run the following command (linux):
		export NAMESPACE_NAME=`bx cr namespace-list | grep sn-labs- | sed 's/ //g'`