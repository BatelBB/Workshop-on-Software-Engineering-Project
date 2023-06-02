# how to develop & run

Install libraries:

```
pip install -r requirements.txt
```

App is ran from `src/webapp.py`. I'm using vscode.

When you change the python files, it restarts, so that you're always running your current code. If you don't like it, change `debug=True` to `debug=False`.

**ABSOLUTELY DO NOT** try to implement file uploading. It's a waste of time. If you want images, see how dicebear is used `home.html`, and see `core_features/dicebear`. 

See the blueprints for examples. If you're adding a blueprint, add it in the `app.py` and make sure you're giving it a unique name.

Links and redirects are using `url_for`. If it's not in a blueprint (like the homepage), it's the method name, like `url_for('home.home')`, and if it's in a blueprint, you need the blueprint name, like `url_for('selling.create_store')`. If the route takes parameters, use keyword arguments, like `url_for('buying.view_store', name=store.name)`.

For forms, use WTForms. See examples in `auth` and `selling` blueprints.

To change the navbar, go to `core_features/nav`.

To access the market, use the methods in `core_features/market_access`.

**Notice there's seed data!** It's in `core_features/seed`. You have a user with your name and password `123456`. There are also two stores. Feel free to mess with the seed data.



## How I run the code (try if you run into issues)

Do once - `python -m venv venv `- this creates a virtual environment of python in the package.

Then run from cmd/powershell `venv\Scripts\Activate`

`pip install -r requirements.txt` 

In vscode, click here
![1683648852276](C:\Users\user\AppData\Roaming\Typora\typora-user-images\1683648852276.png)
Choose the one in your `venv` (should say `recommended`):

![1683648888120](C:\Users\user\AppData\Roaming\Typora\typora-user-images\1683648888120.png)

