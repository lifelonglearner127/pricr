# Crawler

You just need to enter REP_IDs and zip codes in `src/mocks/all.json` file according to the predefined format. Or you can specify the job file as system args

We use `json` file in version 1 crawler but `yml` file for version 2. So we don't need to specify file extension. Just give filename only. Or the filename will be `all` by default. So `all.json` or `all.yml`

```
$ python run.py
```
or
```
$ python run.py debug
```
The `json` file format should look like the following
```
{
    "4CH": ["77016"],
    "DE": ["77016", "75080"],
    ...
}
```

We will use the following `yml` syntax.
```
DE:
  - 
    zipcode: 77016
    commodity: elec
  - 
    zipcode: 77580
    commodity: gas
...
```