# (C) Copyright 2014 Hewlett Packard Enterprise Development Company LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from metricbase import MetricBase


class Gauge(MetricBase):

    def __init__(self, connection, name=None, dimensions=None):
        super(self.__class__, self).__init__(name=name,
                                             connection=connection,
                                             dimensions=dimensions)

    def send(self, name, value, dimensions=None, sample_rate=1):
        """Record the value of a gauge, optionally setting a list of

        dimensions and a sample rate.

        >>> monascastatsd.gauge('users.online', 123)
        >>> monascastatsd.gauge('active.connections', 1001,
        >>>                 dimensions={"protocol": "http"})
        """
        self._connection.report(metric=self.update_name(name),
                                metric_type='g',
                                value=value,
                                dimensions=self.update_dimensions(dimensions),
                                sample_rate=sample_rate)
