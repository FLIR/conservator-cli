from conservator import Conservator

conservator = Conservator.default()

video = conservator.videos.first()

video.download_assets(".", include_frames=True, include_metadata=True)



