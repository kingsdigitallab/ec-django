#!/usr/bin/env python

import os

import pandas as pd


def get_place_names(xslx_dir):
    places = []

    for fn in os.listdir(xslx_dir):
        print('.', fn)

        fn = os.path.join(xslx_dir, fn)

        df = get_sheet(fn, 'Naissances')
        df_places = get_places(df, ['father\'s ', 'mother\'s '])
        places.extend(df_places)

        df = get_sheet(fn, 'Mariages')
        df_places = get_places(df, ['groom\'s ', 'bride\'s '])
        places.extend(df_places)

        df = get_sheet(fn, 'Décès')
        df_places = get_places(df, [''])
        places.extend(df_places)

        places = list(set(places))
        places.sort(key=str.lower)

    with open('places.txt', 'w') as f:
        f.writelines('\n'.join(places))
        f.close()


def get_sheet(fn, sheet_name):
    df = pd.read_excel(fn, sheet_name=sheet_name)
    df.columns = map(str.lower, df.columns)

    return df


def get_places(df, keys):
    places = []

    for key in keys:
        places.extend(get_unique(df, ['{}domicile'.format(key)]))
        places.extend(get_unique(df, [
            '{}birthplace (locality)'.format(key),
            '{}birthplace (region or département)'.format(key)]))
        places.extend(get_unique(df, [
            '{}previous domicile (locality)'.format(key),
            '{}previous domicile (region or département)'.format(key)]))

    return places


def get_unique(df, columns):
    # columns not in the df
    if not set(columns).issubset(df.columns):
        return []

    df = df[columns].dropna(how='all').astype('str')

    return df.apply(
        lambda names: merge_place_names(names), axis=1).unique().tolist()


def merge_place_names(names):
    if isinstance(names, str):
        return names.strip()

    merged = []

    for name in names:
        name = name.strip()

        if name and name != 'nan':
            merged.append(name)

    return ', '.join(merged)


if __name__ == '__main__':
    get_place_names('xlsx')