import os
import time

from tests.integrations.base import BaseTest


class TestWriteCurrentView(BaseTest):
    def setup(self):
        super(TestWriteCurrentView, self).setup()
        self.current = "%scurrent" % self.mount_path

    def test_write_a_file(self):
        content = "Just a small file"
        filename = "%s/new_file" % self.current

        with open(filename, "w") as f:
            f.write(content)

        # check if the write was done correctly
        with open(filename) as f:
            assert f.read() == content

        # check if a commit was made
        self.assert_new_commit()

        self.assert_blob(content, "new_file")
        self.assert_commit_message("Update /new_file")

    def test_create_a_directory(self):
        directory = "%s/new_directory" % self.current

        os.makedirs(directory)

        # check if directory exists or not
        directory_path = "%s/testing_repo/new_directory" % self.repo_path
        assert os.path.exists(directory_path)

        # check for .keep file
        keep_path = "%s/testing_repo/new_directory/.keep" % self.repo_path
        assert os.path.exists(keep_path)

        self.assert_new_commit()
        self.assert_commit_message("Created new_directory/.keep")

    def test_chmod(self):
        filename = "%s/testing" % self.current
        os.chmod(filename, 0766)

        # check if the right mode was set
        stats = os.stat(filename)
        assert stats.st_mode == 0100766

        self.assert_new_commit()
        self.assert_commit_message("Chmod to 0766 on /testing")

    def test_rename(self):
        old_filename = "%s/testing" % self.current
        new_filename = "%s/new_testing" % self.current

        os.rename(old_filename, new_filename)

        # check for new file
        assert os.path.exists(new_filename)

        self.assert_new_commit()
        self.assert_commit_message("Rename /testing to /new_testing")

    def test_fsync(self):
        filename = "%s/me" % self.current
        content = "test fsync"

        with open(filename, "w") as f:
            f.write(content)
            os.fsync(f.fileno())

        self.assert_new_commit()
        self.assert_commit_message("Fsync /me")

        time.sleep(1)

        self.assert_new_commit()
        self.assert_commit_message("Update /me")

    def test_create(self):
        filename = "%s/new_empty_file" % self.current
        open(filename, "a").close()

        time.sleep(1)

        self.assert_new_commit()
        self.assert_commit_message("Created /new_empty_file")

    def test_symbolic_link(self):
        target = "me"
        name = "%s/links" % self.current
        os.symlink(target, name)

        # check if link exists
        assert os.path.exists(name)

        self.assert_new_commit()
        self.assert_commit_message("Create symlink to %s for /links" %
                                   (target))