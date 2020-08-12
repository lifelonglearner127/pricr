# Crawler

You just need to enter REP_IDs and zip codes in `runtime.json` file according to the predefined format. Or you can specify the job file as system args
```
$ python run.py
```
or
```
$ python run.py debug.json
```
The file format should look like the following
```
{
    "4CH": ["77016"],
    "DE": ["77016", "75080"],
    ...
}
```