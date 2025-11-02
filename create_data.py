from pipeline.pipeline import data_pipeline
import pandas as pd
import os

telem, sum = data_pipeline()

if not os.path.isdir("output"):
    os.mkdir("output")

telem.to_csv("output/telemetry.csv", index=False)
sum.to_csv("output/summary.csv", index=False)
