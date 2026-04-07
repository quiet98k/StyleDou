import time
import os
import sys
import argparse
from pathlib import Path


def get_parser():
    parser = argparse.ArgumentParser(description='DouDizhu Evaluation')
    parser.add_argument('--time', default=0.0, type=float)
    parser.add_argument('--frames', default=0, type=int)
    parser.add_argument('--gpu_device', default='0', type=str)
    parser.add_argument('--landlord_ckpt', default='', type=str)
    parser.add_argument('--landlord_up_ckpt', default='', type=str)
    parser.add_argument('--landlord_down_ckpt', default='', type=str)
    parser.add_argument(
        '--checkpoint_dir',
        default='douzero_checkpoints/style/style_model/',
        type=str,
    )
    return parser


def _latest_ckpt(checkpoint_dir, prefix):
    pattern = prefix + '*'
    candidates = sorted(Path(checkpoint_dir).glob(pattern), key=os.path.getmtime)
    return str(candidates[-1]) if candidates else ''


def judge():
    p = os.popen("ps aux | grep generate_eval_data.py | grep -v grep | awk '{print $2}' ")
    x = p.read()
    print(x)
    p.close()
    if not x:
        return True
    return False


def judge_test():
    p = os.popen("ps aux | grep baseline_ADP | grep -v grep | awk '{print $2}' ")
    x = p.read()
    print(x)
    p.close()
    if not x:
        return True
    return False


if __name__ == '__main__':
    args = get_parser().parse_args()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
    checkpoint_dir = args.checkpoint_dir
    if not os.path.isabs(checkpoint_dir):
        checkpoint_dir = os.path.join(repo_root, checkpoint_dir)
    if not checkpoint_dir.endswith(os.sep):
        checkpoint_dir += os.sep
    log_dir = os.path.join(checkpoint_dir, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, 'ADP_test.log')
    csv_path = os.path.join(log_dir, 'adp_eval.csv')
    landlord_ckpt = args.landlord_ckpt or _latest_ckpt(checkpoint_dir, 'landlord_weights_')
    landlord_up_ckpt = args.landlord_up_ckpt or _latest_ckpt(checkpoint_dir, 'landlord_up_weights_')
    landlord_down_ckpt = args.landlord_down_ckpt or _latest_ckpt(checkpoint_dir, 'landlord_down_weights_')
    if not (landlord_ckpt and landlord_up_ckpt and landlord_down_ckpt):
        raise FileNotFoundError('Missing style checkpoints; pass --landlord_ckpt/--landlord_up_ckpt/--landlord_down_ckpt')
    python_exec = sys.executable
    eval_path = os.path.join(script_dir, 'evaluate.py')
    eval_data_path = os.path.join(repo_root, 'eval_data.pkl')
    os.system("".join([
        python_exec,
        " ",
        eval_path,
        " --landlord ",
        landlord_ckpt,
        " --landlord_up baseline_ADP",
        " --landlord_down baseline_ADP",
        " --eval_data ",
        eval_data_path,
        " --csv_path ",
        csv_path,
        " --test_type ADP",
        " --role landlord",
        " --gpu_device ",
        str(args.gpu_device),
        " --time ",
        str(args.time),
        " --frames ",
        str(args.frames),
        " >> ",
        log_path,
    ]))
    flag1 = judge_test()
    while not flag1:
        time.sleep(30)
        flag1 = judge_test()
    os.system("".join([
        python_exec,
        " ",
        eval_path,
        " --landlord baseline_ADP",
        " --landlord_up ",
        landlord_up_ckpt,
        " --landlord_down ",
        landlord_down_ckpt,
        " --eval_data ",
        eval_data_path,
        " --csv_path ",
        csv_path,
        " --test_type ADP",
        " --role farmer",
        " --gpu_device ",
        str(args.gpu_device),
        " --time ",
        str(args.time),
        " --frames ",
        str(args.frames),
        " >> ",
        log_path,
    ]))
