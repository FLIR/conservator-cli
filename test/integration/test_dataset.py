def test_create(conservator):
    dataset = conservator.datasets.create("My Dataset")
    assert dataset is not None
    assert dataset.name == "My Dataset"

    fetched_dataset = conservator.datasets.all().first()
    assert fetched_dataset is not None
    assert fetched_dataset.id == dataset.id
    assert fetched_dataset.name == "My Dataset"


def test_delete(conservator):
    pass


def test_generate_metadata(conservator):
    pass


def test_get_frames(conservator):
    pass


def test_add_frames(conservator):
    pass


def test_commit(conservator):
    pass


def test_from_string_id(conservator):
    pass


def test_from_string_name(conservator):
    pass


class TestDataset:
    # These tests don't modify anything, so we can reuse the same dataset.

    def test_get_git_url(self, conservator):
        pass

    def test_get_commit_history(self, conservator):
        pass

    def test_get_commit_by_id(self, conservator):
        pass

    def test_get_root_tree_id(self, conservator):
        pass

    def test_get_tree_by_id(self, conservator):
        pass

    def test_get_blob_url_by_id(self, conservator):
        pass

    def test_get_blob_id_by_name(self, conservator):
        pass

    def test_download_blob_by_name(self, conservator, tmp_cwd):
        pass

    def test_download_blob(self, conservator, tmp_cwd):
        pass

    def test_download_latest_index(self, conservator, tmp_cwd):
        pass

    def test_from_local_path(self, conservator, tmp_cwd):
        pass
