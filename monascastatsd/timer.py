# (C) Copyright 2014-2016 Hewlett Packard Enterprise Development LP
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
#
# Copyright (c) 2012, Datadog <info@datadoghq.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Datadog nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL DATADOG BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import contextlib
import functools
import time

from monascastatsd import metricbase


class Timer(metricbase.MetricBase):

    def __init__(self, connection, name=None, dimensions=None):
        super(self.__class__, self).__init__(name=name,
                                             connection=connection,
                                             dimensions=dimensions)

    def timing(self, name, value, dimensions=None, sample_rate=1):
        """Record a timing, optionally setting dimensions and a sample rate.

        :param name: metric name
        :param value: value (float or int)
        :param dimensions: dimensions used to distinguish multiple measurements of the same metric (flat dict.)
        :param sample_rate: sample rate, values < 1 mean that only <sample_rate>% of values will be considered

        >>> monascastatsd.timing("query.response.time", 1234)
        """
        self._connection.report(metric=self.update_name(name),
                                metric_type='ms',
                                value=value,
                                dimensions=self.update_dimensions(dimensions),
                                sample_rate=sample_rate)

    def timed(self, name, dimensions=None, sample_rate=1):
        """A decorator that will measure the distribution of a function's

        run time.  Optionally specify a list of tag or a sample rate.
        ::

            @monascastatsd.timed('user.query.time', sample_rate=0.5)
            def get_user(user_id):
                # Do what you need to ...
                pass

            # Is equivalent to ...
            start = time.time()
            try:
                get_user(user_id)
            finally:
                monascastatsd.timing('user.query.time', time.time() - start)
        """
        def wrapper(func):
            @functools.wraps(func)
            def wrapped(*args, **kwargs):
                start = time.time()
                result = func(*args, **kwargs)
                self.timing(name,
                            time.time() - start,
                            dimensions=dimensions,
                            sample_rate=sample_rate)
                return result
            wrapped.__name__ = func.__name__
            wrapped.__doc__ = func.__doc__
            wrapped.__dict__.update(func.__dict__)
            return wrapped
        return wrapper

    @contextlib.contextmanager
    def time(self, name, dimensions=None, sample_rate=1):
        """Time a block of code, optionally setting dimensions and a sample rate.

        try:
            with monascastatsd.time("query.response.time"):
                Do something...
        except Exception:
            Log something...
        """

        start_time = time.time()
        yield
        end_time = time.time()
        self.timing(name, end_time - start_time, dimensions, sample_rate)
