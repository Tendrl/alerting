# flake8: noqa
data = """---
namespace.tendrl.alerting:
  objects:
    Definition:
      enabled: True
      help: "Definition"
      value: _tendrl/definitions/alerting
      list: _tendrl/definitions/alerting
      attrs:
        master:
          help: Alerting definitions
          type: String
    Config:
      attrs:
        data:
          help: Configuration data of alerting for this Tendrl deployment
          type: str
      enabled: true
      value: _tendrl/config/alerting
      list: _tendrl/config/alerting
      help: alerting integration component configuration
    Alert:
      attrs:
        alert_id:
          help: 'The unique identifier of alert'
          type: String
        node_id:
          help: 'The unique identifier of node on which alert was detected'
          type: String
        time_stamp:
          help: 'The timestamp at which alert was observed'
          type: String
        resource:
          help: 'The resource with problem for which alert was raised'
          type: String
        current_value:
          help: 'The current magnitude(status/utilization) of problem'
          type: String
        tags:
          help: 'Alert specific fields that cannot be generalized for all alerts'
          type: json
        alert_type:
          help: 'The type(status/percentage utilization) of alert'
          type: String
        severity:
          help: 'The severity of alert'
          type: String
        significance:
          help: 'The significance of notifying alert'
          type: String
        ackedby:
          help: 'Entity/person acking the alert'
          type: String
        acked:
          help: 'Indication of whether alert is acked or not'
          type: Boolean
        pid:
          help: 'The id of process raising the alert'
          type: String
        source:
          help: 'The process raising the alert'
          type: String
      enabled: true
      value: alerting/alerts/$Alert.alert_id
      list: alerting/alerts
      help: "alerts"
    NodeAlert:
      attrs:
        alert_id:
          help: 'The unique identifier of alert'
          type: String
        node_id:
          help: 'The unique identifier of node on which alert was detected'
          type: String
        time_stamp:
          help: 'The timestamp at which alert was observed'
          type: String
        resource:
          help: 'The resource with problem for which alert was raised'
          type: String
        current_value:
          help: 'The current magnitude(status/utilization) of problem'
          type: String
        tags:
          help: 'Alert specific fields that cannot be generalized for all alerts'
          type: json
        alert_type:
          help: 'The type(status/percentage utilization) of alert'
          type: String
        severity:
          help: 'The severity of alert'
          type: String
        significance:
          help: 'The significance of notifying alert'
          type: String
        ackedby:
          help: 'Entity/person acking the alert'
          type: String
        acked:
          help: 'Indication of whether alert is acked or not'
          type: Boolean
        pid:
          help: 'The id of process raising the alert'
          type: String
        source:
          help: 'The process raising the alert'
          type: String
      enabled: true
      value: alerting/nodes/$Alert.node_id/$Alert.alert_id
      list: alerting/nodes/$Alert.node_id
      help: "Node alerts"
    ClusterAlert:
      attrs:
        alert_id:
          help: 'The unique identifier of alert'
          type: String
        node_id:
          help: 'The unique identifier of node on which alert was detected'
          type: String
        time_stamp:
          help: 'The timestamp at which alert was observed'
          type: String
        resource:
          help: 'The resource with problem for which alert was raised'
          type: String
        current_value:
          help: 'The current magnitude(status/utilization) of problem'
          type: String
        tags:
          help: 'Alert specific fields that cannot be generalized for all alerts'
          type: json
        alert_type:
          help: 'The type(status/percentage utilization) of alert'
          type: String
        severity:
          help: 'The severity of alert'
          type: String
        significance:
          help: 'The significance of notifying alert'
          type: String
        ackedby:
          help: 'Entity/person acking the alert'
          type: String
        acked:
          help: 'Indication of whether alert is acked or not'
          type: Boolean
        pid:
          help: 'The id of process raising the alert'
          type: String
        source:
          help: 'The process raising the alert'
          type: String
      enabled: true
      value: alerting/clusters/$Alert.tags['cluster_id']/$Alert.alert_id
      list: alerting/clusters/$Alert.tags['cluster_id']
      help: "Cluster alerts"
    NotificationMedia:
      attrs:
        media:
          help: 'The list of supported notification medium'
          type: List
      list: alerting/notification_medium/supported/
      value: alerting/notification_medium/supported/
      help: "Supported means of notification"
      enabled: true
    AlertTypes:
      attrs:
        types: List
        help: 'A dict of integration to types of alerts the integration handles'
      list: alerting/alert_types
      enabled: true
      value: alerting/alert_types
      help: 'Alert types'
    NodeContext:
      attrs:
        machine_id:
          help: "Unique /etc/machine-id"
          type: str
        fqdn:
          help: "FQDN of the Tendrl managed node"
          type: str
        node_id:
          help: "Tendrl ID for the managed node"
          type: str
        tags:
          help: "The tags associated with this node"
          type: str
        status:
          help: "Node status"
          type: str
      enabled: true
      list: nodes/$NodeContext.node_id/NodeContext
      value: nodes/$NodeContext.node_id/NodeContext
      help: Node Context
    TendrlContext:
      enabled: True
      attrs:
        integration_id:
          help: "Tendrl managed id for performance-integration"
          type: String
        sds_name:
          help: "Name of the Tendrl managed sds, eg: 'gluster'"
          type: String
        sds_version:
          help: "Version of the Tendrl managed sds, eg: '3.2.1'"
          type: String
        node_id:
          help: "Tendrl ID for the node"
          type: String
      value: nodes/$NodeContext.node_id/TendrlContext
      list: nodes/$NodeContext.node_id/TendrlContext
      help: "Tendrl context"
    NotificationConfig:
      enabled: True
      attrs:
        config:
          help: "Notification global configuration"
          type: json
      value: notification_settings/
      list: notification_settings/
      help: "Notification configuration"
tendrl_schema_version: 0.3
"""
