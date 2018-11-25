# Solar_Rooftops_CV
A web app where a user enters his address to receive the size of his rooftop available for solar panels. The app uses image segmentation to detect the rooftops and connects to an external API for data on the climate.

## Running the server

Using `virtualenv` (`pip install virtualenv`) run:

```
virtualenv [name_of_environment]
source [name_of_environment]/bin/activate
```

Then, simply run:

```bash
pip install -r requirements.txt
cd app
python app.py
```