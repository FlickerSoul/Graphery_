from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

import backend.channels.routing

application = ProtocolTypeRouter({
    'websocket':
        AllowedHostsOriginValidator(
            URLRouter(
                backend.channels.routing.websocket_urlpatterns
            )
        )
})
