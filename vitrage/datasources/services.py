# Copyright 2016 - Alcatel-Lucent
# Copyright 2016 - Nokia
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

from oslo_log import log
from oslo_service import service as os_service

from vitrage.common.constants import SyncMode

LOG = log.getLogger(__name__)


class DatasourceService(os_service.Service):
    def __init__(self, conf, registered_datasources, callback_function):
        super(DatasourceService, self).__init__()
        self.conf = conf
        self.registered_datasources = registered_datasources
        self.callback_function = callback_function


class SnapshotsService(DatasourceService):
    def __init__(self, conf, registered_datasources, callback_function):
        super(SnapshotsService, self).__init__(conf,
                                               registered_datasources,
                                               callback_function)
        self.first_time = True

    def start(self):
        LOG.info("Vitrage datasources Snapshot Service - Starting...")

        super(SnapshotsService, self).start()
        interval = self.conf.datasources.snapshots_interval
        self.tg.add_timer(interval, self._get_all)

        LOG.info("Vitrage datasources Snapshot Service - Started!")

    def stop(self, graceful=False):
        LOG.info("Vitrage datasources Snapshot Service - Stopping...")

        super(SnapshotsService, self).stop()

        LOG.info("Vitrage datasources Snapshot Service - Stopped!")

    def _get_all(self):
        sync_mode = SyncMode.INIT_SNAPSHOT \
            if self.first_time else SyncMode.SNAPSHOT
        LOG.debug("start get all with sync mode %s" % sync_mode)

        for plugin in self.registered_datasources.values():
            entities_dictionaries = plugin.get_all(sync_mode)
            for entity in entities_dictionaries:
                self.callback_function(entity)

        LOG.debug("end get all with sync mode %s" % sync_mode)
        self.first_time = False


class ChangesService(DatasourceService):
    def __init__(self, conf,
                 registered_datasources,
                 changes_interval,
                 callback_function):
        super(ChangesService, self).__init__(conf,
                                             registered_datasources,
                                             callback_function)
        self.changes_interval = changes_interval

    def start(self):
        LOG.info("Vitrage Datasource Changes Service For: %s - Starting...",
                 self.registered_datasources[0].__class__.__name__)

        super(ChangesService, self).start()
        self.tg.add_timer(interval=self.changes_interval,
                          callback=self._get_changes,
                          initial_delay=self.changes_interval)

        LOG.info("Vitrage Datasource Changes Service For: %s - Started!",
                 self.registered_datasources[0].__class__.__name__)

    def stop(self, graceful=False):
        LOG.info("Vitrage Datasource Changes Service For: %s - Stopping...",
                 self.registered_datasources[0].__class__.__name__)

        super(ChangesService, self).stop()

        LOG.info("Vitrage Datasource Changes Service For: %s - Stopped!",
                 self.registered_datasources[0].__class__.__name__)

    def _get_changes(self):
        LOG.debug("start get changes")

        for datasource in self.registered_datasources:
            for entity in datasource.get_changes(SyncMode.UPDATE):
                self.callback_function(entity)

        LOG.debug("end get changes")