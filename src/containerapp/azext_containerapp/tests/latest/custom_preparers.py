# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.testsdk import CliTestError
from azure.cli.testsdk.reverse_dependency import get_dummy_cli
from azure.cli.testsdk.scenario_tests import SingleValueReplacer
from azure.cli.testsdk.preparers import NoTrafficRecordingPreparer, ResourceGroupPreparer


# pylint: disable=too-many-instance-attributes
class ConnectedClusterPreparer(NoTrafficRecordingPreparer, SingleValueReplacer):
    def __init__(self, name_prefix='aks', location='eastus2euap', aks_name='my-aks-cluster', connected_cluster_name='my-connected-cluster',
                 resource_group_parameter_name='resource_group', skip_delete=False):
        super(ConnectedClusterPreparer, self).__init__(name_prefix, 15)
        self.cli_ctx = get_dummy_cli()
        self.location = location
        self.infra_cluster = aks_name
        self.connected_cluster_name = connected_cluster_name
        self.resource_group_parameter_name = resource_group_parameter_name
        self.skip_delete = skip_delete

    def create_resource(self, name, **kwargs):
        group = self._get_resource_group(**kwargs)
        try:
            self.live_only_execute(self.cli_ctx, f'az aks create --resource-group {group} --name {self.infra_cluster} --enable-aad --generate-ssh-keys --enable-cluster-autoscaler --min-count 4 --max-count 10 --node-count 4')
            self.live_only_execute(self.cli_ctx, f'az aks get-credentials --resource-group {group} --name {self.infra_cluster} --overwrite-existing --admin')
            self.live_only_execute(self.cli_ctx, f'az connectedk8s connect --resource-group {group} --name {self.connected_cluster_name}')
        except AttributeError:  # live only execute returns None if playing from record
            pass
        return {'infra_cluster': self.infra_cluster,
                'connected_cluster_name': self.connected_cluster_name}

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_parameter_name)
        except KeyError:
            template = 'Resource group is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ResourceGroupPreparer.__name__,
                                               self.resource_group_parameter_name))
