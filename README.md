# nio-cmdb
```
A tiny cmdb , define dynamic model by restful api.
```
 
## Environment
- python 3.7+
- npm 6.9.0+

## Install
```bash
# install python backend
pip install -r requirements.txt
# initial database
python manage.py makemigratioins 
python manage.py migrate
# run python backend development server
python manage.py runserver 0.0.0.0:8000
# install web front
cd web;
npm install
#  run web front in development mode
npm run dev
```

## Docs
- django-docs 
http://127.0.0.1:8000/docs
- django-rest-framework docs 
http://127.0.0.1:8000/v1/

## Usage
1.define a resource
```
# make a post request to http://127.0.0.1:8000/v1/resourceDefined/ with the body below
 {
            "attributes": [
                {
                    "id": 1,
                    "name": "ip",
                    "default": "127.0.0.1",
                    "resourcetype": "StringAttributeDefined"
                },
                {
                    "id": 2,
                    "name": "namespace",
                    "default": "xxx",
                    "resourcetype": "StringAttributeDefined"
                },
                {
                    "name": "cpu",
                    "default": 11,
                    "resourcetype": "IntegerAttributeDefined"
                }
            ],
            "name": "mysql"
        }
# than you can CRUD the resource you defined by http://127.0.0.1:8000/v1/mysql/

```