import pkgutil
import tendrl.alerting.constants as alerting_consts
import tendrl.alerting.utils.central_store_util as central_store_util


def list_modules_in_package_path(package_path, prefix):
    modules = []
    path_to_walk = [(package_path, prefix)]
    while len(path_to_walk) > 0:
        curr_path, curr_prefix = path_to_walk.pop()
        for importer, name, ispkg in pkgutil.walk_packages(
            path=[curr_path]
        ):
            if ispkg:
                path_to_walk.append(
                    (
                        '%s/%s/' % (curr_path, name),
                        '%s.%s' % (curr_prefix, name)
                    )
                )
            else:
                modules.append((name, '%s.%s' % (curr_prefix, name)))
    return modules


def parse_resource_alerts(resource_type, resource_classification, **kwargs):
    alerts = {}
    alerts = central_store_util.get_entity_alerts(
        resource_classification,
        **kwargs
    )
    critical_alerts = []
    warning_alerts = []
    for alert in alerts:
        if alert['acked'].lower() == "true":
            continue
        if resource_type:
            for alert_type in alerting_consts.SUPPORTED_ALERT_TYPES:
                if alert['resource'] == '%s_%s' % (resource_type, alert_type):
                    if alert['severity'] == alerting_consts.CRITICAL:
                        critical_alerts.append(alert)
                    if alert['severity'] == alerting_consts.WARNING:
                        warning_alerts.append(alert)
        else:
            if alert['severity'] == alerting_consts.CRITICAL:
                critical_alerts.append(alert)
            if alert['severity'] == alerting_consts.WARNING:
                warning_alerts.append(alert)
    return critical_alerts, warning_alerts
