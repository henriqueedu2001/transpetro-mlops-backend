from pathlib import Path
from ultralytics import YOLO

PROJECT_ROOT = Path(__file__).parent.resolve()
RUNS_PATH = 'teste'

def main():
    # Carrega um modelo pré-treinado
    model = YOLO('models/yolo11n.pt')  # ou yolo11s.pt, yolo11m.pt...

    # Treina
    results = model.train(
        data='src/dataset.yaml',
        epochs=1,
        imgsz=640,
        batch=2,
        workers=16,
        device='cuda',          # GPU 0. Use "cpu" para CPU.
        project= RUNS_PATH,
        name='my_training',
        exist_ok=True,
        save=True,
        verbose=True,
    )

    print('Treinamento finalizado!')
    print(f'Melhor modelo: {results.save_dir}/weights/best.pt')
    print(f'Último modelo: {results.save_dir}/weights/last.pt')
    print(f'CSV das métricas: {results.save_dir}/results.csv')


if __name__ == '__main__':
    main()