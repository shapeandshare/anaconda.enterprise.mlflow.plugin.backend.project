""" Authentication / Authorization Helper Functions """

import os

from ae5_tools.api import AEUserSession


def create_session() -> AEUserSession:
    """
    This function is responsible for pulling Anaconda Enterprise credentials out of the environment definition
    and creating an instance of a session.

    Returns
    -------
    session: AEUserSession
        An instance of an Anaconda Enterprise user session.
    """

    # Create the session directly and provide the AE5 config and credentials:
    ae_session: AEUserSession = AEUserSession(
        hostname=os.environ["AE5_HOSTNAME"], username=os.environ["AE5_USERNAME"], password=os.environ["AE5_PASSWORD"]
    )

    # Connect to Anaconda Enterprise
    ae_session._connect(password=ae_session)
    return ae_session
