============
Installation
============

Note: node-agent is required for logging(functional dependency)

1. Install Notifier yum install tendrl-notifier::

   yum install tendrl-notifier

2. Configure notifier::

    Open /etc/tendrl/notifier/notifier.conf.yaml
   
    update -->

    etcd_connection = <IP of etcd server>

3. Configure email source::

    Open /etc/tendrl/notifier/email.conf.yaml
   
    update -->

    email_id = <The sender email id>

    email_smtp_server = <The smtp server>

    email_smtp_port = <The smtp port>


    Note: If SMTP server supports only authenticated email, 
    follow the template as in: /etc/tendrl/notifier/email_auth.conf.yaml.sample
          And accordingly enable the following:

        auth = <ssl/tls>

        email_pass = <password corresponding to email_id for authenticating to smtp server>

4. Enable and start notifier service::

   systemctl enable tendrl-notifier

   systemctl start tendrl-notifier

Note: 

1. All nodes need to have tendrl-user added to tendrl group created by node-agent

``useradd tendrl-user -g tendrl``

2. For more detailed steps please follow: 
https://github.com/Tendrl/documentation/wiki/Tendrl-Package-Installation-Reference

