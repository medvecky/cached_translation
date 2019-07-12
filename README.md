# Cached translation

### Caching service for google translate API


## Installation and running up

* Install python V3 and docker 
* Clone project
* Copy to project directory google application credential json file
* In project directory execute:
```
 pip3 install -r requirements.txt
 python3 codegen.py
 docker-compose build
 docker-compose up
```
* For operations with service possible use command line client
```
 usage: cached_translation_client.py [-h] [--source Source] --to Target 
                                     Text [Text ...]
 Example:
 python3 cached_translation_client.py --source=en --to=ru "Helo people"
``` 
 
 ## Test run
 Now unit tests works only when project was opened in Intelij idea IDE
 
 * Open project in Intelij IDE - ide must contain python plugin or just use pycharm 
 * Unit tests may be runned as is
 * Integration tests needs working sever and added to run configuration environment variable
 ``` 
 GOOGLE_APPLICATION_CREDENTIALS=[path to json file with credentials received from google]
 ``` 
 
 