# Copyright 2014 PressLabs SRL
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from mock import MagicMock, patch

from gitfs.router import Router


class TestRouter(object):
    def get_new_router(self):
        mocked_credentials = MagicMock()
        mocked_branch = MagicMock()
        mocked_repo = MagicMock()
        mocked_repository = MagicMock()
        mocked_log = MagicMock()
        mocked_ignore = MagicMock()
        mocked_cache_ignore = MagicMock()
        mocked_lru = MagicMock()
        mocked_pwnam = MagicMock()
        mocked_grnam = MagicMock()
        mocked_time = MagicMock()
        mocked_queue = MagicMock()
        mocked_shutil = MagicMock()
        mocked_shutting = MagicMock()
        mocked_fetch = MagicMock()

        mocked_time.time.return_value = 0
        mocked_repository.clone.return_value = mocked_repo
        mocked_ignore.return_value = mocked_cache_ignore
        mocked_pwnam.return_value.pw_uid = 1
        mocked_grnam.return_value.gr_gid = 1

        mocks = {
            'repository': mocked_repository,
            'repo': mocked_repo,
            'log': mocked_log,
            'ignore': mocked_ignore,
            'ignore_cache': mocked_ignore,
            'lru': mocked_lru,
            'getpwnam': mocked_pwnam,
            'getgrnam': mocked_grnam,
            'time': mocked_time,
            'queue': mocked_queue,
            'shutil': mocked_shutil,
            'shutting': mocked_shutting,
            'fetch': mocked_fetch,
        }

        init_kwargs = {
            'remote_url': 'remote_url',
            'repo_path': 'repository_path',
            'mount_path': 'mount_path',
            'credentials': mocked_credentials,
            'branch': mocked_branch,
            'user': 'user',
            'group': 'root',
            'commit_queue': mocked_queue,
            'max_size': 10,
            'max_offset': 10,
        }

        with patch.multiple('gitfs.router', Repository=mocked_repository,
                            log=mocked_log, CachedIgnore=mocked_ignore,
                            lru_cache=mocked_lru, getpwnam=mocked_pwnam,
                            getgrnam=mocked_grnam, time=mocked_time,
                            shutil=mocked_shutil, fetch=mocked_fetch,
                            shutting_down=mocked_shutting):
            router = Router(**init_kwargs)

        mocks.update(init_kwargs)
        return router, mocks

    def test_constructor(self):
        router, mocks = self.get_new_router()

        asserted_call = (mocks['remote_url'], mocks['repo_path'],
                         mocks['branch'], mocks['credentials'])
        mocks['repository'].clone.assert_called_once_with(*asserted_call)
        mocks['ignore'].assert_called_once_with(**{
            'submodules': True,
            'ignore': True,
            'path': mocks['repo_path'],
        })
        mocks['getpwnam'].assert_called_once_with(mocks['user'])
        mocks['getgrnam'].assert_called_once_with(mocks['group'])

        assert mocks['repo'].commits.update.call_count == 1
        assert mocks['time'].time.call_count == 1
        assert router.commit_queue == mocks['queue']
        assert router.max_size == 10
        assert router.max_offset == 10

    def test_init(self):
        mocked_fetch = MagicMock()
        mocked_sync = MagicMock()

        router, mocks = self.get_new_router()
        router.workers = [mocked_fetch, mocked_sync]

        router.init("path")

        assert mocked_fetch.start.call_count == 1
        assert mocked_sync.start.call_count == 1

    def test_destroy(self):
        mocked_fetch = MagicMock()
        mocked_sync = MagicMock()

        router, mocks = self.get_new_router()
        router.workers = [mocked_fetch, mocked_sync]

        with patch.multiple('gitfs.router', shutil=mocks['shutil'],
                            fetch=mocks['fetch'],
                            shutting_down=mocks['shutting']):
            router.destroy("path")

        assert mocked_fetch.join.call_count == 1
        assert mocked_sync.join.call_count == 1
        assert mocks['fetch'].set.call_count == 1
        assert mocks['shutting'].set.call_count == 1
        mocks['shutil'].rmtree.assert_called_once_with(mocks['repo_path'])