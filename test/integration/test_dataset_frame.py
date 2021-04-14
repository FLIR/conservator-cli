import pytest as pytest


class TestDatasetFrame:
    @pytest.fixture(scope="class", autouse=True)
    def init_dataset(self, conservator, test_data):
        local_path = test_data / "png" / "flight_0.png"
        media_id = conservator.media.upload(local_path)
        conservator.media.wait_for_processing(media_id)
        image = conservator.images.all().first()
        frame = image.get_frame()
        dataset = conservator.datasets.create("Test dataset")
        dataset.add_frames([frame])

    def test_initial_state(self, conservator):
        # Good to test initial conditions the other tests will assume
        dataset = conservator.datasets.all().first()
        frames = dataset.get_frames()
        assert len(frames) == 1
        frame = frames.first()

        assert not frame.is_flagged
        assert not frame.is_empty
        assert frame.qa_status is None

    def test_flag(self, conservator):
        dataset = conservator.datasets.all().first()
        frames = dataset.get_frames()
        assert len(frames) == 1
        frame = frames.first()

        frame.flag()

        frame.populate("is_flagged")
        assert frame.is_flagged

    def test_unflag(self, conservator):
        dataset = conservator.datasets.all().first()
        frames = dataset.get_frames()
        assert len(frames) == 1
        frame = frames.first()

        frame.unflag()

        frame.populate("is_flagged")
        assert not frame.is_flagged

    def test_mark_empty(self, conservator):
        dataset = conservator.datasets.all().first()
        frames = dataset.get_frames()
        assert len(frames) == 1
        frame = frames.first()

        frame.mark_empty()

        frame.populate("is_empty")
        assert frame.is_empty

    def test_unmark_empty(self, conservator):
        dataset = conservator.datasets.all().first()
        frames = dataset.get_frames()
        assert len(frames) == 1
        frame = frames.first()

        frame.unmark_empty()

        frame.populate("is_empty")
        assert not frame.is_empty

    def test_approve(self, conservator):
        dataset = conservator.datasets.all().first()
        frames = dataset.get_frames()
        assert len(frames) == 1
        frame = frames.first()

        frame.approve()

        frame.populate("qa_status")
        assert frame.qa_status == "approved"

    def test_request_changes(self, conservator):
        dataset = conservator.datasets.all().first()
        frames = dataset.get_frames()
        assert len(frames) == 1
        frame = frames.first()

        frame.request_changes()

        frame.populate("qa_status")
        assert frame.qa_status == "changesRequested"

    def test_unset_qa_status(self, conservator):
        dataset = conservator.datasets.all().first()
        frames = dataset.get_frames()
        assert len(frames) == 1
        frame = frames.first()

        frame.unset_qa_status()

        frame.populate("qa_status")
        assert frame.qa_status is None
