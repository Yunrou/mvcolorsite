# Django
from django.conf import settings
from django.core.files import File
from ..models import Dataset, Chart

import os, json
import pickle5 as pickle
from werkzeug.utils import secure_filename
from pandas import read_csv

from .handler import Handler

def load_example(example, save_mvobject=False):

    # Path
    example_root = os.path.join(settings.MEDIA_ROOT, 'example', example)
    read_dataset_root = os.path.join(example_root, 'dataset')
    read_chart_root = os.path.join(example_root, 'chart')
    write_dataset_root = os.path.join(settings.MEDIA_ROOT, 'dataset')
    write_chart_root = os.path.join(settings.MEDIA_ROOT, 'chart')

    # Load datasets
    for filename in os.listdir(read_dataset_root):
        name = secure_filename(filename)
        # Remove file if the file exists
        target = os.path.join(write_dataset_root, name)
        if os.path.isfile(target):
            os.remove(target)
        # Create instance
        filepath = os.path.join(read_dataset_root, filename)
        if (not os.path.isfile(filepath)) or filename[0] == '.': 
            continue
        f = open(filepath, 'rb')
        obj = Dataset.objects.create(example=example, name=name, 
                                     file=File(name=name, file=f))
        f.close()
        
    # Load layout
    df = read_csv(os.path.join(example_root, 'layout.csv'))

    # Load chart specs
    for index, row in df.iterrows():
        name = row['name']
        # Remove file if the file exists
        target = os.path.join(write_chart_root, name)
        if os.path.isfile(target):
            os.remove(target)

        filepath = os.path.join(read_chart_root, name)
        if (not os.path.isfile(filepath)) or name[0] == '.': 
            continue

        f = open(filepath, 'rb')
        spec = json.loads(f.read())
        # Change data's url in spec
        dataset = ''
        if "url" in spec["data"]:
            spec = Handler.set_url(spec)
            dataset = spec["data"]["url"].split('/')[-1]
        # Set title and remove it in spec
        title = spec["title"]
        spec.pop("title", None)
        # Set spec and layout
        spec = json.dumps(spec)
        # Create instance
        obj = Chart.objects.create(current=False,
                                   example=example,
                                   index=index,
                                   name=name,
                                   title=title,
                                   file=File(name=name, file=f), 
                                   spec=spec, 
                                   raw_spec=spec, 
                                   dataset=dataset,
                                   ce_id=0,
                                   x=row.x,
                                   y=row.y,
                                   w=row.w,
                                   h=row.h)
        f.close()
        # if title == "City Breakdown":
        #     print(spec)
    if not save_mvobject: return

    # Check if MV object has saved.
    model_path = os.path.join(example_root, "model.sav")
    if os.path.isfile(model_path):
        os.remove(model_path)

    mv = Handler.createMV(Dataset.objects.filter(example=example), 
                          Chart.objects.filter(example=example))

    pickle.dump(mv, open(model_path, 'wb'))
    print("Save MV object to", model_path)