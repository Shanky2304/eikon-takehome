from flask import Flask, jsonify
import pandas as pd
import numpy
import csv
from collections import Counter
from psycopg2.extensions import register_adapter, AsIs
from io import StringIO

from sqlalchemy import create_engine

def addapt_numpy_float64(numpy_float64):
    return AsIs(numpy_float64)
def addapt_numpy_int64(numpy_int64):
    return AsIs(numpy_int64)
register_adapter(numpy.float64, addapt_numpy_float64)
register_adapter(numpy.int64, addapt_numpy_int64)

def preprocessDf(df):
    columns = [column.replace(',','') for column in df.columns]
    df.columns = columns

    for index, row in df.iterrows():
        row = [str(value).replace(',', '') for value in row]
        df.loc[index] = row
    return df    


def psql_insert_copy(table, conn, keys, data_iter):
    # gets a DBAPI connection that can provide a cursor
    dbapi_conn = conn.connection
    with dbapi_conn.cursor() as cur:
        s_buf = StringIO()
        writer = csv.writer(s_buf)
        writer.writerows(data_iter)
        s_buf.seek(0)

        columns = ', '.join('"{}"'.format(k) for k in keys)
        if table.schema:
            table_name = '{}.{}'.format(table.schema, table.name)
        else:
            table_name = table.name

        sql = 'COPY {} ({}) FROM STDIN WITH CSV'.format(
            table_name, columns)
        #print(sql)
        cur.copy_expert(sql=sql, file=s_buf)


app = Flask(__name__)

# Function to load CSV files, process data, and upload to the database
def etl():
    try:
        # Extract data from the CSV files
        users_df = preprocessDf(pd.read_csv('data/users.csv', delimiter='\t'))
        user_experiments_df = preprocessDf(pd.read_csv('data/user_experiments.csv', delimiter='\t'))
        compounds_df = preprocessDf(pd.read_csv('data/compounds.csv', delimiter='\t'))

        # Transform the data
        user_experiments_df['experiment_compound_ids'] = user_experiments_df['experiment_compound_ids'].str.split(';')
        total_exp_per_user = user_experiments_df.groupby('user_id')['experiment_id'].count()
        res_df = users_df[['user_id','name']].copy()
        res_df['experiment_count'] = total_exp_per_user.values
        
        user_experiments_df['experiment_run_time'] = user_experiments_df['experiment_run_time'].astype(int)
        average_experiment_runtime = user_experiments_df.groupby('user_id')['experiment_run_time'].mean()
        most_frequent_compound_ids = user_experiments_df.groupby('user_id')['experiment_compound_ids'].apply(lambda x: Counter([item for sublist in x for item in sublist]).most_common(1)[0][0])
        most_frequent_compound_names = most_frequent_compound_ids.map(
            lambda x: compounds_df.loc[compounds_df['compound_id'] == x, 'compound_name'].values[0])

        res_df['average_experiment_runtime'] = res_df['user_id'].map(average_experiment_runtime)
        res_df['most_common_compound'] = res_df['user_id'].map(most_frequent_compound_names)
        
        # Load data into DB
        engine = create_engine('postgresql://postgres:1234@mypostgres:5432/postgres')
        res_df.to_sql('features', engine, if_exists='replace', method=psql_insert_copy, index=False)

        return True
    except Exception as e:
        print('Got exception')
        print(str(e.with_traceback()))
        return False

# API endpoint to trigger the ETL process
@app.route('/etl', methods=['POST'])
def trigger_etl():

    success = etl()

    if success:
        return jsonify({'message': 'ETL process completed successfully.'}), 200
    else:
        return jsonify({'message': 'ETL process failed.'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
