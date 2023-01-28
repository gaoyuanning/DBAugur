import pandas as pd
import numpy as np
import datetime
import argparse
import re
import os
import glob
import csv
import pickle

f = open('cluster-coverage/coverage.pickle', 'rb')

_, coverage = pickle.load(f)

print(coverage)