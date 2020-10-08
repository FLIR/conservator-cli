## file-system conservator collection
The upload and download script for conservator collections tries to create an accurate representation of the conservator collection in your file system.

The following is the general structure of a Project

```/
    integration-test/
      image1.jpg
      image2.jpg
      video_metadata/
        5_second_cut.json
      associated_files/
        car_arrow.png
        nntc_config.json
      test/
        index.json
      subfolder/
        video_metadata/
        associated_files/
          uav.png
```
Key ideas:
  video_metadata is now a reserved folder name
  associated_files is now a reserved folder name
