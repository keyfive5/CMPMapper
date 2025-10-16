"""
Version information for CMP Mapper.
"""

__version__ = "1.0.0"
__build_date__ = "2025-01-16"
__build_time__ = "19:15:00"
__last_updated__ = "2025-01-16 19:15:00 UTC"

# Update history
UPDATE_HISTORY = [
    {
        "version": "1.0.0",
        "date": "2025-01-16",
        "time": "19:15:00",
        "changes": [
            "Fixed ButtonType import error in banner detector",
            "Enhanced banner detection patterns for real-world sites",
            "Improved CSS selector generation with UUID filtering",
            "Added support for ideocookie-widget and widget-cookie-banner patterns",
            "More lenient banner detection (reduced keyword requirements)",
            "Better handling of complex class names and problematic IDs",
            "Successfully tested with Margis Pharmacy and Midtown Compounding Pharmacy"
        ]
    }
]

def get_version_info():
    """Get complete version information."""
    return {
        "version": __version__,
        "build_date": __build_date__,
        "build_time": __build_time__,
        "last_updated": __last_updated__,
        "update_history": UPDATE_HISTORY
    }

def print_version_info():
    """Print formatted version information."""
    info = get_version_info()
    print(f"🍪 CMP Mapper v{info['version']}")
    print(f"📅 Built: {info['build_date']} at {info['build_time']}")
    print(f"🕒 Last Updated: {info['last_updated']}")
    
    if UPDATE_HISTORY:
        latest = UPDATE_HISTORY[0]
        print(f"\n🔄 Latest Changes (v{latest['version']}):")
        for change in latest['changes']:
            print(f"  • {change}")
