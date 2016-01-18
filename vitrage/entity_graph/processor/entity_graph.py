# Copyright 2015 - Alcatel-Lucent
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

from dateutil import parser
from oslo_log import log

from vitrage.common.constants import EdgeProperties as EProps
from vitrage.common.constants import VertexProperties as VProps
from vitrage.common.utils import utcnow
from vitrage.graph import networkx_graph


LOG = log.getLogger(__name__)


class EntityGraph(networkx_graph.NXGraph):

    def __init__(self, name):
        super(EntityGraph, self).__init__(name)

    def can_vertex_be_deleted(self, vertex):
        """Check if the vertex can be deleted

        Vertex can be deleted if it's IS_PLACEHOLDER property is
        True and if it has no neighbors that aren't marked deleted
        """

        if not vertex[VProps.IS_PLACEHOLDER]:
            return False

        # check that vertex has no neighbors
        neighbor_edges = self.get_edges(vertex.vertex_id)

        return not any(True for neighbor_edge in neighbor_edges
                       if not self.is_edge_deleted(neighbor_edge))

    def delete_placeholder_vertex(self, suspected_vertex):
        """Checks if it is a placeholder vertex, and if so deletes it """

        if self.can_vertex_be_deleted(suspected_vertex):
            LOG.debug("Delete placeholder vertex: %s", suspected_vertex)
            self.remove_vertex(suspected_vertex)

    @staticmethod
    def is_vertex_deleted(vertex):
        return vertex.get(VProps.IS_DELETED, False)

    @staticmethod
    def is_edge_deleted(edge):
        return edge.get(EProps.IS_DELETED, False)

    def mark_vertex_as_deleted(self, vertex):
        """Marks the vertex as is deleted, and updates deletion timestamp"""
        # TODO(Alexey): change the update_vertex so it will raise a trigger
        vertex[VProps.IS_DELETED] = True
        vertex[VProps.UPDATE_TIMESTAMP] = str(utcnow())
        self.update_vertex(vertex)

    def mark_edge_as_deleted(self, edge):
        """Marks the edge as is deleted, and updates delete timestamp"""
        # TODO(Alexey): change the update_edge so it will raise a trigger
        edge[EProps.IS_DELETED] = True
        edge[EProps.UPDATE_TIMESTAMP] = str(utcnow())
        self.update_edge(edge)

    def find_neighbor_types(self, neighbors):
        """Finds all the types (TYPE, SUB_TYPE) of the neighbors """

        neighbor_types = set()
        for (vertex, edge) in neighbors:
            neighbor_types.add(self.get_vertex_category(vertex))
        return neighbor_types

    @staticmethod
    def get_vertex_category(vertex):
        category = vertex[VProps.CATEGORY]
        type = vertex[VProps.TYPE]
        return category, type

    def check_update_validation(self, graph_vertex, updated_vertex):
        """Checks current and updated validation

        Check 2 conditions:
        1. is the vertex not deleted
        2. is updated timestamp bigger then current timestamp
        """

        return (not self.is_vertex_deleted(graph_vertex)) and \
            self.check_timestamp(graph_vertex, updated_vertex)

    @staticmethod
    def check_timestamp(graph_vertex, new_vertex):
        curr_timestamp = graph_vertex.get(VProps.UPDATE_TIMESTAMP)
        if not curr_timestamp:
            return True

        current_time = parser.parse(curr_timestamp)
        new_time = parser.parse(new_vertex[VProps.UPDATE_TIMESTAMP])
        return current_time <= new_time

    @staticmethod
    def can_update_vertex(graph_vertex, new_vertex):
        return (not graph_vertex) or (not new_vertex[VProps.IS_PLACEHOLDER])
