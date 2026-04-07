import numpy as np

import torch
from torch import nn


def _resolve_device(device):
    if isinstance(device, str):
        if device == "cpu":
            return torch.device("cpu")
        return torch.device(device)
    if device is None:
        return torch.device("cpu")
    return torch.device('cuda:' + str(device))


class StyleEncoder(nn.Module):
    def __init__(self, hidden_dim):
        super().__init__()
        self.lstm = nn.LSTM(162, hidden_dim, batch_first=True)

    def forward(self, z):
        lstm_out, _ = self.lstm(z)
        return lstm_out[:, -1, :]


class StylePredictModel(nn.Module):
    def __init__(self, style_dim=64):
        super().__init__()
        self.style_encoder = StyleEncoder(style_dim)
        self.aux_head = nn.Linear(style_dim, 15)

    def forward(self, opp_z):
        if opp_z.dim() == 3:
            opp_emb = self.style_encoder(opp_z)
            opp_emb = opp_emb.unsqueeze(0)
        elif opp_z.dim() == 4:
            batch = opp_z.size(0)
            opp_flat = opp_z.view(batch * 2, opp_z.size(2), opp_z.size(3))
            opp_emb = self.style_encoder(opp_flat)
            opp_emb = opp_emb.view(batch, 2, -1)
        else:
            raise ValueError("Unexpected opponent history shape: %s" % (tuple(opp_z.size()),))
        aux_logits = self.aux_head(opp_emb)
        return opp_emb, aux_logits


class StyleDecisionModel(nn.Module):
    def __init__(self, x_dim, style_dim=64, history_dim=128):
        super().__init__()
        self.history_lstm = nn.LSTM(162, history_dim, batch_first=True)
        self.dense1 = nn.Linear(x_dim + history_dim + 2 * style_dim, 512)
        self.dense2 = nn.Linear(512, 512)
        self.dense3 = nn.Linear(512, 512)
        self.dense4 = nn.Linear(512, 512)
        self.dense5 = nn.Linear(512, 512)
        self.dense6 = nn.Linear(512, 1)

    def _encode_history(self, z):
        lstm_out, _ = self.history_lstm(z)
        return lstm_out[:, -1, :]

    def forward(self, z, x, opp_emb):
        hist_emb = self._encode_history(z)
        if opp_emb.size(0) != hist_emb.size(0):
            if opp_emb.size(0) == 1:
                opp_emb = opp_emb.expand(hist_emb.size(0), -1, -1)
            elif hist_emb.size(0) == 1:
                hist_emb = hist_emb.expand(opp_emb.size(0), -1)
            else:
                raise ValueError("Batch mismatch between history and opponent embeddings")
        opp_1 = opp_emb[:, 0, :]
        opp_2 = opp_emb[:, 1, :]
        x = torch.cat([hist_emb, x, opp_1, opp_2], dim=-1)
        x = torch.relu(self.dense1(x))
        x = torch.relu(self.dense2(x))
        x = torch.relu(self.dense3(x))
        x = torch.relu(self.dense4(x))
        x = torch.relu(self.dense5(x))
        return self.dense6(x)


class StyleQModel(nn.Module):
    def __init__(self, x_dim, style_dim=64, history_dim=128):
        super().__init__()
        self.style_model = StylePredictModel(style_dim)
        self.decision_model = StyleDecisionModel(x_dim, style_dim, history_dim)

    def forward(self, z, x, opp_z, return_value=False, flags=None):
        opp_emb, aux_logits = self.style_model(opp_z)
        values = self.decision_model(z, x, opp_emb)
        if return_value:
            return dict(values=values, aux_logits=aux_logits)
        if flags is not None and flags.exp_epsilon > 0 and np.random.rand() < flags.exp_epsilon:
            action = torch.randint(values.shape[0], (1,))[0]
        else:
            action = torch.argmax(values, dim=0)[0]
        return dict(action=action)


class LandlordStyleModel(StyleQModel):
    def __init__(self, style_dim=64, history_dim=128):
        super().__init__(x_dim=373, style_dim=style_dim, history_dim=history_dim)


class FarmerStyleModel(StyleQModel):
    def __init__(self, style_dim=64, history_dim=128):
        super().__init__(x_dim=484, style_dim=style_dim, history_dim=history_dim)


class LandlordStylePredictModel(StylePredictModel):
    def __init__(self, style_dim=64):
        super().__init__(style_dim=style_dim)


class FarmerStylePredictModel(StylePredictModel):
    def __init__(self, style_dim=64):
        super().__init__(style_dim=style_dim)


class Base_LandlordLstmModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(162, 128, batch_first=True)
        self.dense1 = nn.Linear(373 + 128, 512)
        self.dense2 = nn.Linear(512, 512)
        self.dense3 = nn.Linear(512, 512)
        self.dense4 = nn.Linear(512, 512)
        self.dense5 = nn.Linear(512, 512)
        self.dense6 = nn.Linear(512, 1)

    def forward(self, z, x, return_value=False, flags=None):
        lstm_out, _ = self.lstm(z)
        lstm_out = lstm_out[:, -1, :]
        x = torch.cat([lstm_out, x], dim=-1)
        x = torch.relu(self.dense1(x))
        x = torch.relu(self.dense2(x))
        x = torch.relu(self.dense3(x))
        x = torch.relu(self.dense4(x))
        x = torch.relu(self.dense5(x))
        x = self.dense6(x)
        if return_value:
            return dict(values=x)
        if flags is not None and flags.exp_epsilon > 0 and np.random.rand() < flags.exp_epsilon:
            action = torch.randint(x.shape[0], (1,))[0]
        else:
            action = torch.argmax(x, dim=0)[0]
        return dict(action=action)


class Base_FarmerLstmModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(162, 128, batch_first=True)
        self.dense1 = nn.Linear(484 + 128, 512)
        self.dense2 = nn.Linear(512, 512)
        self.dense3 = nn.Linear(512, 512)
        self.dense4 = nn.Linear(512, 512)
        self.dense5 = nn.Linear(512, 512)
        self.dense6 = nn.Linear(512, 1)

    def forward(self, z, x, return_value=False, flags=None):
        lstm_out, _ = self.lstm(z)
        lstm_out = lstm_out[:, -1, :]
        x = torch.cat([lstm_out, x], dim=-1)
        x = torch.relu(self.dense1(x))
        x = torch.relu(self.dense2(x))
        x = torch.relu(self.dense3(x))
        x = torch.relu(self.dense4(x))
        x = torch.relu(self.dense5(x))
        x = self.dense6(x)
        if return_value:
            return dict(values=x)
        if flags is not None and flags.exp_epsilon > 0 and np.random.rand() < flags.exp_epsilon:
            action = torch.randint(x.shape[0], (1,))[0]
        else:
            action = torch.argmax(x, dim=0)[0]
        return dict(action=action)


baseline_model_dict = {
    'landlord': Base_LandlordLstmModel,
    'landlord_up': Base_FarmerLstmModel,
    'landlord_down': Base_FarmerLstmModel,
}

model_dict = {
    'landlord': LandlordStyleModel,
    'landlord_up': FarmerStyleModel,
    'landlord_down': FarmerStyleModel,
}

style_model_dict = {
    'landlord': LandlordStylePredictModel,
    'landlord_up': FarmerStylePredictModel,
    'landlord_down': FarmerStylePredictModel,
}


class Model:
    def __init__(self, device=0, style_dim=64, history_dim=128):
        device = _resolve_device(device)
        self.models = {}
        self.models['landlord'] = LandlordStyleModel(style_dim=style_dim, history_dim=history_dim).to(device)
        self.models['landlord_up'] = FarmerStyleModel(style_dim=style_dim, history_dim=history_dim).to(device)
        self.models['landlord_down'] = FarmerStyleModel(style_dim=style_dim, history_dim=history_dim).to(device)

    def forward(self, position, z, x, opp_z, training=False, flags=None):
        model = self.models[position]
        return model.forward(z, x, opp_z, training, flags)

    def share_memory(self):
        self.models['landlord'].share_memory()
        self.models['landlord_up'].share_memory()
        self.models['landlord_down'].share_memory()

    def eval(self):
        self.models['landlord'].eval()
        self.models['landlord_up'].eval()
        self.models['landlord_down'].eval()

    def parameters(self, position):
        return self.models[position].parameters()

    def get_model(self, position):
        return self.models[position]

    def get_models(self):
        return self.models


class Style_model:
    def __init__(self, device=0, style_dim=64):
        device = _resolve_device(device)
        self.models = {}
        self.models['landlord'] = LandlordStylePredictModel(style_dim=style_dim).to(device)
        self.models['landlord_up'] = FarmerStylePredictModel(style_dim=style_dim).to(device)
        self.models['landlord_down'] = FarmerStylePredictModel(style_dim=style_dim).to(device)

    def forward(self, position, opp_z):
        model = self.models[position]
        return model.forward(opp_z)

    def share_memory(self):
        self.models['landlord'].share_memory()
        self.models['landlord_up'].share_memory()
        self.models['landlord_down'].share_memory()

    def eval(self):
        self.models['landlord'].eval()
        self.models['landlord_up'].eval()
        self.models['landlord_down'].eval()

    def parameters(self, position):
        return self.models[position].parameters()

    def get_model(self, position):
        return self.models[position]

    def get_models(self):
        return self.models
