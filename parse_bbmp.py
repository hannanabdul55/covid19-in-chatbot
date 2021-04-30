import pandas as pd
from datetime import datetime, tzinfo
from dateutil import tz
from time import gmtime, strftime, localtime


def parse_url(url='https://bbmpgov.com/chbms/'):
    dfs = pd.read_html(url)
    combined_df = pd.DataFrame(
        columns=['Name of facility', 'General', 'ICU', 'ICU_Ventilator', 'High Dependency Unit',
                 'Total'])
    for df in dfs:
        cols = df.columns
        # print(cols)
        if isinstance(cols, pd.MultiIndex) and len(
                cols.levels) > 1 and 'Dedicated Covid Healthcare Centers (DCHCs)' in cols.levels[
            0] and 'Net Available Beds for C+ Patients' in cols.levels[0]:
            # extract name and facility to a new dataframe
            df = df.dropna()
            df_total = df.loc[:, ['Dedicated Covid Healthcare Centers (DCHCs)',
                                  'Net Available Beds for C+ Patients']].droplevel(0,
                                                                                   axis="columns")
            df_total = df_total.rename(columns={
                'Gen': 'General',
                'ICUVentl': 'ICU_Ventilator',
                'HDU': 'High Dependency Unit'
            })
            # display(df_total)
            combined_df = combined_df.append(df_total.loc[:, list(combined_df.columns)])
            # display(df_total)

    final_df = pd.DataFrame(
        columns=['id', 'title', 'category', 'resource type', 'address', 'pin_code', 'description',
                 'phone_1', 'phone_2', 'email', 'state', 'district', 'city', 'quantity_available',
                 'price', 'source_link', 'comment', 'created_by', 'created_on',
                 'verification_status', 'verified_by', 'last_verified_on',
                 'hospital_available_normal_beds', 'hospital_available_oxygen_beds',
                 'hospital_available_icu_beds', 'hospital_available_ventilator_beds'])
    now = str(datetime.now(tz=tz.gettz('Asia/Kolkata')).strftime('%d/%m/%y %H:%M:%S'))
    for row in combined_df.iterrows():
        data = row[1]
        item = {
            'id': row[0] + 1,
            'title': data['Name of facility'],
            'comment': 'automatically parsed from source link - BBMP website for available beds',
            'created_by': 'automatic script',
            'verified_by': 'script testing',
            'last_verified_on': now,
            'state': 'Karnataka',
            'district': 'Bengaluru (Bangalore) Urban',
            'category': 'hospital',
            'source_link': 'https://bbmpgov.com/chbms/',
            'quantity_available': data['Total'] if 'Total' in data.index else 0,
            'hospital_available_normal_beds': data['General'] if 'General' in data.index else 0
        }
        if 'General' in data.index:
            item['hospital_available_normal_beds'] = data['General']
        if 'ICU' in data.index:
            item['hospital_available_icu_beds'] = data['ICU']
        if 'ICU_Ventilator' in data.index:
            item['hospital_available_ventilator_beds'] = data['ICU_Ventilator']
        final_df = final_df.append(item, ignore_index=True)
    return final_df

FILENAME = 'bbmp_beds_data'
if __name__ == '__main__':
    df = parse_url()
    df.to_json(f"{FILENAME}.json", orient='records')
    df.to_csv(f"{FILENAME}.csv", index=False)