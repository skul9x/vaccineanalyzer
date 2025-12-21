"""
Version information for VaccineAnalyzer
Update this file to change version across the entire application.
"""

# Application Version - Change this to update version everywhere
APP_VERSION = "4.8.4"

# Application Name
APP_NAME = "VaccineAnalyzer"

# Full title for window
APP_TITLE = f"{APP_NAME} V{APP_VERSION} - Clinical Dashboard"

# Short version string for display
VERSION_STRING = f"v{APP_VERSION}"


def get_version():
    """Returns the current application version."""
    return APP_VERSION


def get_full_title():
    """Returns the full application title with version."""
    return APP_TITLE
