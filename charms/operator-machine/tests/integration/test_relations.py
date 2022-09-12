import logging
import pytest
import integration.utils as utils
from pytest_operator.plugin import OpsTest

LOGGER = logging.getLogger(__name__)


@pytest.mark.abort_on_fail
@pytest.mark.usefixtures("deploy_built_bundle")
@pytest.mark.skip
class TestRelations:

    async def test_it_waits_for_relation(self, ops_test: OpsTest):
        # Wait for the units to enter idle state, with particular statuses
        # such that we can test the workload messages.
        async with ops_test.fast_forward():
            await ops_test.model.wait_for_idle(apps=["livepatch-machine"], status="blocked")

        # Test it expects a relation to occur
        livepatch_unit = await utils.get_unit_by_name("livepatch-machine", "0", ops_test.model.units)
        assert livepatch_unit.workload_status == "blocked"
        assert livepatch_unit.workload_status_message == "Waiting for postgres relation to be established."

    async def test_it_informs_users_of_waiting_for_postgres_master_node(self, ops_test: OpsTest):
        # Grab unit
        livepatch_unit = await utils.get_unit_by_name("livepatch-machine", "0", ops_test.model.units)

        # Relate these bad boys
        await ops_test.model.add_relation("livepatch-machine:db", "postgresql:db")

        # Push to first waiting status
        async with ops_test.fast_forward():
            await ops_test.model.wait_for_idle(apps=["livepatch-machine"], status="waiting")
        # Test livepatch wants the master node selected
        assert livepatch_unit.workload_status_message == "Waiting for postgres to select master node..."
