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


class VertexProperties(object):
    TYPE = 'TYPE'
    SUB_TYPE = 'SUB_TYPE'
    ID = 'ID'
    IS_DELETED = 'IS_DELETED'
    STATE = 'STATE'
    PROJECT = 'PROJECT'
    UPDATE_TIMESTAMP = 'UPDATE_TIMESTAMP'
    NAME = 'NAME'
    IS_PLACEHOLDER = 'IS_PLACEHOLDER'


class EdgeProperties(object):
    RELATION_NAME = 'RELATION_NAME'
    IS_DELETED = 'IS_DELETED'
    UPDATE_TIMESTAMP = 'UPDATE_TIMESTAMP'


class EdgeLabels(object):
    ON = 'on'
    CONTAINS = 'contains'


class SyncMode(object):
    SNAPSHOT = 'snapshot'
    INIT_SNAPSHOT = 'init_snapshot'
    UPDATE = 'update'


class EntityTypes(object):
    RESOURCE = 'RESOURCE'


class EventAction(object):
    CREATE = 'create'
    DELETE = 'delete'
    UPDATE = 'update'