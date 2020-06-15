import logging
from pathlib import Path
from typing import List, Dict, Union

import cv2
import numpy

from FLIR.conservator_cli.lib.hierarchy_tree.utils import read_json_file

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s]: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

lg = logging.getLogger(__name__)
lg.setLevel(logging.INFO)


def get_frames_from_video(video_path: Union[str, Path]) -> list:
    vidcap = cv2.VideoCapture(str(video_path))
    success, image = vidcap.read()
    count = 0
    frames = []
    while success:
        frames.append(image)
        # cv2.imwrite("frame%d.jpg" % count, image)  # save frame as JPEG file
        success, image = vidcap.read()
        count += 1
    return frames


def convert_frames_to_video(save_path: Union[str, Path], *list_of_frames):
    how_many_classifiers = len(list_of_frames)
    height, width, layers = list_of_frames[0][0].shape
    size = (width * how_many_classifiers, height)

    out = cv2.VideoWriter(save_path,
                          cv2.VideoWriter_fourcc(*'MP4V'),
                          24,
                          size)

    for frames in zip(*list_of_frames):
        out.write(numpy.hstack(frames))
    out.release()


def get_unique_classifiers(json_content: dict):
    classifier_names = []
    frames = json_content['videos'][0]['frames']
    for frame in frames:
        for annotation in frame['annotations']:
            classifier_names.append(annotation['source']['meta']['classifierName'])
    return numpy.unique(classifier_names).tolist()


def annotate_frames_with_bboxes(video_file_path: Path, used_classifier: str) -> List[numpy.ndarray]:
    font_scale = 2
    line_type = 2
    font_color = (0, 0, 0)
    font = cv2.FONT_HERSHEY_SIMPLEX

    json_path = video_file_path.parent / f'{video_file_path.stem}.json'
    content = read_json_file(json_path)
    unique_classifier = get_unique_classifiers(content)

    if used_classifier not in unique_classifier:
        raise Exception('classifier was not used in any of the video frames')

    frames: List[Dict] = content['videos'][0]['frames']
    images = get_frames_from_video(video_file_path)

    for image in images:
        cv2.putText(image,
                    used_classifier,
                    (100, 100),
                    font,
                    3,
                    font_color,
                    line_type)

    for frame in frames:
        frame_index = frame['frameIndex'] - 1  # -1 to maintain indexing from 0
        image: numpy.ndarray = images[frame_index]

        annotations = frame['annotations']
        annotations = list(filter(lambda x: x['source']['meta']['classifierName'] == used_classifier, annotations))

        for annotation in annotations:
            label = annotation['labels'][0]
            detection_score = annotation['custom']['detection_score']

            bounding_box = annotation['boundingBox']
            x = bounding_box['x']
            y = bounding_box['y']
            w = bounding_box['w']
            h = bounding_box['h']

            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 0), 2)
            cv2.putText(image,
                        label,
                        (x + 10, y),
                        font,
                        font_scale,
                        font_color,
                        line_type)
    return images


def main():
    path = Path('/FLIR8and9/Conservator/YYJ_Video_Analytics/cars_rgb')

    video_file_paths = list(path.glob('*.mp4'))

    for video_file_path in video_file_paths[:2]:
        yolo_preds = annotate_frames_with_bboxes(video_file_path, 'Yolo9000')
        # another_preds = annotate_frames_with_bboxes(video_file_path, 'Yolo9000')
        convert_frames_to_video(
            f'/FLIR8and9/Conservator/side_by_side_{video_file_path.stem}.mp4',
            yolo_preds,
            yolo_preds
        )


if __name__ == '__main__':
    main()
