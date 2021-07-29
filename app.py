import geopandas as geopandas
from flask import Flask
from flask_cors import CORS
from flask_restx import Resource, Api
import pandas as pd
import json
import numpy as np
import time
from flask_caching import Cache

config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 3600
}

app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)

CORS(app)
api = Api(app)
# egrid2019_data


@api.route('/data')
class PlantsData(Resource):
    def get(self):
        print("hello")
        start_time = time.time()
        df = pd.read_excel("./static/data_backup.xlsx", sheet_name="PLNT19")
        # print(df) #SEQPLT19 - PSTATABB - PNAME - LAT - LON
        read_at = time.time()
        print(f"time to read file: {read_at - start_time}")
        df = df[["Plant name", "Plant state abbreviation", "Plant latitude", "Plant longitude", "Plant annual net generation (MWh)"]]
        df.columns = df.iloc[0]
        df = df[df.LAT.notnull()]
        df = df[df.LON.notnull()].replace({np.nan: ""})
        df = df[1:]
        filtered_at = time.time()
        print(f"time to filtered at: {filtered_at - read_at}")
        gdf = geopandas.GeoDataFrame(df,
                               geometry=geopandas.points_from_xy(df['LON'], df['LAT']))
        geopandas_at = time.time()
        print(f"time to transform pandas to geojson at: {geopandas_at - filtered_at}")
        return {'data': json.loads(gdf.to_json())}
        # return {'data': SAMPLE_DATA}


@api.route('/data_from_file')
class PlantsDataFromFile(Resource):
    def get(self):
        file = open("./static/data.json", "r")
        data = json.load(file)
        return {"data": data}


if __name__ == '__main__':
    app.run(debug=True)