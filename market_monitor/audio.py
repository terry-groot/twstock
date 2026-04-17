"""Audio alert functionality."""

import sys

# Platform-specific beep implementations
try:
    import winsound

    def beep_alert(frequency: int = 1000, duration: int = 500) -> None:
        """Play beep sound on Windows.

        Args:
            frequency: Frequency in Hz (default 1000)
            duration: Duration in milliseconds (default 500)
        """
        try:
            winsound.Beep(frequency, duration)
        except Exception:
            # Fallback to console beep if winsound fails
            print("\a", end="", flush=True)

except ImportError:
    # Unix/Linux/macOS fallback
    def beep_alert(frequency: int = 1000, duration: int = 500) -> None:
        """Play beep sound on Unix-like systems.

        Args:
            frequency: Frequency in Hz (ignored on Unix, for API compatibility)
            duration: Duration in milliseconds (ignored on Unix, for API compatibility)
        """
        print("\a", end="", flush=True)


def should_beep(has_critical_alert: bool, beep_enabled: bool = True) -> bool:
    """Determine if a beep should be played.

    Args:
        has_critical_alert: Whether critical (red) alert is present
        beep_enabled: Whether beeping is enabled

    Returns:
        True if beep should be played
    """
    return has_critical_alert and beep_enabled
