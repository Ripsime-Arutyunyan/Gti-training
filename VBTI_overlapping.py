import json
from pathlib import Path
import glob, os
import superannotate as sa
from shapely.geometry import Polygon, LinearRing
import numpy as np
import shutil
import tempfile

"""
WE ARE MESSING HERE TO CHECK HOW MERGING WORKS

"""

#1. Create a folder and paste this script in that folder 
#2. Open the script and in the project_name within the quotes write the name of your project / close the script
#3. Right click on the folder and choose 'new terminal' / 'open in terminal' - depends on your OS 
#4. Authorize in your team: superannotatecli init / y / token - Make sure your SDK is updated
#5. type: 'pip install shapely'
#6. type 'python VBTI.py' in terminal and press enter
# 39e0f2c11be83145c1f4fe35353667e3e6207891c66a550bc8646856d7b87193bd1c9e46120079a5t=15291


project_name = 'Cucumber/batch_8' 

os.makedirs(project_name)
cwd = os.getcwd()
project_path = cwd + f"/{project_name}"

annotations = sa.get_annotations(project_name)

for annot in annotations:
    file_path = os.path.join(project_path, f"{annot['metadata']['name']}___objects.json")
    with open(file_path, 'w') as fw:
        json.dump(annot, fw)

images = []
pathname = project_path + "/**/*objects.json"
annotations_ = glob.glob(pathname, recursive=True)

for annotation in annotations_:
    with open(annotation, 'r+') as f:
        info = json.load(f)
        email = "kevork@superannotate.com" #change email to your preferred one
        all_polygons = []
        for instance in info["instances"]:
            if instance["type"] == "polygon":
                points = instance["points"]
                pts = np.reshape(points, (-1,2))
                polygon = Polygon(pts)
                lr = LinearRing(pts)
                if lr.is_valid:
                    all_polygons.append(polygon)
                else:
                    all_polygons.append(polygon.buffer(0))

        total = len(all_polygons)
        overlapped = []

        for i in range(total-1):
            for j in range(i+1,total):
                p1 = all_polygons[i]
                p2 = all_polygons[j]
                if p1.intersects(p2):
                    p = sorted([i,j])
                    if p1.area + p2.area < p1.area + p2.area + p1.intersection(p2).area:
                        overlapped.append(p)

        to_comment = []
        [to_comment.append(i) for i in overlapped if i not in to_comment]
        if len(to_comment) > 0:
            images.append(info["metadata"]["name"])

        for i in to_comment:
            id1 = i[0]
            id2 = i[1]
            try:
                coord = all_polygons[id1].intersection(all_polygons[id2]).exterior.coords[0]
            except:
                coord = list(all_polygons[id1].intersection(all_polygons[id2]))[0].exterior.coords[0]
            info["comments"].append(
                                {
                    "correspondence": [
                                {
                                "text": "Polygons overlap",
                                "email": email
                                }
                                ],
                                "x": coord[0],
                                "y": coord[1],
                                "resolved": False
                                }
                                )

        f.seek(0)
        json.dump(info, f, indent=4)
        f.truncate()

sa.upload_annotations_from_folder_to_project(project_name, project_path)
sa.set_annotation_statuses(project_name, "Returned", images)

sa.upload_image_annotations()


# sa.prepare_export("Cucumber", ["Batch_8"])
# sa.download_export("Cucumber", sa.get_exports("Cucumber")[0],'/home/hripsime/Desktop/clients/VBTI')

# imgs = sa.search_items("Cucumber/Batch_8")
annotations_path = '/home/hripsime/Desktop/clients/VBTI/annotations'
# for i in imgs:
#     sa.download_image("Cucumber/Batch_8", i["name"], imgs_path, include_annotations=True)import os

# sourcepath = annotations_path
# sourcefiles = os.listdir(sourcepath)
images_path = '/home/hripsime/Desktop/clients/VBTI/images'
# for file in sourcefiles:
#     if file.endswith('.png'):
#         shutil.move(os.path.join(sourcepath,file), os.path.join(images_path,file))


# sa.upload_annotations_from_folder_to_project("VBTI_Test", annotations_path)