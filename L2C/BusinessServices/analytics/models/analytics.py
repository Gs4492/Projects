class Analytics:
    def __init__(self, service_name, metric_name, value, timestamp):
        self.service_name = service_name
        self.metric_name = metric_name
        self.value = value
        self.timestamp = timestamp
