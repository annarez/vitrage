#!/usr/bin/env bash
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

DEVSTACK_PATH="$BASE/new"

#Argument is received from Zuul
if [ "$1" = "api" ]; then
  TESTS="topology|test_rca|test_alarms|test_resources|test_template
  |test_webhook"
elif [ "$1" = "datasources" ]; then
  TESTS="datasources|test_events|notifiers|e2e|database"
else
  TESTS="topology"
fi

if [ "$DEVSTACK_GATE_USE_PYTHON3" == "True" ]; then
        export PYTHON=python3
fi

sudo cp -rf $DEVSTACK_PATH/vitrage/vitrage_tempest_tests/tests/resources/heat/heat_template.yaml /etc/vitrage/
sudo cp -rf $DEVSTACK_PATH/vitrage/vitrage_tempest_tests/tests/resources/heat/heat_nested_template.yaml /etc/vitrage/
sudo cp -rf $DEVSTACK_PATH/vitrage/vitrage_tempest_tests/tests/resources/heat/server.yaml /etc/vitrage/

sudo cp -rf $DEVSTACK_PATH/tempest/etc/logging.conf.sample $DEVSTACK_PATH/tempest/etc/logging.conf

${PYTHON:-python} $DEVSTACK_PATH/vitrage/vitrage_tempest_tests/add_legacy_dir_templates.py

# restart due to configuration files changes
sudo systemctl restart devstack@vitrage-graph.service

# wait for 30 seconds
sleep 30



cd $DEVSTACK_PATH/tempest/; sudo -E testr init

echo "Listing existing Tempest tests"
sudo -E testr list-tests vitrage_tempest_tests
sudo -E testr list-tests vitrage_tempest_tests | grep -E "$TESTS" > /tmp/vitrage_tempest_tests.list
echo "Testing $1: $TESTS..."
sudo -E testr run --subunit --load-list=/tmp/vitrage_tempest_tests.list | subunit-trace --fails
