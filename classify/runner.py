import fetcher
import embedder
from collection import Collection
import logging
from logging.handlers import RotatingFileHandler
import sys
import build_webdata
import glob
import os
import shutil

# set up rotating logfile (and log to console)
logger = logging.getLogger('propinquity')
logger.setLevel(logging.DEBUG)
fh = RotatingFileHandler('propinquity.log', maxBytes=1e8, backupCount=1)
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

# log exceptions to logfile
def my_handler(type, value, tb):
    logger.error("Uncaught exception: {0}".format(str(value)), exc_info=(type, value, tb))
sys.excepthook = my_handler

collectionOpts = [
  {
    'collection_id': 'NMK-B',
    'artifact_name': 'Fotografi',
    'process_id': 'photography'
  },
  {
    'collection_id': 'NMK-B',
    'artifact_name': 'Maleri',
    'process_id': 'painting_subject'
  },
  {
    'collection_id': 'NMK-B',
    'artifact_name': 'Maleri',
    'process_id': 'painting_style'
  },
  {
    'collection_id': 'NMK-B',
    'artifact_name': 'Grafikk',
    'process_id': 'printmaking'
  },
  {
    'collection_id': 'NMK-B',
    'artifact_name': 'Tegning',
    'process_id': 'drawings'
  },
  {
    'collection_id': 'NMK-D',
    'artifact_name': None,
    'process_id': 'design'
  }
]

for options in collectionOpts:

  collection = Collection(options['process_id'])

  options['start_date'] = collection.most_recently_published_date()
  options['collection'] = collection

  fetcher.fetch_new(options)
  embedder.embed_new(options)
  collection.write()
  if collection.modified:
    build_webdata.build_web_files(options)
    # copy built files to dist folder
    process = options['process_id']
    dest_dir = "../dist/data/"+process+"/"
    files = []
    for ff in ['*.jpg','*.dds','*.js']:
      files.extend( glob.glob("./data/"+process+"/"+ff) )
    if not os.path.exists(dest_dir):
      os.makedirs(dest_dir)
    for file in files:
      shutil.copy(file, dest_dir)
