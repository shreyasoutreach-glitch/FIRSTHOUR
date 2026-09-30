import pytest

from app.services.recovery.command import ReadOnlyRecoveryError, execute_command

def test_recovery_execution_is_read_only():
    with pytest.raises(ReadOnlyRecoveryError):
        execute_command(None, None, "USR_TEST")
