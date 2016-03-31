# Copyright 2016 - Alcatel-Lucent
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from synchronizer.plugins.neutron.network import NEUTRON_NETWORK_PLUGIN
from vitrage.common.constants import EntityCategory
from vitrage.common.constants import SynchronizerProperties as SyncProps
from vitrage.common.constants import VertexProperties as VProps
from vitrage.synchronizer.plugins.base.resource.transformer import \
    BaseResourceTransformer
from vitrage.synchronizer.plugins import transformer_base as tbase
from vitrage.synchronizer.plugins.transformer_base import extract_field_value

import vitrage.graph.utils as graph_utils


class NetworkTransformer(BaseResourceTransformer):

    UPDATE_EVENT_TYPES = {}

    def __init__(self, transformers):
        super(NetworkTransformer, self).__init__(transformers)

    def _create_entity_key(self, entity_event):
        network_id = 'network_id' if tbase.is_update_event(entity_event) \
            else 'id'
        key_fields = self._key_values(NEUTRON_NETWORK_PLUGIN,
                                      extract_field_value(entity_event,
                                                          network_id))
        return tbase.build_key(key_fields)

    def _create_snapshot_entity_vertex(self, entity_event):
        name = extract_field_value(entity_event, 'name')
        entity_id = extract_field_value(entity_event, 'id')
        state = extract_field_value(entity_event, 'status')

        return self._create_vertex(entity_event, name, entity_id, state)

    def _create_vertex(self, entity_event, name, entity_id, state):

        metadata = {
            VProps.NAME: name,
        }

        sample_timestamp = entity_event[SyncProps.SAMPLE_DATE]

        # TODO(Alexey): need to check here that only the UPDATE sync_mode will
        #               update the UPDATE_TIMESTAMP property
        update_timestamp = self._format_update_timestamp(
            extract_field_value(entity_event, SyncProps.SAMPLE_DATE),
            sample_timestamp)

        return graph_utils.create_vertex(
            self._create_entity_key(entity_event),
            entity_id=entity_id,
            entity_category=EntityCategory.RESOURCE,
            entity_type=NEUTRON_NETWORK_PLUGIN,
            entity_state=state,
            sample_timestamp=sample_timestamp,
            update_timestamp=update_timestamp,
            metadata=metadata)

    def _create_update_entity_vertex(self, entity_event):
        pass

    @staticmethod
    def _create_neighbors(entity_event):
        return []
