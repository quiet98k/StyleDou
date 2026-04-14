#!/usr/bin/env python3

import argparse
import csv
import html
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import multiprocessing as mp
import numpy as np

from generate_eval_data import generate
from style_modeling.evaluation import simulation as style_simulation


AGENT_ORDER = [
    'style_model',
    'baseline_ADP',
    'baseline_WP',
    'baseline_SL',
    'rlcard',
    'random',
]


@dataclass(frozen=True)
class AgentSpec:
    name: str
    landlord: str
    landlord_up: str
    landlord_down: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Round-robin evaluation across baseline, RLCard, random, and style models.',
    )
    parser.add_argument(
        '--eval-data',
        default='eval_data.pkl',
        help='Path to the evaluation dataset pickle.',
    )
    parser.add_argument(
        '--num-games',
        default=10000,
        type=int,
        help='Number of games to generate for each evaluation run.',
    )
    parser.add_argument(
        '--num-workers',
        default=5,
        type=int,
        help='Worker processes per matchup.',
    )
    parser.add_argument(
        '--style-dir',
        default='most_recent_model',
        help='Directory containing style_modeling checkpoints landlord.ckpt, landlord_up.ckpt, landlord_down.ckpt.',
    )
    parser.add_argument(
        '--output-dir',
        default='model_eval_results',
        help='Directory where CSV and Markdown tables will be written.',
    )
    parser.add_argument(
        '--seed',
        default=None,
        type=int,
        help='Optional numpy seed for eval data generation. Omit it to use random entropy each run.',
    )
    return parser.parse_args()


def ensure_eval_data(eval_data_path: Path, num_games: int, seed: int | None) -> None:
    seed_text = str(seed) if seed is not None else 'random'
    print(f'Generating {num_games} evaluation games to {eval_data_path} (seed={seed_text})...')

    if seed is not None:
        np.random.seed(seed)

    data = [generate() for _ in range(num_games)]
    eval_data_path.parent.mkdir(parents=True, exist_ok=True)
    with eval_data_path.open('wb') as handle:
        pickle.dump(data, handle, pickle.HIGHEST_PROTOCOL)
    print(f'Saved evaluation data to {eval_data_path}')


def build_agents(style_dir: Path) -> Dict[str, AgentSpec]:
    style_paths = {
        'landlord': style_dir / 'landlord.ckpt',
        'landlord_up': style_dir / 'landlord_up.ckpt',
        'landlord_down': style_dir / 'landlord_down.ckpt',
    }
    missing = [str(path) for path in style_paths.values() if not path.exists()]
    if missing:
        missing_text = '\n'.join(missing)
        raise FileNotFoundError(f'Missing style checkpoints:\n{missing_text}')

    return {
        'baseline_ADP': AgentSpec('baseline_ADP', 'baseline_ADP', 'baseline_ADP', 'baseline_ADP'),
        'baseline_WP': AgentSpec('baseline_WP', 'baseline_WP', 'baseline_WP', 'baseline_WP'),
        'baseline_SL': AgentSpec('baseline_SL', 'baseline_sl', 'baseline_sl', 'baseline_sl'),
        'rlcard': AgentSpec('rlcard', 'rlcard', 'rlcard', 'rlcard'),
        'random': AgentSpec('random', 'random', 'random', 'random'),
        'style_model': AgentSpec(
            'style_model',
            str(style_paths['landlord']),
            str(style_paths['landlord_up']),
            str(style_paths['landlord_down']),
        ),
    }


def reset_counters() -> None:
    counters = [
        style_simulation.num_landlord_wins,
        style_simulation.num_farmer_wins,
        style_simulation.num_landlord_scores,
        style_simulation.num_farmer_scores,
    ]
    for counter in counters:
        with counter.get_lock():
            counter.value = 0


def run_matchup(landlord_agent: AgentSpec, farmer_agent: AgentSpec, eval_data_path: Path, num_workers: int) -> Dict[str, float]:
    reset_counters()

    with eval_data_path.open('rb') as handle:
        card_play_data_list = pickle.load(handle)

    batches = style_simulation.data_allocation_per_worker(card_play_data_list, num_workers)
    model_path_dict = {
        'landlord': landlord_agent.landlord,
        'landlord_up': farmer_agent.landlord_up,
        'landlord_down': farmer_agent.landlord_down,
    }

    with mp.Pool(processes=num_workers) as pool:
        jobs = [
            pool.apply_async(style_simulation.mp_simulate, args=(batch, model_path_dict))
            for batch in batches
        ]
        for job in jobs:
            job.get()

    num_total_wins = style_simulation.num_landlord_wins.value + style_simulation.num_farmer_wins.value
    if num_total_wins == 0:
        return {
            'wp_landlord': 0.0,
            'wp_farmer': 0.0,
            'adp_landlord': 0.0,
            'adp_farmer': 0.0,
        }

    return {
        'wp_landlord': style_simulation.num_landlord_wins.value / num_total_wins,
        'wp_farmer': style_simulation.num_farmer_wins.value / num_total_wins,
        'adp_landlord': style_simulation.num_landlord_scores.value / num_total_wins,
        'adp_farmer': 2 * style_simulation.num_farmer_scores.value / num_total_wins,
    }


def write_csv(results: List[Dict[str, float]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        'landlord_agent',
        'farmer_agent',
        'wp_landlord',
        'wp_farmer',
        'adp_landlord',
        'adp_farmer',
    ]
    with output_path.open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def build_markdown_style_block() -> str:
    return '\n'.join([
        '<style>',
        '.matrix-table { border-collapse: collapse; margin: 12px 0 24px; }',
        '.matrix-table th, .matrix-table td { border: 1px solid #999; padding: 8px 10px; text-align: center; vertical-align: middle; }',
        '.matrix-table thead th { background: #f3f3f3; }',
        '.matrix-row-header { background: #f9f9f9; font-weight: 600; }',
        '.matrix-corner { position: relative; min-width: 112px; width: 112px; height: 72px; padding: 0; background: linear-gradient(to bottom right, transparent 49.2%, #666 49.5%, #666 50.5%, transparent 50.8%), linear-gradient(135deg, #f9f9f9 0%, #f9f9f9 49.5%, #eef4ff 50.5%, #eef4ff 100%); }',
        '.matrix-corner .corner-landlord { position: absolute; left: 10px; bottom: 8px; font-weight: 600; color: #000; }',
        '.matrix-corner .corner-farmers { position: absolute; right: 10px; top: 8px; font-weight: 600; color: #000; }',
        '.metric-cell { line-height: 1.4; white-space: nowrap; }',
        '</style>',
        '',
    ])


def format_matrix(agent_names: List[str], results: List[Dict[str, float]], metric_keys: List[str], title: str) -> str:
    lookup = {(row['landlord_agent'], row['farmer_agent']): row for row in results}
    lines = [f'# {title}', '']
    lines.append('<table class="matrix-table">')
    lines.append('  <thead>')
    lines.append('    <tr>')
    lines.append('      <th class="matrix-corner"><span class="corner-farmers">Farmers</span><span class="corner-landlord">Landlord</span></th>')
    for farmer_agent in agent_names:
        lines.append(f'      <th>{html.escape(farmer_agent)}</th>')
    lines.append('    </tr>')
    lines.append('  </thead>')
    lines.append('  <tbody>')

    for landlord_agent in agent_names:
        lines.append('    <tr>')
        lines.append(f'      <th class="matrix-row-header">{html.escape(landlord_agent)}</th>')
        for farmer_agent in agent_names:
            row = lookup[(landlord_agent, farmer_agent)]
            parts = [f'{key}={row[key]:.4f}' for key in metric_keys]
            lines.append(f'      <td><div class="metric-cell">{"<br>".join(parts)}</div></td>')
        lines.append('    </tr>')
    lines.append('  </tbody>')
    lines.append('</table>')
    lines.append('')
    return '\n'.join(lines)


def format_summary(agent_names: List[str], results: List[Dict[str, float]]) -> str:
    landlord_summary = {name: {'wp': [], 'adp': []} for name in agent_names}
    farmer_summary = {name: {'wp': [], 'adp': []} for name in agent_names}

    for row in results:
        landlord_summary[row['landlord_agent']]['wp'].append(row['wp_landlord'])
        landlord_summary[row['landlord_agent']]['adp'].append(row['adp_landlord'])
        farmer_summary[row['farmer_agent']]['wp'].append(row['wp_farmer'])
        farmer_summary[row['farmer_agent']]['adp'].append(row['adp_farmer'])

    lines = ['# Summary', '', '| agent | avg_landlord_wp | avg_landlord_adp | avg_farmer_wp | avg_farmer_adp |', '| --- | --- | --- | --- | --- |']
    for agent_name in agent_names:
        avg_landlord_wp = np.mean(landlord_summary[agent_name]['wp'])
        avg_landlord_adp = np.mean(landlord_summary[agent_name]['adp'])
        avg_farmer_wp = np.mean(farmer_summary[agent_name]['wp'])
        avg_farmer_adp = np.mean(farmer_summary[agent_name]['adp'])
        lines.append(
            '| {} | {:.4f} | {:.4f} | {:.4f} | {:.4f} |'.format(
                agent_name,
                avg_landlord_wp,
                avg_landlord_adp,
                avg_farmer_wp,
                avg_farmer_adp,
            )
        )
    lines.append('')
    return '\n'.join(lines)


def write_markdown(agent_names: List[str], results: List[Dict[str, float]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sections = [
        '# Model Round Robin',
        '',
        build_markdown_style_block(),
        format_summary(agent_names, results),
        format_matrix(agent_names, results, ['wp_landlord'], 'Landlord Win Rate Matrix'),
        format_matrix(agent_names, results, ['adp_landlord'], 'Landlord ADP Matrix'),
        format_matrix(agent_names, results, ['wp_landlord', 'adp_landlord'], 'Combined Landlord Metrics Matrix'),
    ]
    output_path.write_text('\n'.join(sections))


def print_run_config(args: argparse.Namespace, agent_names: List[str], eval_data_path: Path, style_dir: Path, output_dir: Path) -> None:
    seed_text = str(args.seed) if args.seed is not None else 'random'
    print('Evaluation config:')
    print(f'  eval_data: {eval_data_path}')
    print(f'  num_games: {args.num_games}')
    print(f'  num_workers: {args.num_workers}')
    print(f'  style_dir: {style_dir}')
    print(f'  output_dir: {output_dir}')
    print(f'  seed: {seed_text}')
    print(f'  agent_order: {", ".join(agent_names)}')


def main() -> None:
    args = parse_args()
    eval_data_path = Path(args.eval_data).resolve()
    style_dir = Path(args.style_dir).resolve()
    output_dir = Path(args.output_dir).resolve()

    agents = build_agents(style_dir)
    agent_names = [name for name in AGENT_ORDER if name in agents]
    agent_names.extend(name for name in agents if name not in agent_names)
    print_run_config(args, agent_names, eval_data_path, style_dir, output_dir)
    ensure_eval_data(eval_data_path, args.num_games, args.seed)

    results: List[Dict[str, float]] = []
    total_matchups = len(agent_names) * len(agent_names)
    matchup_index = 0
    for landlord_name in agent_names:
        for farmer_name in agent_names:
            matchup_index += 1
            print(f'[{matchup_index}/{total_matchups}] {landlord_name} vs {farmer_name}')
            metrics = run_matchup(agents[landlord_name], agents[farmer_name], eval_data_path, args.num_workers)
            result = {
                'landlord_agent': landlord_name,
                'farmer_agent': farmer_name,
                **metrics,
            }
            results.append(result)
            print(
                '  wp_landlord={:.4f} adp_landlord={:.4f}'.format(
                    metrics['wp_landlord'],
                    metrics['adp_landlord'],
                )
            )

    csv_path = output_dir / 'model_round_robin.csv'
    markdown_path = output_dir / 'model_round_robin.md'
    write_csv(results, csv_path)
    write_markdown(agent_names, results, markdown_path)

    print(f'Wrote CSV to {csv_path}')
    print(f'Wrote Markdown table to {markdown_path}')


if __name__ == '__main__':
    main()