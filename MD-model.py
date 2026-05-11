from __future__ import absolute_import

from __future__ import division

from __future__ import print_function

import logging

import math

import torch

import torch.nn as nn

from torch.nn import functional as F

import clip

from clip.simple_tokenizer import SimpleTokenizer as _Tokenizer

from .model_utils import *



_tokenizer = _Tokenizer()



# ----------------------------------------------------------------



# ----------------------------------------------------------------

class TextEncoder(nn.Module):

    def __init__(self, clip_model):

        super().__init__()

        self.transformer = clip_model.transformer

        self.positional_embedding = clip_model.positional_embedding

        self.ln_final = clip_model.ln_final

        self.text_projection = clip_model.text_projection

        self.dtype = clip_model.dtype



    def forward(self, prompts, tokenized_prompts):

        x = prompts + self.positional_embedding.type(self.dtype)

        x = x.permute(1, 0, 2)  

        x = self.transformer(x)

        x = x.permute(1, 0, 2)  

        x = self.ln_final(x).type(self.dtype)

        x = x[torch.arange(x.shape[0]), tokenized_prompts.argmax(dim=-1)] @ self.text_projection

        return x



class PromptLearner(nn.Module):

    def __init__(self, classnames, clip_model):

        super().__init__()

        n_cls = len(classnames)

        n_ctx = 16

        dtype = clip_model.dtype

        ctx_dim = clip_model.ln_final.weight.shape[0]



        ctx_vectors = torch.empty(n_ctx, ctx_dim, dtype=dtype)

        nn.init.normal_(ctx_vectors, std=0.02)

        self.ctx = nn.Parameter(ctx_vectors)  



        classnames = [name.replace("_", " ") for name in classnames]

        prompts = [name for name in classnames]

        tokenized_prompts = torch.cat([clip.tokenize(p) for p in prompts])

        with torch.no_grad():

            embedding = clip_model.token_embedding(tokenized_prompts).type(dtype)



        self.register_buffer("token_prefix", embedding[:, :1, :])  

        self.register_buffer("token_suffix", embedding[:, 1:-n_ctx, :])



        self.n_cls = n_cls

        self.n_ctx = n_ctx

        self.tokenized_prompts = tokenized_prompts



    def forward(self):

        ctx = self.ctx

        if ctx.dim() == 2:

            ctx = ctx.unsqueeze(0).expand(self.n_cls, -1, -1)

        prefix = self.token_prefix

        suffix = self.token_suffix

        prompts = torch.cat([prefix, ctx, suffix], dim=1)

        return prompts



def _no_grad_trunc_normal_(tensor, mean, std, a, b):

    def norm_cdf(x):

        return (1. + math.erf(x / math.sqrt(2.))) / 2.

    with torch.no_grad():

        l = norm_cdf((a - mean) / std)

        u = norm_cdf((b - mean) / std)

        tensor.uniform_(2 * l - 1, 2 * u - 1)

        tensor.erfinv_()

        tensor.mul_(std * math.sqrt(2.))

        tensor.add_(mean)

        tensor.clamp_(min=a, max=b)

        return tensor



def trunc_normal_(tensor, mean=0., std=1., a=-2., b=2.):

    return _no_grad_trunc_normal_(tensor, mean, std, a, b)



# ----------------------------------------------------------------



# ----------------------------------------------------------------

class ViLa_MIL_Model(nn.Module):

    def __init__(self, config, num_classes=3):

        super(ViLa_MIL_Model, self).__init__()

        self.loss_ce = nn.CrossEntropyLoss()

        self.num_classes = num_classes

        self.L = config.input_size # [N,1024] number of patches * 1024

        self.D = config.hidden_size # reduce dimension 

        self.K = 1

       

       

        self.attention_V = nn.Sequential(nn.Linear(self.L, self.D), nn.Tanh())  #tanh(L to D)

        self.attention_U = nn.Sequential(nn.Linear(self.L, self.D), nn.Sigmoid()) #sigmoid(L to D)

        self.attention_weights = nn.Linear(self.D, self.K) # D to 1 attention score 



        clip_model, _ = clip.load("RN50", device="cpu")

        self.prompt_learner = PromptLearner(config.text_prompt, clip_model.float())

        self.text_encoder = TextEncoder(clip_model.float())



        self.norm = nn.LayerNorm(config.input_size)

        self.cross_attention_1 = MultiheadAttention(embed_dim=config.input_size, num_heads=1)

        self.cross_attention_2 = MultiheadAttention(embed_dim=config.input_size, num_heads=1)



        self.learnable_image_center = nn.Parameter(torch.Tensor(*[config.prototype_number, 1, config.input_size])) 

        trunc_normal_(self.learnable_image_center, std=.02)

       

        # ==========================================================

       

        self.smoothing_T = nn.Parameter(torch.tensor(2.0))

        # ==========================================================

       

    def get_orthogonal_loss(self, features):

        norm_features = F.normalize(features, p=2, dim=1)  # transfer to unit vector

        cosine_sim = torch.mm(norm_features, norm_features.T)

        identity = torch.eye(cosine_sim.shape[0], device=cosine_sim.device) # Identity Matrix

        loss_ortho = torch.norm(cosine_sim - identity, p='fro') # add every element square of loss matrix

        return loss_ortho



    def forward(self, x_s, coord_s, x_l, coords_l, label):

        prompts = self.prompt_learner()

        tokenized_prompts = self.prompt_learner.tokenized_prompts

        text_features = self.text_encoder(prompts, tokenized_prompts) # [number of classes, 1024]



       

        M = x_s.float() #[N,1,1024]

        compents, _ = self.cross_attention_1(self.learnable_image_center, M, M) #[16,1,1024]

        H = self.norm(compents.squeeze().float() + self.learnable_image_center.squeeze()) # [16, 1024]  initial prototype+new prototype



        M_high = x_l.float()

        compents_high, _ = self.cross_attention_1(self.learnable_image_center, M_high, M_high)

        H_high = self.norm(compents_high.squeeze().float() + self.learnable_image_center.squeeze()) # [P, D]



       

        text_features_low = text_features[:self.num_classes]

        text_features_high = text_features[self.num_classes:]



       

        safe_T = torch.clamp(self.smoothing_T, min=1.0)



       

        text_query_low = text_features_low.mean(dim=0, keepdim=True) # [1, D]  [1,1024]  get the mean vector of all classes 

        semantic_gate_low = torch.mm(H, text_query_low.T.cuda()) # [P, 1] [16,1024]



       

        A_visual_low = self.attention_weights(self.attention_V(H) * self.attention_U(H)) # [P, 1] [16,1]



       

        spatial_weights_low = F.softmax((A_visual_low + semantic_gate_low) / safe_T, dim=0)  #[16,1]



       

        patch_logits_low = H @ text_features_low.T.cuda()  #[16,number of classes]
 
        logits_low = torch.sum(spatial_weights_low * patch_logits_low, dim=0, keepdim=True) #[1,number of classes]



       

        text_query_high = text_features_high.mean(dim=0, keepdim=True)

        semantic_gate_high = torch.mm(H_high, text_query_high.T.cuda())



        A_visual_high = self.attention_weights(self.attention_V(H_high) * self.attention_U(H_high))



       

        spatial_weights_high = F.softmax((A_visual_high + semantic_gate_high) / safe_T, dim=0)



        patch_logits_high = H_high @ text_features_high.T.cuda()

        logits_high = torch.sum(spatial_weights_high * patch_logits_high, dim=0, keepdim=True)



     



       

        logits = logits_low + logits_high

        loss_ce = self.loss_ce(logits, label)

       

        prob_low, prob_high = F.softmax(logits_low, dim=1), F.softmax(logits_high, dim=1)

        log_prob_low, log_prob_high = F.log_softmax(logits_low, dim=1), F.log_softmax(logits_high, dim=1)

        conf_low, conf_high = prob_low.max(dim=1, keepdim=True)[0], prob_high.max(dim=1, keepdim=True)[0]

       

        tau = 0.7

        mask_low_teaches = ((conf_low > tau) & (conf_low > conf_high)).float().detach()

        mask_high_teaches = ((conf_high > tau) & (conf_high > conf_low)).float().detach()

       

        kl_high = F.kl_div(log_prob_high, prob_low.detach(), reduction='none').sum(dim=1, keepdim=True)

        kl_low = F.kl_div(log_prob_low, prob_high.detach(), reduction='none').sum(dim=1, keepdim=True)

        loss_kl = (mask_low_teaches * kl_high + mask_high_teaches * kl_low).mean()

       

        loss_ortho = self.get_orthogonal_loss(H) + self.get_orthogonal_loss(H_high)

       

        loss = loss_ce + 0.1 * loss_kl + 0.05 * loss_ortho

       

        return F.softmax(logits, dim=1), torch.argmax(logits, dim=1), loss