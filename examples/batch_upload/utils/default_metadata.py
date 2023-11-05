# pylint: disable=missing-class-docstring
# pylint: disable=missing-module-docstring
class DefaultMetadata:
    name: str
    cameras: dict

    def __init__(self, metadata: dict, name: str):
        self.name = name
        self.metadata = metadata

    def get_tags(self, camera_name_or_spectrum: str) -> list:
        """
        A preset can represent a capture from multiple frame-synced cameras
        so provide a camera name.
        However in the generic case we assume a single default camera,
        so camera name is not required
        :param camera_name_or_spectrum:
        :return:
        """
        default_metadata = self.metadata.get(camera_name_or_spectrum, {})

        tags_input = default_metadata.get("tags")
        tags = []

        if isinstance(tags_input, str):
            tags_input = tags_input.strip()

            if len(tags_input):
                for t in tags_input.split(","):
                    tags.append(t.strip().lower())

            # Cache tags
            default_metadata["tags"] = tags
        elif not isinstance(tags, list):
            raise Exception(
                f'Unsupported type for tags for camera / \
                    spectrum: "{camera_name_or_spectrum}" for hardware name: "{self.name}"'
            )
        else:
            for i, tag in enumerate(tags_input):
                tags_input[
                    i
                ] = (
                    tag.lower()
                )  # Conservator wants this to be lowercase or it fails (wtf, but ok)
            tags = tags_input

        return tags

    def _default_metadata(self, camera_name_or_spectrum: str) -> dict:
        default_metadata = self.metadata.get(camera_name_or_spectrum)

        if default_metadata is None:
            raise Exception(
                f'Default metadata does not exist for key "{camera_name_or_spectrum}"'
            )

        return default_metadata

    def get_spectrum(self, camera_name_or_spectrum: str) -> str:
        """
        :param camera_name_or_spectrum:
        :return:
        """
        default_metadata = self._default_metadata(camera_name_or_spectrum)

        spectrum = default_metadata.get("spectrum")

        if spectrum is None:
            raise Exception(
                f'Default metadata for key "{camera_name_or_spectrum}" does not have spectrum'
            )
        elif not isinstance(spectrum, str):
            raise Exception(
                f'Unsupported type for description for camera /\
                    spectrum: "{camera_name_or_spectrum}" for hardware name: "{self.name}"'
            )

        return str(spectrum).lower()

    def get_description(self, camera_name_or_spectrum: str) -> str:
        """
        :param camera_name_or_spectrum:
        :return:
        """
        return self._default_metadata(camera_name_or_spectrum).get("description", "")

    def get_location(self, camera_name_or_spectrum: str) -> str:
        """
        :param camera_name_or_spectrum:
        :return:
        """
        return self._default_metadata(camera_name_or_spectrum).get("location", "")
