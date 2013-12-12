from fnpdjango.deploy import DebianGunicorn
from base import Environment


env1 = Environment(
    host = '',
    user = '',
    app_path = '',
    services = [
        DebianGunicorn('')
    ],
    node_bin_path = '/usr/bin',
    npm_bin = 'npm',
)