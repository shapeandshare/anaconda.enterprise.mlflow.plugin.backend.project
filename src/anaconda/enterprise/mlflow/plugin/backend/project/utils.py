""" Authentication / Authorization Helper Functions """

from ae5_tools.api import AEUserSession

from anaconda.enterprise.server.common.sdk import demand_env_var, load_ae5_user_secrets


def create_session() -> AEUserSession:
    """
    This function is responsible for pulling Anaconda Enterprise credentials out of the environment definition
    and creating an instance of a session.

    Returns
    -------
    session: AEUserSession
        An instance of an Anaconda Enterprise user session.
    """

    # Load defined environmental variables
    load_ae5_user_secrets()

    # Create the session directly and provide the AE5 config and credentials:
    ae_session: AEUserSession = AEUserSession(
        hostname=demand_env_var(name="AE5_HOSTNAME"),
        username=demand_env_var(name="AE5_USERNAME"),
        password=demand_env_var(name="AE5_PASSWORD"),
    )

    # Connect to Anaconda Enterprise
    # This is currently accomplished this by accessing a private method.
    # pylint: disable=protected-access
    ae_session._connect(password=ae_session)
    return ae_session
