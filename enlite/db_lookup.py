import argparse
from argparse import RawTextHelpFormatter

from enlite.classes.DataHandlers import DBLConfigLoader, Filehandler, DatabaseHandler
from enlite.classes.CustomExceptions import RecordNotFoundError
from enlite.classes.Reporters import Enliter


def options():
    main_parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
    subcommands = main_parser.add_subparsers(title='subcommands', dest='command', description='valid subcommands:', help='\nuse "python db_lookup.py {subcommand} --help"\n\nfor details on the usage of the subcommands\n   ')

    cpd_info_parser = subcommands.add_parser('cpd_info', help='find data on one or more compound IDs', formatter_class=RawTextHelpFormatter)
    cpd_info_parser.usage = "python db_lookup.py cpd_info [-h] input_data -i [-l] [-al] "
    cpd_info_parser.add_argument('input_data', help='one identifier or a path to a txt file containing one ID per line')
    cpd_info_parser.add_argument('-i', '--in', help="type of database ID for input\n\tm: ModelSEED\n\tc: MetaCyc\n\tk: KEGG\n\tb: BiGG", choices=['m','c','k','b'], dest='input_type', required=True, metavar="")
    cpd_info_parser.add_argument('-l', '--list', help="if set, supply a list of IDs as txt file", dest='list_input', action='store_true')
    cpd_info_parser.add_argument('-al', '--altered', help="flag for altered metacyc ID", dest='is_altered_id', action='store_true')

    rxn_info_parser = subcommands.add_parser('rxn_info', help='find data on one or more compound IDs', formatter_class=RawTextHelpFormatter)
    rxn_info_parser.usage = "python db_lookup.py rxn_info [-h] input_data -i [-l] [-al]"
    rxn_info_parser.add_argument('input_data', help='one identifier or a path to a txt file containing one ID per line')
    rxn_info_parser.add_argument('-i', '--in', help="type of database ID for input\n\tm: ModelSEED\n\tc: MetaCyc\n\tk: KEGG\n\tb: BiGG", choices=['m','c','k','b'], dest='input_type', required=True, metavar="")
    rxn_info_parser.add_argument('-l', '--list', help="if set, supply a list of IDs as txt file", dest='list_input', action='store_true')
    rxn_info_parser.add_argument('-al', '--altered', help="flag for altered metacyc ID", dest='is_altered_id', action='store_true')

    cpd_single_parser = subcommands.add_parser('cpd_single', help='find one aliases of one or more compound IDs', formatter_class=RawTextHelpFormatter)
    cpd_single_parser.usage = "python db_lookup.py cpd_single [-h] input_data -i -o [-l] [-al]"
    cpd_single_parser.add_argument('cpd_data', help='one identifier or a path to a txt file containing one ID per line')
    cpd_single_parser.add_argument('-i', '--in', help="type of database ID for input\n\tm: ModelSEED\n\tc: MetaCyc\n\tk: KEGG\n\tb: BiGG", choices=['m','c','k','b'], dest='input_type', required=True, metavar="")
    cpd_single_parser.add_argument('-o', '--out', help="type of database ID for output\n\tm: ModelSEED\n\tc: MetaCyc\n\tk: KEGG\n\tb: BiGG", choices=['m','c','k','b'], dest='output_type', required=True, metavar="")
    cpd_single_parser.add_argument('-l', '--list', help="if set, supply a list of IDs as txt file", dest='list_input', action='store_true')
    cpd_single_parser.add_argument('-al', '--altered', help="flag for altered metacyc ID", dest='is_altered_id', action='store_true')

    cpd_multi_parser = subcommands.add_parser('cpd_multi', help='find all aliases of one or more compound IDs', formatter_class=RawTextHelpFormatter)
    cpd_multi_parser.usage = "python db_lookup.py cpd_multi [-h] input_data -i -o [-l] [-al]"
    cpd_multi_parser.add_argument('cpd_data', help='one identifier or a path to a txt file containing one ID per line')
    cpd_multi_parser.add_argument('-i', '--in', help="type of database ID for input\n\tm: ModelSEED\n\tc: MetaCyc\n\tk: KEGG\n\tb: BiGG", choices=['m','c','k','b'], dest='input_type', required=True, metavar="")
    cpd_multi_parser.add_argument('-o', '--out', help="type of database ID for output\n\tm: ModelSEED\n\tc: MetaCyc\n\tk: KEGG\n\tb: BiGG", choices=['m','c','k','b'], dest='output_type', required=True, metavar="")
    cpd_multi_parser.add_argument('-l', '--list', help="if set, supply a list of IDs as txt file", dest='list_input', action='store_true')
    cpd_multi_parser.add_argument('-al', '--altered', help="flag for altered metacyc ID", dest='is_altered_id', action='store_true')

    rxn_single_parser = subcommands.add_parser('rxn_single', help='find one aliases of one or more reaction IDs', formatter_class=RawTextHelpFormatter)
    rxn_single_parser.usage = "python db_lookup.py rxn_single [-h] input_data -i -o [-l] [-al]"
    rxn_single_parser.add_argument('rxn_data', help='one identifier or a path to a txt file containing one ID per line')
    rxn_single_parser.add_argument('-i', '--in', help="type of database ID for input\n\tm: ModelSEED\n\tc: MetaCyc\n\tk: KEGG\n\tb: BiGG", choices=['m','c','k','b'], dest='input_type', required=True, metavar="")
    rxn_single_parser.add_argument('-o', '--out', help="type of database ID for output\n\tm: ModelSEED\n\tc: MetaCyc\n\tk: KEGG\n\tb: BiGG", choices=['m','c','k','b'], dest='output_type', required=True, metavar="")
    rxn_single_parser.add_argument('-l', '--list', help="if set, supply a list of IDs as txt file", dest='list_input', action='store_true')
    rxn_single_parser.add_argument('-al', '--altered', help="flag for altered metacyc ID", dest='is_altered_id', action='store_true')

    rxn_multi_parser = subcommands.add_parser('rxn_multi', help='find all aliases of one or more reaction IDs', formatter_class=RawTextHelpFormatter)
    rxn_multi_parser.usage = "python db_lookup.py rxn_multi [-h] input_data -i -o [-l] [-al]"
    rxn_multi_parser.add_argument('rxn_data', help='one identifier or a path to a txt file containing one ID per line')
    rxn_multi_parser.add_argument('-i', '--in', help="type of database ID for input\n\tm: ModelSEED\n\tc: MetaCyc\n\tk: KEGG\n\tb: BiGG", choices=['m','c','k','b'], dest='input_type', required=True, metavar="")
    rxn_multi_parser.add_argument('-o', '--out', help="type of database ID for output\n\tm: ModelSEED\n\tc: MetaCyc\n\tk: KEGG\n\tb: BiGG", choices=['m','c','k','b'], dest='output_type', required=True, metavar="")
    rxn_multi_parser.add_argument('-l', '--list', help="if set, supply a list of IDs as txt file", dest='list_input', action='store_true')
    rxn_multi_parser.add_argument('-al', '--altered', help="flag for altered metacyc ID", dest='is_altered_id', action='store_true')

    args = main_parser.parse_args()
    return args


def main():
    conf = DBLConfigLoader(config_root="config", project_root=".")
    db_handler = DatabaseHandler(conf.get_database_path())
    filehandler = Filehandler()
    enliter = Enliter(db_handler, filehandler)

    db_names_dict = {
                'a': 'all',
                'm': 'modelseed',
                'c': 'metacyc',
                'b': 'bigg',
                'k': 'kegg'
            }

    args = options()
    #print(vars(args))
    command_used = args.command

    if command_used == "cpd_info":
        input_db_name = args.input_type
        if args.list_input:
            cpd_list = filehandler.build_list(args.input_data)
        else:
            cpd_list = [args.input_data]
        print(input_db_name)
        records_found = []
        for compound_id in cpd_list:
            try:
                if input_db_name == "m":
                    cpd_record = db_handler.fetch_modelseed_cpd_info(compound_id)
                elif input_db_name == "c":
                    if args.is_altered_id:
                        cpd_record = db_handler.fetch_metacyc_cpd_info(compound_id)
                    else:
                        altered_id = db_handler.get_altered_metacyc_cpd_id(compound_id)
                        cpd_record = db_handler.fetch_metacyc_cpd_info(altered_id)
                elif input_db_name == "b":
                    cpd_record = db_handler.fetch_bigg_cpd_info(compound_id)
                elif input_db_name == "k":
                    cpd_record = db_handler.fetch_kegg_cpd_info(compound_id)
            except RecordNotFoundError:
                cpd_record = {'database_record': None}
            records_found.append(cpd_record)
        print("  ".join(cpd_record.keys()))
        for rec in records_found:
            print("  ".join([str(rec[field]) for field in rec.keys()]))

    elif command_used == "rxn_info":
        input_db_name = args.input_type
        if args.list_input:
            rxn_list = filehandler.build_list(args.input_data)
        else:
            rxn_list = [args.input_data]
        records_found = []
        for reaction_id in rxn_list:
            try:
                if input_db_name == "m":
                    rxn_record = db_handler.fetch_modelseed_rxn_info(reaction_id)
                elif input_db_name == "c":
                    if args.is_altered_id:
                        rxn_record = db_handler.fetch_metacyc_rxn_info(reaction_id)
                    else:
                        altered_id = db_handler.get_altered_metacyc_rxn_id(reaction_id)
                        rxn_record = db_handler.fetch_metacyc_rxn_info(altered_id)
                elif input_db_name == "b":
                    rxn_record = db_handler.fetch_bigg_rxn_info(reaction_id)
                elif input_db_name == "k":
                    rxn_record = db_handler.fetch_kegg_rxn_info(reaction_id)
            except RecordNotFoundError:
                rxn_record = {'database_record': None}
            records_found.append(rxn_record)
        print("  ".join(rxn_record.keys()))
        for rec in records_found:
            print("  ".join([str(rec[field]) for field in rec.keys()]))

    elif command_used == "cpd_single":
        input_db_name = db_names_dict[args.input_type]
        output_db_name = db_names_dict[args.output_type]
        if args.list_input:
            cpd_list = filehandler.build_list(args.cpd_data)
        else:
            cpd_list = [args.cpd_data]
        multiple_aliases = {}
        for compound_id in cpd_list:
            single_alias = enliter.find_compound_alias_single(compound_id, input_db_name, output_db_name, metacyc_id_is_altered=args.is_altered_id)
            multiple_aliases[compound_id] = [single_alias]
        print("Input database:", input_db_name)
        for item in multiple_aliases:
            print("\n", item)
            for k in multiple_aliases[item]:
                print("\t", k)

    elif command_used == "cpd_multi":
        input_db_name = db_names_dict[args.input_type]
        output_db_name = db_names_dict[args.output_type]
        if args.list_input:
            cpd_list = filehandler.build_list(args.cpd_data)
        else:
            cpd_list = [args.cpd_data]
        multiple_aliases = enliter.find_compound_alias_multi(cpd_list, input_db_name, output_db_name, metacyc_id_is_altered=args.is_altered_id)
        print("Input database:", input_db_name)
        for item in multiple_aliases:
            print("\n", item)
            for k in multiple_aliases[item]:
                print("\t", k)

    elif command_used == "rxn_single":
        input_db_name = db_names_dict[args.input_type]
        output_db_name = db_names_dict[args.output_type]
        if args.list_input:
            rxn_list = filehandler.build_list(args.rxn_data)
        else:
            rxn_list = [args.rxn_data]
        multiple_aliases = {}
        for reaction_id in rxn_list:
            single_alias = enliter.find_reaction_alias_single(reaction_id, input_db_name, output_db_name, metacyc_id_is_altered=args.is_altered_id)
            multiple_aliases[reaction_id] = [single_alias]
        print("Input database:", input_db_name)
        for item in multiple_aliases:
            print("\n", item)
            for k in multiple_aliases[item]:
                print("\t", k)

    elif command_used == "rxn_multi":
        input_db_name = db_names_dict[args.input_type]
        output_db_name = db_names_dict[args.output_type]
        if args.list_input:
            rxn_list = filehandler.build_list(args.rxn_data)
        else:
            rxn_list = [args.rxn_data]
        multiple_aliases = enliter.find_reaction_alias_multi(rxn_list, input_db_name, output_db_name, metacyc_id_is_altered=args.is_altered_id)
        print("Input database:", input_db_name)
        for item in multiple_aliases:
            print("\n", item)
            for k in multiple_aliases[item]:
                print("\t", k)

if __name__ == '__main__':
    main()
