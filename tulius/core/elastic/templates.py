
REQUESTS_TEMPLATE = {
    'index_patterns': ['requests_*', 'profile'],
    'template': {
        'settings': {
            "index": {
                "number_of_shards": 3,
                "number_of_replicas": 1,
            }
        },
        'mappings': {
            'properties': {
                '@timestamp': {'type': 'date'},
                'app_name': {'type': 'text'},
                'browser': {'type': 'text'},
                'browser_version': {'type': 'text'},
                'content_length': {'type': 'long'},
                'device': {'type': 'text'},
                'exec_time': {'type': 'float'},
                'host': {'type': 'text'},
                'ip': {'type': 'text'},
                'level': {'type': 'text'},
                'logger_name': {'type': 'text'},
                'message': {'type': 'text'},
                'method': {'type': 'text'},
                'mobile': {'type': 'boolean'},
                'os': {'type': 'text'},
                'os_version': {'type': 'text'},
                'scheme': {'type': 'text'},
                'status_code': {'type': 'long'},
                'thread_id': {'type': 'long'},
                'url_args': {'type': 'text'},
                'url_kwargs': {
                    'properties': {
                        'name': {'type': 'text'},
                        'value': {'type': 'text'},
                    },
                },
                'url_name': {'type': 'text'},
                'user': {
                    'properties': {
                        'id': {'type': 'long'},
                        'title': {'type': 'text'},
                    }
                }
            }
        }
    }
}

LOGGING_TEMPLATE = {
    'index_patterns': ['logging_*', ],
    'template': {
        'settings': {
            'index': {
                "number_of_shards": 3,
                "number_of_replicas": 1,
            }
        },
        'mappings': {
            "properties": {
                '@timestamp': {'type': 'date'},
                'level': {'type': 'text'},
                'logger_name': {'type': 'text'},
                'message': {'type': 'text'},
            }
        }
    }
}
