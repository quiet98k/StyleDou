import os
import torch
import numpy as np

from style_modeling.env.env import test_get_obs


def _load_model(position, model_path):
    from style_modeling.dmc.models import build_style_model
    if torch.cuda.is_available():
        pretrained = torch.load(model_path, map_location='cuda:0')
    else:
        pretrained = torch.load(model_path, map_location='cpu')
    if isinstance(pretrained, dict) and 'state_dict' in pretrained and isinstance(pretrained['state_dict'], dict):
        pretrained = pretrained['state_dict']
    elif isinstance(pretrained, dict) and 'model_state_dict' in pretrained and isinstance(pretrained['model_state_dict'], dict):
        pretrained = pretrained['model_state_dict']

    model = build_style_model(position, pretrained if isinstance(pretrained, dict) else None)
    model_state_dict = model.state_dict()
    if isinstance(pretrained, dict):
        pretrained = {
            k: v for k, v in pretrained.items()
            if k in model_state_dict and model_state_dict[k].shape == v.shape
        }
        model_state_dict.update(pretrained)
    model.load_state_dict(model_state_dict)
    if torch.cuda.is_available():
        model.cuda()
    model.eval()
    return model


class DeepAgent:
    def __init__(self, position, model_path):
        self.model = _load_model(position, model_path)

    def act(self, infoset):
        if len(infoset.legal_actions) == 1:
            return infoset.legal_actions[0]

        obs = test_get_obs(infoset)

        z_batch = torch.from_numpy(obs['z_batch']).float()
        x_batch = torch.from_numpy(obs['x_batch']).float()
        opp_z = torch.from_numpy(obs['opp_z']).float()
        if torch.cuda.is_available():
            z_batch, x_batch = z_batch.cuda(), x_batch.cuda()
            opp_z = opp_z.cuda()
        y_pred = self.model.forward(z_batch, x_batch, opp_z, return_value=True)['values']
        y_pred = y_pred.detach().cpu().numpy()

        best_action_index = np.argmax(y_pred, axis=0)[0]
        best_action = infoset.legal_actions[best_action_index]

        return best_action
