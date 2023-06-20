from unittest.mock import MagicMock

import pytest
from _pytest.fixtures import FixtureRequest
from pytest_mock import MockFixture

from overhave import OverhaveEmulationSettings
from overhave.emulation import Emulator
from overhave.storage import EmulationRunModel, EmulationStorage
from overhave.transport import EmulationData, EmulationTask


@pytest.fixture(scope="module")
def envs_for_mock() -> dict[str, str | None]:
    return {
        "OVERHAVE_EMULATION_BASE_CMD": "overhave emulate",
    }


@pytest.fixture(scope="module")
def mock_default_value() -> str:
    return ""


@pytest.fixture()
def emulation_settings(mock_envs: None) -> OverhaveEmulationSettings:
    return OverhaveEmulationSettings()


@pytest.fixture()
def emulator(
    test_emulation_storage: EmulationStorage, emulation_settings: OverhaveEmulationSettings, mock_envs: None
) -> Emulator:
    return Emulator(settings=emulation_settings, storage=test_emulation_storage)


@pytest.fixture()
def emulation_task(test_emulation_run: EmulationRunModel) -> EmulationTask:
    return EmulationTask(data=EmulationData(emulation_run_id=test_emulation_run.id))


@pytest.fixture()
def emulator_raises_error(request: FixtureRequest) -> bool:
    if hasattr(request, "param"):
        return request.param
    raise NotImplementedError


@pytest.fixture()
def mock_subprocess_popen(mocker: MockFixture, emulator_raises_error: bool) -> MagicMock:
    mock_popen = MagicMock()
    if emulator_raises_error:
        mock_popen = MagicMock(side_effect=FileNotFoundError())
    with mocker.patch("subprocess.Popen", mock_popen):
        yield mock_popen
