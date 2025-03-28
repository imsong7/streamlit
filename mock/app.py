# -*- coding:utf-8 -*-

import sktime
import pmdarima
import pandas as pd

def main():
    print(sktime.__version__)
    print(pmdarima.__version__)
    print(yfinance.__version__)
    print(lightgbm.__version__)
    print(prophet.__version__)
    print(statsmodels.__version__)
    print(geopandas.__version__)
    print(xmltodict.__version__)
    print(millify.__version__)

if __name__ == "__main__":
    main()
    