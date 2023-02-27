from typing import Optional

from anaconda.enterprise.server.common.sdk import demand_env_var
from anaconda.enterprise.server.sdk import AEClient, AESessionFactory, ClientOptions


def get_ae_client(options: Optional[ClientOptions] = None) -> AEClient:
    """
    Get an AE Client

    Parameters
    ----------
    options: Optional[ClientOptions]
        Optional configuration for the client instantiation.

    Returns
    -------
    client: AEClient
        An instance of an AEClient.
    """

    if options is None:
        options_dict: dict = {
            "hostname": demand_env_var(name="AE_HOSTNAME"),
            "username": demand_env_var(name="AE_USERNAME"),
            "password": demand_env_var(name="AE_AUTH"),
        }
        options: ClientOptions = ClientOptions.parse_obj(options_dict)

    session_factory: AESessionFactory = AESessionFactory(options=options)
    return AEClient(session_factory=session_factory)
