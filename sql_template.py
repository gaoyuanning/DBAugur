import pandas as pd
import numpy as np
import datetime
import argparse
import re
import os
import csv

pd.set_option('max_colwidth',1000)

STATEMENTS = ['select', 'SELECT', 'INSERT', 'insert', 'UPDATE', 'update', 'delete', 'DELETE', 'create', 'CREATE']

def processData(dir, output_dir):
    for raw_file in os.listdir(dir):
        current_date = datetime.datetime.strptime(raw_file.split('.')[0], '%Y-%m-%d')
        if current_date <=  datetime.datetime.strptime('2019-01-03', '%Y-%m-%d'):
            continue
        print('##########################################################')
        print('Begin to process the logs of ' + raw_file.split('.')[0])
        raw_data = pd.read_csv(dir + raw_file)
        # raw_data['date'] = pd.to_datetime(raw_data['date'])
        # raw_data.dropna(axis=0, how='any', inplace=True)
        raw_data = raw_data[pd.notnull(raw_data['dd'])]

        templated_workload = dict()
        invalidSqlNum = 0
        attributeErrorNum = 0

        for _, row in raw_data.iterrows():
            try:
                time_stamp = f"{int(row['yy'])}-{int(row['mm'])}-{int(row['dd'])}-{int(row['hh'])}-{int(row['mi'])}-{int(row['ss'])}"
            except ValueError:
                continue
            else:
                time_stamp = pd.to_datetime(time_stamp, format='%Y-%m-%d-%H-%M-%S').replace(second=0)
            try:
                query = row['statement'].replace('\n', ' ').strip()
            except AttributeError:
                attributeErrorNum += 1
                continue

            for stmt in ['select', 'SELECT', 'INSERT', 'insert', 'UPDATE', 'update', 'delete', 'DELETE', 'create', 'CREATE']:
                idx = query.find(stmt)
                if idx >= 0:
                    break
                if idx < 0:
                    continue
            if idx >= 0:
                query = query[idx:]
                stmt = query.split(' ')[0]
                if stmt not in ['select', 'SELECT', 'INSERT', 'insert', 'UPDATE', 'update', 'delete', 'DELETE', 'create', 'CREATE']:
                    # print(stmt)
                    invalidSqlNum += 1
                    continue
                else:
                    getTemplate(query, time_stamp, templated_workload)

        print(current_date, 'Attribute Error Sql Count:', attributeErrorNum)
        print(current_date, 'Invalid Sql Statements Count:', invalidSqlNum)
        makeTemplateCSV(templated_workload, raw_file, output_dir)
        print('Finish to process the logs of ' + raw_file.split('.')[0])
        print('##########################################################')
        print('')


def getTemplate(query, time_stamp, templated_workload):  
    HASH_REGEX = r'(\'\d+\\.*?\')'  #'234\fsdf3234\fsf23'
    STRING_REGEX = r'([^\\])\'((\')|(.*?([^\\])\'))'
    DOUBLE_QUOTE_STRING_REGEX = r'([^\\])"((")|(.*?([^\\])"))'
    HEX_REGEX = r'0[xX][0-9a-fA-F]+' # '0x112d0a13a01e004f'
    INT_REGEX = r'([^a-zA-Z])-?\d+(\.\d+)?' # To prevent us from capturing table name like "a1"
    SINGLE_QUOTE_REGEX = r'\"' 

    template = re.sub(HASH_REGEX, r"@@@", query)
    template = re.sub(STRING_REGEX, r"\1&&&", template)
    template = re.sub(DOUBLE_QUOTE_STRING_REGEX, r"\1&&&", template)
    template = re.sub(HEX_REGEX, r"#", template)
    template = re.sub(INT_REGEX, r"\1#", template)
    template = re.sub(SINGLE_QUOTE_REGEX, r"", template)

    if template in templated_workload:
        # add timestamp
        if time_stamp in templated_workload[template]:
            templated_workload[template][time_stamp] += 1
        else:
            templated_workload[template][time_stamp] = 1
    else:
        templated_workload[template] = dict()
        templated_workload[template][time_stamp] = 1


def makeTemplateCSV(templated_workload, raw_file, output_dir):
    print("Generating CSV files of Templated Sql Statements", raw_file)
    
    sub_dir = raw_file.split('.')[0]
    output_dir = os.path.join(output_dir, sub_dir)
    # print(output_dir)

    # Create the result folder if not exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # delete any old existing files
    for old_file in os.listdir(output_dir):
        os.remove(output_dir + old_file)

    template_count = 0
    template_file = open(output_dir + '/' + sub_dir + '-template.txt', 'w')
    for template in templated_workload:
        template_file.write(template + '\n')
        #print(template)
        template_timestamps = templated_workload[
            template]  # time stamps for ith cluster
        #time_stamp_dict = collections.OrderedDict()
        num_queries_for_template = sum(template_timestamps.values())

        # loops over timestamps stepping by TIME_STAMP_STEP
        #for i in range(
        #        int((max_timestamp - min_timestamp) / TIME_STAMP_STEP) + 1):
        #    time_stamp = min_timestamp + (i * TIME_STAMP_STEP)
        #    if time_stamp in template_timestamps:
        #        count = template_timestamps[time_stamp]
        #    else:
        #        count = 0

        #    time_stamp_dict[time_stamp] = count

        # write to csv file
        with open(output_dir + '/template' + str(template_count) +
                  ".csv", 'w') as csvfile:
            template_writer = csv.writer(csvfile, dialect='excel')
            template_writer.writerow([num_queries_for_template, template])
            for entry in sorted(template_timestamps.keys()):
                template_writer.writerow([entry, template_timestamps[entry]])
            #for entry in time_stamp_dict:
            #    template_writer.writerow([entry, time_stamp_dict[entry]])
        csvfile.close()
        template_count += 1
    template_file.close()
    print(str(raw_file), "Template count: " + str(template_count))


if __name__ == '__main__':
    aparser = argparse.ArgumentParser(description='Templatize SQL Queries')
    aparser.add_argument('--dir', help='Input Data Directory', default='Raw_Logs/')
    # aparser.add_argument('--raw_file', help='Raw Data File', default='2019-01-03.csv')
    aparser.add_argument('--output_dir', help='Output template dir', default='Templates/')
    args = vars(aparser.parse_args())

    processData(args['dir'], args['output_dir'])