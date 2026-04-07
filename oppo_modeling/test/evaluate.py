import os
import sys
import csv
import argparse
from datetime import datetime, timezone

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from oppo_modeling.evaluation.simulation import evaluate


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Dou Dizhu Evaluation')
    parser.add_argument('--landlord', type=str,
                        default='baselines/douzero_ADP/landlord.ckpt')
    parser.add_argument('--landlord_up', type=str,
                        default='baselines/sl/landlord_up.ckpt')
    parser.add_argument('--landlord_down', type=str,
                        default='baselines/sl/landlord_down.ckpt')
    parser.add_argument('--eval_data', type=str,
                        default='eval_data.pkl')
    parser.add_argument('--num_workers', type=int, default=5)
    parser.add_argument('--gpu_device', type=str, default='0')
    parser.add_argument('--time', default=0.0, type=float)
    parser.add_argument('--frames', default=0, type=int)
    parser.add_argument('--csv_path', type=str, default='')
    parser.add_argument('--test_type', type=str, default='')
    parser.add_argument('--role', type=str, default='')
    args = parser.parse_args()

    os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
    os.environ['CUDA_VISIBLE_DEVICES'] = args.gpu_device
    print('time&frames: ', args.time, args.frames)

    metrics = evaluate(
        args.landlord,
        args.landlord_up,
        args.landlord_down,
        args.eval_data,
        args.num_workers,
    )

    if args.csv_path:
        csv_dir = os.path.dirname(os.path.abspath(args.csv_path))
        if csv_dir:
            os.makedirs(csv_dir, exist_ok=True)
        row = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'test_type': args.test_type,
            'role': args.role,
            'frames': args.frames,
            'time_seconds': args.time,
            'landlord_model': args.landlord,
            'landlord_up_model': args.landlord_up,
            'landlord_down_model': args.landlord_down,
        }
        row.update(metrics)
        fieldnames = [
            'timestamp',
            'test_type',
            'role',
            'frames',
            'time_seconds',
            'landlord_model',
            'landlord_up_model',
            'landlord_down_model',
            'wp_landlord',
            'wp_farmer',
            'adp_landlord',
            'adp_farmer',
        ]
        write_header = not os.path.exists(args.csv_path)
        with open(args.csv_path, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if write_header:
                writer.writeheader()
            writer.writerow(row)
