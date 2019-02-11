#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ecnet/tools/database.py
# v.3.0.0
# Developed in 2019 by Travis Kessler <travis.j.kessler@gmail.com>
#
# Contains functions for creating ECNet-formatted databases
#

# Stdlib imports
from copy import deepcopy
from csv import writer, QUOTE_ALL
from os import remove

# ECNet imports
from ecnet.tools.conversions import get_smiles, smiles_to_mdl,\
    mdl_to_descriptors


def create_db(input_txt, output_name, id_prefix='', targets=None, form='name',
              smiles_file='mols.smi', mdl_file='mols.mdl',
              desc_file='descriptors.csv', clean_up=True):
    '''Create an ECNet-formatted database from either molecule names or SMILES
    strings

    Args:
        input_txt (str): path to file containing either molecule names or
            SMILES (one entry per line)
        output_name (str): path to desired database file once created
        id_prefix (str): prefix for DATAID column entries, if supplied
        targets (str): path to file containing target values (optional)
        form (str): `name` or `smiles` for selecting input format
        smiles_file (str): if input format is not SMILES, this is the name of
            a temporary .smi file containing SMILES strings
        mdl_file (str): name of MDL file generated by Open Babel
        desc_file (str): name of descriptors file generated by PaDEL-Descriptor
        clean_up (bool): if True, cleans up all files generated during
            processing except for the input text files and output database
    '''

    input_data = _read_txt(input_txt)
    if form == 'name':
        input_names = deepcopy(input_data)
        for i, d in enumerate(input_data):
            input_data[i] = get_smiles(d)
        with open(smiles_file, 'w') as smi_file:
            for d in input_data:
                smi_file.write(d + '\n')
    elif form == 'smiles':
        input_names = ['' for _ in range(len(input_data))]
        smiles_file = input_txt

    else:
        raise ValueError('Unknown `format` argument: {}'.format(form))

    if targets is not None:
        target_data = _read_txt(targets)
        if len(target_data) != len(input_data):
            raise IndexError(
                'Number of targets does not equal the number of supplied'
                ' molecules: {}, {}'.format(
                    len(target_data), len(input_data)
                )
            )
    else:
        target_data = [0 for _ in range(len(input_data))]

    smiles_to_mdl(smiles_file, mdl_file)
    desc = mdl_to_descriptors(mdl_file, desc_file)
    desc_keys = list(desc[0].keys())
    try:
        desc_keys.remove('Name')
    except:
        pass

    valid_keys = []
    for ds in desc_keys:
        is_valid = True
        for row in desc[1:]:
            if row[ds] == '' or row[ds] is None:
                row[ds] = 0
        if is_valid:
            valid_keys.append(ds)
    desc_keys = valid_keys

    rows = []
    type_row = ['DATAID', 'ASSIGNMENT', 'STRING', 'STRING', 'TARGET']
    type_row.extend(['INPUT' for _ in range(len(desc_keys))])
    title_row = ['DATAID', 'ASSIGNMENT', 'Compound Name', 'SMILES', 'Target']
    title_row.extend(desc_keys)
    rows.append(type_row)
    rows.append(title_row)

    for idx, name in enumerate(input_names):
        mol_row = [
            '{}'.format(id_prefix) + '%04d' % (idx + 1),
            'L',
            name,
            input_data[idx],
            target_data[idx]
        ]
        mol_row.extend([desc[idx][k] for k in desc_keys])
        rows.append(mol_row)

    with open(output_name, 'w', encoding='utf-8') as new_db:
        wr = writer(new_db, quoting=QUOTE_ALL, lineterminator='\n')
        for row in rows:
            wr.writerow(row)

    if clean_up:
        if form != 'smiles':
            remove(smiles_file)
        remove(mdl_file)
        remove(desc_file)


def _read_txt(file):
    '''Reads text file, returns contents

    Args:
        file (str): path to file

    Returns:
        list: each line in the text file is a list element
    '''

    with open(file, 'r') as txt_file:
        return txt_file.read().split('\n')
