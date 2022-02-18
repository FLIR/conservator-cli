import sys
import os
import json

# import jsonlines


def jsonl_to_json(dir, index_path=None):

    videos_file = os.path.join(dir, "videos.jsonl")

    frames_file = os.path.join(dir, "frames.jsonl")

    dataset_file = os.path.join(dir, "dataset.jsonl")

    if not os.path.exists(dataset_file):
        print(f"Path {dataset_file} doesn't exist!")
        sys.exit(1)

    frames = []
    videos = []

    if os.path.exists(frames_file):
        with open(frames_file) as frame_f:
            for frame in frame_f:
                frames.append(json.loads(frame))

    if os.path.exists(videos_file):
        with open(videos_file) as video_f:
            for video in video_f:
                videos.append(json.loads(video))

    with open(dataset_file) as dataset_f:
        dataset = json.load(dataset_f)

    frames = sorted(
        frames,
        key=lambda frame: (
            frame["videoMetadata"]["videoId"],
            frame["videoMetadata"]["frameIndex"],
        ),
    )

    videos = sorted(videos, key=lambda video: video["id"])

    dataset["frames"] = frames

    dataset["videos"] = videos

    if index_path:
        index_json = index_path
    else:
        index_json = os.path.join(dir, "index.json")

    with open(index_json, mode="w") as idx:
        json.dump(dataset, idx, indent=1, sort_keys=True)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        jsonl_dir = sys.argv[1]
    else:
        jsonl_dir = os.getcwd()

    index_path = None
    if len(sys.argv) > 2:
        index_path = sys.argv[2]

    if not os.path.exists(jsonl_dir):
        print(f"Path {jsonl_dir} doesn't exist!")
        print(
            "Usage: python3 jsonl_to_index_json.py <directory that contains jsonl files>"
        )
        sys.exit(1)

    jsonl_to_json(jsonl_dir, index_path)
