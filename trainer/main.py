import argparse
from time import *

def main():
    parser = argparse.ArgumentParser(
        description='The Transpetro ML Ops Tool.'
    )

    parser.add_argument(
        'dataset_dir',
        help='The directory of the dataset.'
    )

    parser.add_argument(
        '--epochs',
        default=1,
        required=False,
        help='The hyperparameter number of epochs.'
    )

    parser.add_argument(
        '--batch',
        default=16,
        required=False,
        help='The hyperparameter batch size.'
    )

    parser.add_argument(
        '--workers',
        default=8,
        required=False,
        help='The training parameter number of workers'
    )


    args = parser.parse_args()

    # arguments extraction
    dataset_dir = args.dataset_dir
    epochs = args.epochs
    batch = args.batch
    workers = args.workers
    
    print(f'JOB DESCRIPTION')
    print(f'\t- dataset_dir: {dataset_dir}')
    print(f'\t- epochs: {epochs}')
    print(f'\t- batch: {batch}')
    print(f'\t- workers: {workers}')

    print(f'JOB EXECUTION')
    print(f'\t- Starting the job...')
    sleep(1)
    print(f'\t- Running the job...')
    sleep(3)
    print(f'\t- Job finalized!')

    return


if __name__ == '__main__':
    main()