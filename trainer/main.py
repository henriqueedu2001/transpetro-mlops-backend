import argparse
from pathlib import Path
import yaml
from ultralytics import YOLO

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
        type=int,
        help='The hyperparameter number of epochs.'
    )

    parser.add_argument(
        '--batch',
        default=16,
        type=int,
        help='The hyperparameter batch size.'
    )

    parser.add_argument(
        '--workers',
        default=8,
        type=int,
        help='The training parameter number of workers'
    )

    args = parser.parse_args()

    # solves the paths
    dataset_dir = Path(args.dataset_dir).resolve()
    output_dir = dataset_dir.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    epochs = args.epochs
    batch = args.batch
    workers = args.workers

    # default/fixed parameters
    yolo_model = 'yolov8n.pt'
    imgsz = 640
    device = 'cuda'
    nc = 5
    names = ['Car', 'Person', 'Motorcycle', 'Truck', 'Animal']
    exist_ok = True

    print('JOB DESCRIPTION')
    print(f'\t- dataset_dir: {dataset_dir}')
    print(f'\t- output_dir: {output_dir}')
    print(f'\t- epochs: {epochs}')
    print(f'\t- batch: {batch}')
    print(f'\t- workers: {workers}')

    # creates a data.yaml file
    data_dict = {
        'train': str(dataset_dir / 'train' / 'images'),
        'val':   str(dataset_dir / 'val' / 'images'),
        'test':  str(dataset_dir / 'test' / 'images'),  # opcional
        'nc':    nc,
        'names': names
    }

    # writes the data.yaml file
    yaml_path = output_dir / 'data.yaml'
    with open(yaml_path, 'w') as f:
        yaml.safe_dump(data_dict, f, default_flow_style=False)

    print('TRAINING PARAMETERS')
    print(f'\t- Dataset YAML: {yaml_path}')
    print(f'\t- Output: {output_dir}')
    print(f'\t- Model: {yolo_model}')
    print(f'\t- Epochs: {epochs}')
    print(f'\t- Batch: {batch}')
    print(f'\t- Image size: {imgsz}')
    print(f'\t- Workers: {workers}')
    print(f'\t- Device: {device}')
    print(f'\t- Classes: {nc}')
    print(f'\t- Names: {names}')

    # solving paths for the training
    project_parent = output_dir.parent
    project_name = output_dir.name
    if not project_name:
        project_name = "output"

    # training the model
    print(f'TRAINING EXECUTION')

    print('\t- Setting up the YOLO model...')
    model = YOLO(yolo_model)
    print('\t- Training...')

    results = model.train(
        data=str(yaml_path),
        epochs=epochs,
        batch=batch,
        imgsz=imgsz,
        workers=workers,
        device=device,
        project=str(project_parent),
        name=project_name,
        exist_ok=exist_ok,
        verbose=True
    )
    print(f'Finished!')

if __name__ == '__main__':
    main()