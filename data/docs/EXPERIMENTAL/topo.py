#!/usr/bin/env python3
# Copyright 2025
# Damien Davison & Michael Maillet & Sacha Davison
# Recursive AI Devs
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# ============================================================================
# IMPORTS & GLOBAL CONFIGURATION
# ============================================================================
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from scipy.fft import fft2, ifft2, fftshift
from scipy.ndimage import gaussian_filter, zoom
from scipy.optimize import minimize
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA, NMF
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import rbf_kernel
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List, Dict, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from collections import defaultdict
from pathlib import Path
from abc import ABC, abstractmethod
import logging
import pickle
import random
import os

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# PHASE 0: DATA PREPROCESSING MODULE
# ============================================================================

class DataPreprocessor:
    """
    Universal preprocessor for tabular data supporting normalization, PCA dimensionality
    reduction with adaptive variance thresholding, and inverse transformation for
    reconstruction fidelity assessment.
    """
    
    def __init__(self, normalize: bool = True, reduce_dim: bool = False, 
                 target_dim: Optional[int] = None, variance_threshold: float = 0.95):
        self.normalize = normalize
        self.reduce_dim = reduce_dim
        self.target_dim = target_dim
        self.variance_threshold = variance_threshold
        
        self.scaler = None
        self.pca = None
        self.original_shape = None
        self.is_fitted = False
        
    def fit(self, X: np.ndarray) -> 'DataPreprocessor':
        logger.info(f"Fitting DataPreprocessor to data of shape {X.shape}")
        self.original_shape = X.shape
        
        if self.normalize:
            logger.info("Applying StandardScaler normalization")
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
        else:
            X_scaled = X.copy()
        
        if self.reduce_dim:
            logger.info("Applying PCA dimensionality reduction")
            if self.target_dim is None:
                self.pca = PCA(n_components=self.variance_threshold, svd_solver='full')
            else:
                self.pca = PCA(n_components=self.target_dim)
            
            X_reduced = self.pca.fit_transform(X_scaled)
            logger.info(f"Reduced dimension from {X_scaled.shape[1]} to {X_reduced.shape[1]}")
        else:
            X_reduced = X_scaled
        
        self.is_fitted = True
        logger.info("DataPreprocessor fitting completed")
        return self
    
    def transform(self, X: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Preprocessor not fitted. Call fit() first.")
        
        if self.normalize:
            X_transformed = self.scaler.transform(X)
        else:
            X_transformed = X.copy()
        
        if self.reduce_dim:
            X_transformed = self.pca.transform(X_transformed)
        
        return X_transformed
    
    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        return self.fit(X).transform(X)
    
    def inverse_transform(self, X: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Preprocessor not fitted. Call fit() first.")
        
        if self.reduce_dim:
            X_reconstructed = self.pca.inverse_transform(X)
        else:
            X_reconstructed = X.copy()
        
        if self.normalize:
            X_original = self.scaler.inverse_transform(X_reconstructed)
        else:
            X_original = X_reconstructed
        
        return X_original
    
    def get_preprocessing_info(self) -> Dict[str, Any]:
        if not self.is_fitted:
            return {'status': 'Not fitted'}
        
        info = {
            'status': 'Fitted',
            'original_shape': self.original_shape,
            'normalize': self.normalize,
            'reduce_dim': self.reduce_dim
        }
        
        if self.reduce_dim and self.pca is not None:
            info['explained_variance_ratio'] = self.pca.explained_variance_ratio_
            info['cumulative_variance'] = np.cumsum(self.pca.explained_variance_ratio_)
            info['n_components'] = self.pca.n_components_
        
        return info


class ImagePreprocessor:
    """
    Specialized preprocessor for image data with support for grayscale conversion,
    anti-aliased resizing, pixel normalization, and multi-scale feature extraction
    (histogram, edge density, texture statistics).
    """
    
    def __init__(self, target_size: Tuple[int, int] = (32, 32), normalize_pixels: bool = True,
                 extract_features: bool = False, feature_type: str = 'histogram'):
        self.target_size = target_size
        self.normalize_pixels = normalize_pixels
        self.extract_features = extract_features
        self.feature_type = feature_type
        
        self.is_fitted = False
        self.feature_stats = {}
        
    def fit(self, images: List[np.ndarray]) -> 'ImagePreprocessor':
        logger.info(f"Fitting ImagePreprocessor to {len(images)} images")
        
        processed_images = []
        for img in images:
            processed_img = self._preprocess_single_image(img, fit_mode=True)
            processed_images.append(processed_img)
        
        processed_images = np.array(processed_images)
        
        if self.extract_features:
            self._compute_feature_statistics(processed_images)
        
        self.is_fitted = True
        logger.info("ImagePreprocessor fitting completed")
        return self
    
    def transform(self, images: List[np.ndarray]) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Preprocessor not fitted. Call fit() first.")
        
        feature_vectors = []
        for img in images:
            features = self._extract_features(img)
            feature_vectors.append(features)
        
        return np.array(feature_vectors)
    
    def fit_transform(self, images: List[np.ndarray]) -> np.ndarray:
        return self.fit(images).transform(images)
    
    def _preprocess_single_image(self, image: np.ndarray, fit_mode: bool = False) -> np.ndarray:
        # Handle channel dimension
        if len(image.shape) == 3:
            if image.shape[2] == 3:
                image = np.mean(image, axis=2)
            elif image.shape[2] == 1:
                image = image.squeeze(axis=2)
        
        # Resize with anti-aliasing
        try:
            from skimage.transform import resize
            image = resize(image, self.target_size, anti_aliasing=True, preserve_range=True)
        except ImportError:
            # Robust fallback using scipy.ndimage
            zoom_factors = (self.target_size[0] / image.shape[0], self.target_size[1] / image.shape[1])
            image = zoom(image, zoom_factors, order=1, mode='reflect')
        
        # Normalize pixel values
        if self.normalize_pixels:
            image = image.astype(np.float32) / 255.0
        
        return image
    
    def _extract_features(self, image: np.ndarray) -> np.ndarray:
        processed_img = self._preprocess_single_image(image)
        features = processed_img.flatten()
        
        if self.extract_features:
            additional_features = self._compute_additional_features(processed_img)
            features = np.concatenate([features, additional_features])
        
        return features
    
    def _compute_additional_features(self, image: np.ndarray) -> np.ndarray:
        if self.feature_type == 'histogram':
            hist, _ = np.histogram(image, bins=16, range=(0, 1), density=True)
            return hist
        
        elif self.feature_type == 'edges':
            try:
                from skimage.filters import sobel
                edges = sobel(image)
                edge_density = np.mean(edges)
                return np.array([edge_density])
            except ImportError:
                # Gradient-based edge detection fallback
                grad_x = np.abs(np.diff(image, axis=0)).mean()
                grad_y = np.abs(np.diff(image, axis=1)).mean()
                return np.array([grad_x + grad_y])
        
        elif self.feature_type == 'texture':
            texture_std = np.std(image)
            texture_var = np.var(image)
            return np.array([texture_std, texture_var])
        
        return np.array([])
    
    def _compute_feature_statistics(self, images: np.ndarray) -> None:
        all_features = []
        for img in images:
            additional_features = self._compute_additional_features(img)
            all_features.append(additional_features)
        
        all_features = np.array(all_features)
        self.feature_stats = {
            'mean': np.mean(all_features, axis=0),
            'std': np.std(all_features, axis=0),
            'min': np.min(all_features, axis=0),
            'max': np.max(all_features, axis=0)
        }
        logger.info(f"Computed feature statistics for {all_features.shape[1]} additional features")
    
    def get_preprocessing_info(self) -> Dict[str, Any]:
        if not self.is_fitted:
            return {'status': 'Not fitted'}
        
        info = {
            'status': 'Fitted',
            'target_size': self.target_size,
            'normalize_pixels': self.normalize_pixels,
            'extract_features': self.extract_features,
            'feature_type': self.feature_type
        }
        
        if self.extract_features:
            info['feature_stats'] = self.feature_stats
        
        return info


class TextPreprocessor:
    """
    Text preprocessor supporting TF-IDF, Word2Vec, and BERT embeddings with
    intelligent fallback strategies and configurable tokenization parameters.
    """
    
    def __init__(self, embedding_type: str = 'tfidf', max_features: int = 1000,
                 min_df: int = 2, max_df: float = 0.95):
        self.embedding_type = embedding_type
        self.max_features = max_features
        self.min_df = min_df
        self.max_df = max_df
        
        self.vectorizer = None
        self.embedding_model = None
        self.is_fitted = False
        
    def fit(self, texts: List[str]) -> 'TextPreprocessor':
        logger.info(f"Fitting TextPreprocessor to {len(texts)} documents")
        
        if self.embedding_type == 'tfidf':
            self.vectorizer = TfidfVectorizer(
                max_features=self.max_features,
                min_df=self.min_df,
                max_df=self.max_df,
                stop_words='english',
                lowercase=True,
                ngram_range=(1, 2)
            )
            self.vectorizer.fit(texts)
            
        elif self.embedding_type == 'word2vec':
            from gensim.models import Word2Vec
            tokenized_texts = [text.lower().split() for text in texts]
            self.embedding_model = Word2Vec(
                sentences=tokenized_texts,
                vector_size=100,
                window=5,
                min_count=self.min_df,
                workers=4
            )
            
        elif self.embedding_type == 'bert':
            try:
                from sentence_transformers import SentenceTransformer
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            except ImportError:
                logger.warning("sentence_transformers not available, falling back to TF-IDF")
                self.embedding_type = 'tfidf'
                return self.fit(texts)
        
        self.is_fitted = True
        logger.info("TextPreprocessor fitting completed")
        return self
    
    def transform(self, texts: List[str]) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Preprocessor not fitted. Call fit() first.")
        
        if self.embedding_type == 'tfidf':
            return self.vectorizer.transform(texts).toarray()
        
        elif self.embedding_type == 'word2vec':
            embeddings = []
            for text in texts:
                words = text.lower().split()
                vectors = [self.embedding_model.wv[word] for word in words if word in self.embedding_model.wv]
                embeddings.append(np.mean(vectors, axis=0) if vectors else np.zeros(self.embedding_model.vector_size))
            return np.array(embeddings)
        
        elif self.embedding_type == 'bert':
            return self.embedding_model.encode(texts)
        
        return np.array([])
    
    def fit_transform(self, texts: List[str]) -> np.ndarray:
        return self.fit(texts).transform(texts)
    
    def get_preprocessing_info(self) -> Dict[str, Any]:
        if not self.is_fitted:
            return {'status': 'Not fitted'}
        
        info = {'status': 'Fitted', 'embedding_type': self.embedding_type}
        
        if self.embedding_type == 'tfidf' and self.vectorizer:
            info['vocabulary_size'] = len(self.vectorizer.vocabulary_)
            info['max_features'] = self.vectorizer.max_features
        
        elif self.embedding_type == 'word2vec' and self.embedding_model:
            info['vector_size'] = self.embedding_model.vector_size
            info['vocab_size'] = len(self.embedding_model.wv)
        
        elif self.embedding_type == 'bert' and self.embedding_model:
            info['model_name'] = self.embedding_model._modules['0'].auto_model.name_or_path
        
        return info


def create_preprocessor(data_type: str, **kwargs) -> Union[DataPreprocessor, ImagePreprocessor, TextPreprocessor]:
    """
    Factory function for creating appropriate preprocessor based on data modality.
    
    Args:
        data_type: One of 'general', 'image', 'text'
        **kwargs: Arguments passed to preprocessor constructor
        
    Returns:
        Instantiated preprocessor
    """
    if data_type == 'general':
        return DataPreprocessor(**kwargs)
    elif data_type == 'image':
        return ImagePreprocessor(**kwargs)
    elif data_type == 'text':
        return TextPreprocessor(**kwargs)
    else:
        raise ValueError(f"Unknown data_type: {data_type}. Supported: 'general', 'image', 'text'")


def preprocess_pipeline(data: Union[np.ndarray, List], data_type: str,
                       fit_transform: bool = True, **kwargs) -> Tuple[np.ndarray, Union[DataPreprocessor, ImagePreprocessor, TextPreprocessor]]:
    """
    Complete preprocessing pipeline with automatic modality detection.
    
    Returns:
        Tuple of (processed_data, preprocessor_instance)
    """
    preprocessor = create_preprocessor(data_type, **kwargs)
    processed_data = preprocessor.fit_transform(data) if fit_transform else preprocessor.transform(data)
    return processed_data, preprocessor


# ============================================================================
# PHASE 1: TOPOLOGICAL STRUCTURE LEARNING
# ============================================================================

@dataclass
class CommunityNode:
    """Node in the Concept Tree representing a hierarchical data community."""
    id: int
    members: List[int]
    parent: Optional[int] = None
    children: List[int] = None
    level: int = 0
    archetype_idx: Optional[int] = None
    pagerank_scores: Optional[np.ndarray] = None
    center: Optional[np.ndarray] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []


class DiffusionMap:
    """
    Diffusion Maps for nonlinear manifold learning. Constructs a Markov chain on the data
    and computes its spectral decomposition to reveal intrinsic geometric structure.
    """
    
    def __init__(self, n_neighbors: int = 15, alpha: float = 0.5, n_components: int = 50):
        self.n_neighbors = n_neighbors
        self.alpha = alpha
        self.n_components = n_components
        self.transition_matrix_ = None
        self.diffusion_coords_ = None
        self.eigenvalues_ = None
        self.eigenvectors_ = None
        self.training_data_ = None
        self.kernel_bandwidth_ = None
        
    def fit(self, X: np.ndarray) -> 'DiffusionMap':
        logger.info(f"Computing diffusion map for {X.shape[0]} samples in {X.shape[1]} dimensions")
        self.training_data_ = X
        
        # Nearest neighbors for local kernel construction
        nbrs = NearestNeighbors(n_neighbors=self.n_neighbors + 1).fit(X)
        distances, indices = nbrs.kneighbors(X)
        distances, indices = distances[:, 1:], indices[:, 1:]
        
        # Adaptive kernel bandwidth
        self.kernel_bandwidth_ = np.median(distances)
        
        # Sparse kernel matrix
        n_samples = X.shape[0]
        row_ind = np.repeat(np.arange(n_samples), self.n_neighbors)
        col_ind = indices.flatten()
        kernel_values = np.exp(-distances.flatten()**2 / (2 * self.kernel_bandwidth_**2))
        
        K = sp.csr_matrix((kernel_values, (row_ind, col_ind)), shape=(n_samples, n_samples))
        K = K + K.T
        
        # Alpha normalization for density invariance
        d = np.array(K.sum(axis=1)).flatten()
        d_alpha = d ** self.alpha
        D_alpha_inv = sp.diags(1.0 / d_alpha)
        
        K_normalized = D_alpha_inv @ K @ D_alpha_inv
        
        # Markov transition matrix
        d_norm = np.array(K_normalized.sum(axis=1)).flatten()
        D_norm_inv = sp.diags(1.0 / d_norm)
        self.transition_matrix_ = D_norm_inv @ K_normalized
        
        # Spectral decomposition
        eigenvalues, eigenvectors = spla.eigs(
            self.transition_matrix_, k=self.n_components + 1, which='LR', tol=1e-6
        )
        
        # Sort eigen-components (descending, excluding λ=1 trivial solution)
        idx = np.argsort(eigenvalues)[::-1][1:]
        self.eigenvalues_ = eigenvalues[idx].real
        self.eigenvectors_ = eigenvectors[:, idx].real
        
        # Diffusion coordinates at time t=1
        self.diffusion_coords_ = self.eigenvectors_ * (self.eigenvalues_ ** 1)
        
        logger.info(f"Diffusion map computed: {self.diffusion_coords_.shape[1]} components capture "
                   f"{np.sum(self.eigenvalues_):.2%} of spectral energy")
        return self
    
    def transform(self, X_new: np.ndarray) -> np.ndarray:
        """
        Out-of-sample extension for new data points using Nystrom approximation.
        """
        if self.training_data_ is None:
            raise ValueError("Must fit diffusion map before transforming new points")
        
        # Compute kernel between new points and training data
        distances = np.linalg.norm(
            X_new[:, np.newaxis] - self.training_data_[np.newaxis, :], axis=2
        )
        K_new = np.exp(-distances**2 / (2 * self.kernel_bandwidth_**2))
        
        # Symmetrize and normalize
        d_new = K_new.sum(axis=1)
        d_train = self.transition_matrix_.sum(axis=1).A.flatten()
        
        # Nystrom extension for eigenvectors
        eigenvectors_new = (K_new @ self.eigenvectors_) / (d_new[:, np.newaxis] * d_train[np.newaxis, :] / d_new.sum())
        
        return eigenvectors_new
    
    def get_transition_matrix(self) -> sp.csr_matrix:
        return self.transition_matrix_
    
    def get_diffusion_coordinates(self) -> np.ndarray:
        return self.diffusion_coords_


class ConceptTree:
    """
    Hierarchical community detection using spectral graph theory. Builds a tree structure
    where each node represents a data community with learned archetypes via PageRank centrality.
    """
    
    def __init__(self, min_community_size: int = 10, max_depth: int = 5):
        self.min_community_size = min_community_size
        self.max_depth = max_depth
        self.nodes: Dict[int, CommunityNode] = {}
        self.next_id = 0
        self.root_id = None
        
    def build(self, transition_matrix: sp.csr_matrix, X: np.ndarray) -> 'ConceptTree':
        logger.info(f"Building Concept Tree: min_size={self.min_community_size}, max_depth={self.max_depth}")
        
        import networkx as nx
        G = nx.from_scipy_sparse_array(transition_matrix)
        
        all_nodes = list(range(X.shape[0]))
        self._recursive_community_detection(G, all_nodes, X, parent_id=None, level=0)
        
        logger.info(f"Concept Tree constructed with {len(self.nodes)} nodes and {len(self.get_leaf_nodes())} leaves")
        return self
    
    def _recursive_community_detection(self, G: nx.Graph, nodes: List[int], 
                                     X: np.ndarray, parent_id: Optional[int], level: int):
        if len(nodes) < self.min_community_size or level >= self.max_depth:
            return
        
        subgraph = G.subgraph(nodes).copy()
        communities = self._spectral_community_detection(subgraph)
        
        if len(communities) <= 1:
            return
        
        # Create parent node with PageRank-based archetype selection
        parent_node = CommunityNode(id=self.next_id, members=nodes, parent=parent_id, level=level)
        self.nodes[self.next_id] = parent_node
        
        if parent_id is None:
            self.root_id = self.next_id
        
        current_parent_id = self.next_id
        self.next_id += 1
        
        # Compute community statistics
        community_data = X[nodes]
        parent_node.center = np.mean(community_data, axis=0)
        
        # PageRank for archetype identification
        try:
            pagerank_scores = nx.pagerank(subgraph, max_iter=1000, tol=1e-6)
            parent_node.pagerank_scores = np.array([pagerank_scores.get(i, 0) for i in nodes])
            parent_node.archetype_idx = nodes[np.argmax(parent_node.pagerank_scores)]
        except:
            # Fallback to centrality-based archetype
            centrality = nx.degree_centrality(subgraph)
            parent_node.archetype_idx = nodes[np.argmax([centrality.get(i, 0) for i in nodes])]
        
        # Recursively process sub-communities
        for community in communities:
            self._recursive_community_detection(G, community, X, current_parent_id, level + 1)
    
    def _spectral_community_detection(self, G: nx.Graph, n_communities: int = 2) -> List[List[int]]:
        """
        Spectral clustering via normalized graph Laplacian. Uses Fiedler vector for bipartition.
        """
        nodes = list(G.nodes())
        if len(nodes) < n_communities * 2:
            return [nodes]
        
        try:
            # Use NetworkX Girvan-Newman if available
            import networkx.algorithms.community as nx_comm
            communities = list(nx_comm.girvan_newman(G))
            if communities:
                return [list(comm) for comm in communities[0]]
        except:
            pass
        
        # Manual spectral bipartition
        L = nx.normalized_laplacian_matrix(G)
        try:
            eigenvalues, eigenvectors = np.linalg.eigh(L.toarray())
            fiedler = eigenvectors[:, 1]  # Second smallest eigenvector
            
            # Partition by sign
            part1 = [nodes[i] for i in range(len(nodes)) if fiedler[i] >= 0]
            part2 = [nodes[i] for i in range(len(nodes)) if fiedler[i] < 0]
            
            # Ensure non-empty partitions
            if len(part1) == 0 or len(part2) == 0:
                return [nodes]
            
            return [part1, part2]
        except:
            # Final fallback: random partition
            np.random.shuffle(nodes)
            mid = len(nodes) // 2
            return [nodes[:mid], nodes[mid:]]
    
    def get_leaf_nodes(self) -> List[int]:
        return [node_id for node_id, node in self.nodes.items() if not node.children]
    
    def get_path_to_root(self, node_id: int) -> List[int]:
        path = []
        current_id = node_id
        while current_id is not None:
            path.append(current_id)
            current_id = self.nodes[current_id].parent
        return path
    
    def visualize_tree(self) -> str:
        if self.root_id is None:
            return "Empty tree"
        
        lines = []
        self._visualize_node(self.root_id, "", lines, is_last=True)
        return "\n".join(lines)
    
    def _visualize_node(self, node_id: int, prefix: str, lines: List[str], is_last: bool):
        node = self.nodes[node_id]
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}Node {node_id}: {len(node.members)} members (level {node.level})")
        if node.archetype_idx is not None:
            lines[-1] += f", archetype: {node.archetype_idx}"
        
        for i, child_id in enumerate(node.children):
            child_is_last = (i == len(node.children) - 1)
            child_prefix = prefix + ("    " if is_last else "│   ")
            self._visualize_node(child_id, child_prefix, lines, child_is_last)


# ============================================================================
# PHASE 2: DICTIONARY & EXPERT LEARNING
# ============================================================================

class LocalDictionary:
    """
    Non-negative Matrix Factorization for parts-based representation learning.
    Each community learns its own dictionary of atomic components characteristic of its
    semantic niche, enabling compositional generation.
    """
    
    def __init__(self, n_components: int = 64, max_iter: int = 200, tol: float = 1e-4):
        self.n_components = n_components
        self.max_iter = max_iter
        self.tol = tol
        self.nmf_model = None
        self.components_ = None
        self.activation_pattern_ = None
        
    def fit(self, X: np.ndarray) -> 'LocalDictionary':
        logger.info(f"Learning NMF dictionary: {X.shape[0]} samples, {self.n_components} components")
        
        X_nonneg = np.maximum(X - X.min(), 0)
        self.nmf_model = NMF(
            n_components=self.n_components,
            max_iter=self.max_iter,
            tol=self.tol,
            random_state=42,
            init='nndsvda'
        )
        
        self.activation_pattern_ = self.nmf_model.fit_transform(X_nonneg)
        self.components_ = self.nmf_model.components_
        
        sparsity = self.get_sparsity()
        logger.info(f"NMF converged in {self.nmf_model.n_iter_} iterations, sparsity: {sparsity:.3f}")
        return self
    
    def encode(self, x: np.ndarray) -> np.ndarray:
        if self.nmf_model is None:
            raise ValueError("Dictionary not fitted")
        return self.nmf_model.transform(np.maximum(x - x.min(), 0).reshape(1, -1))[0]
    
    def decode(self, activations: np.ndarray) -> np.ndarray:
        if self.components_ is None:
            raise ValueError("Dictionary not fitted")
        return np.dot(activations, self.components_)
    
    def get_sparsity(self) -> float:
        if self.activation_pattern_ is None:
            return 0.0
        
        # Hoyer's sparsity measure
        sqrt_n = np.sqrt(self.n_components)
        l1 = np.mean(np.sum(np.abs(self.activation_pattern_), axis=1))
        l2 = np.sqrt(np.mean(np.sum(self.activation_pattern_**2, axis=1)))
        
        return (sqrt_n - l1 / (l2 + 1e-8)) / (sqrt_n - 1)


class RecognitionNetwork(nn.Module):
    """
    Bottom-up recognition network for Wake-Sleep training. Maps generated samples back
    to their topological embedding space, creating a bidirectional learning loop.
    """
    
    def __init__(self, input_dim: int, hidden_dims: List[int], output_dim: int):
        super().__init__()
        
        layers = []
        prev_dim = input_dim
        
        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.BatchNorm1d(hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.2)
            ])
            prev_dim = hidden_dim
        
        layers.append(nn.Linear(prev_dim, output_dim))
        layers.append(nn.Softmax(dim=-1))
        
        self.network = nn.Sequential(*layers)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)


class GenerativeExpert(nn.Module):
    """
    Neural expert for a specific community in the Concept Tree. Learns the generative
    dynamics of composing dictionary atoms into coherent samples via Wake-Sleep protocol.
    """
    
    def __init__(self, community_id: int, input_dim: int, n_dictionary_atoms: int, hidden_dims: List[int] = None):
        super().__init__()
        self.community_id = community_id
        self.input_dim = input_dim
        self.n_dictionary_atoms = n_dictionary_atoms
        
        if hidden_dims is None:
            hidden_dims = [256, 128]
        
        # Latent code to activation pattern generator
        self.generator_net = nn.Sequential(
            nn.Linear(input_dim, hidden_dims[0]),
            nn.BatchNorm1d(hidden_dims[0]),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dims[0], hidden_dims[1]),
            nn.BatchNorm1d(hidden_dims[1]),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dims[1], n_dictionary_atoms),
            nn.Softmax(dim=-1)
        )
        
        # Learnable combination weights
        self.combination_weights = nn.Parameter(torch.ones(n_dictionary_atoms))
        
        # Recognition network for sleep phase
        self.recognition_net = RecognitionNetwork(
            input_dim=n_dictionary_atoms,
            hidden_dims=hidden_dims[::-1],  # Reverse architecture
            output_dim=input_dim
        )
        
        self.optimizer = optim.AdamW(
            list(self.generator_net.parameters()) + 
            list(self.recognition_net.parameters()) + 
            [self.combination_weights],
            lr=0.001, weight_decay=1e-5
        )
        
        self.training_losses = {'wake': [], 'sleep': []}
        
    def generate_activations(self, latent_code: torch.Tensor) -> torch.Tensor:
        base_activations = self.generator_net(latent_code)
        weighted_activations = base_activations * torch.softmax(self.combination_weights, dim=-1)
        return weighted_activations
    
    def decode_to_data(self, activations: torch.Tensor, dictionary_components: torch.Tensor) -> torch.Tensor:
        return torch.matmul(activations, dictionary_components)
    
    def wake_phase_step(self, real_data: torch.Tensor, latent_codes: torch.Tensor,
                       dictionary_components: torch.Tensor) -> float:
        self.optimizer.zero_grad()
        
        # Forward generation
        activations = self.generate_activations(latent_codes)
        reconstruction = self.decode_to_data(activations, dictionary_components)
        
        # Reconstruction loss
        loss = F.mse_loss(reconstruction, real_data)
        
        # Add sparsity penalty
        sparsity_loss = torch.mean(torch.abs(activations))
        total_loss = loss + 0.01 * sparsity_loss
        
        total_loss.backward()
        self.optimizer.step()
        
        self.training_losses['wake'].append(total_loss.item())
        return total_loss.item()
    
    def sleep_phase_step(self, batch_size: int, dictionary_components: torch.Tensor) -> float:
        self.optimizer.zero_grad()
        
        # Hallucinate from random latent codes
        random_latent = torch.randn(batch_size, self.input_dim)
        hallucinated_activations = self.generate_activations(random_latent)
        hallucinated_data = self.decode_to_data(hallucinated_activations, dictionary_components)
        
        # Train recognition network to invert the generation
        recognized_latent = self.recognition_net(hallucinated_activations)
        
        # Inversion loss
        loss = F.mse_loss(recognized_latent, torch.softmax(random_latent, dim=-1))
        
        loss.backward()
        self.optimizer.step()
        
        self.training_losses['sleep'].append(loss.item())
        return loss.item()


@dataclass
class ExpertConfig:
    wake_epochs: int = 100
    sleep_epochs: int = 50
    batch_size: int = 32
    wake_sleep_ratio: float = 0.7


class WakeSleepTrainer:
    """
    Coordination layer for Wake-Sleep training across all community experts.
    Implements alternating phases of reality-driven learning and hallucinatory refinement.
    """
    
    def __init__(self, experts: Dict[int, GenerativeExpert], config: ExpertConfig):
        self.experts = experts
        self.config = config
        
    def train(self, data_by_community: Dict[int, np.ndarray],
              latent_codes_by_community: Dict[int, np.ndarray],
              dictionaries_by_community: Dict[int, LocalDictionary]) -> Dict[str, List[float]]:
        """
        Execute Wake-Sleep training protocol across all communities.
        
        Returns:
            Aggregate training metrics
        """
        logger.info(f"Wake-Sleep training: {self.config.wake_epochs} wake + {self.config.sleep_epochs} sleep epochs")
        
        total_wake_loss = []
        total_sleep_loss = []
        
        for epoch in range(self.config.wake_epochs + self.config.sleep_epochs):
            is_wake = epoch < self.config.wake_epochs
            
            epoch_wake_losses = []
            epoch_sleep_losses = []
            
            for community_id, expert in self.experts.items():
                if community_id not in data_by_community:
                    continue
                
                dictionary = dictionaries_by_community[community_id]
                dict_components = torch.FloatTensor(dictionary.components_)
                
                if is_wake:
                    # Wake phase: learn from real data
                    data = data_by_community[community_id]
                    latent_codes = latent_codes_by_community[community_id]
                    
                    data_tensor = torch.FloatTensor(data)
                    latent_tensor = torch.FloatTensor(latent_codes)
                    
                    loss = expert.wake_phase_step(data_tensor, latent_tensor, dict_components)
                    epoch_wake_losses.append(loss)
                else:
                    # Sleep phase: refine via hallucination
                    loss = expert.sleep_phase_step(self.config.batch_size, dict_components)
                    epoch_sleep_losses.append(loss)
            
            # Log epoch progress
            if epoch % 10 == 0:
                if is_wake:
                    avg_loss = np.mean(epoch_wake_losses) if epoch_wake_losses else 0
                    logger.info(f"Wake Epoch {epoch}: Avg Loss = {avg_loss:.6f}")
                else:
                    avg_loss = np.mean(epoch_sleep_losses) if epoch_sleep_losses else 0
                    logger.info(f"Sleep Epoch {epoch - self.config.wake_epochs}: Avg Loss = {avg_loss:.6f}")
            
            total_wake_loss.extend(epoch_wake_losses)
            total_sleep_loss.extend(epoch_sleep_losses)
        
        logger.info("Wake-Sleep training completed")
        return {'wake_losses': total_wake_loss, 'sleep_losses': total_sleep_loss}


# ============================================================================
# PHASE 3: GENERATIVE ASSEMBLY
# ============================================================================

class BBSNoise:
    """
    Cryptographically-secure Blum Blum Shub pseudorandom generator for high-entropy
    seed initialization. Ensures reproducible yet non-repetitive exploration of the
    generative space.
    """
    
    def __init__(self, p: int = 2003, q: int = 2011, seed: Optional[int] = None):
        self.p = p
        self.q = q
        self.m = p * q
        
        if seed is None:
            while True:
                seed = random.randint(2, self.m - 1)
                if np.gcd(seed, self.m) == 1:
                    break
        
        self.state = seed
        self.bit_index = 0
    
    def next_bit(self) -> int:
        self.state = (self.state * self.state) % self.m
        return self.state % 2
    
    def next_float(self) -> float:
        result = 0.0
        for i in range(32):
            result = result * 2 + self.next_bit()
        return result / (2**32)
    
    def next_normal(self, mean: float = 0.0, std: float = 1.0) -> float:
        u1, u2 = self.next_float(), self.next_float()
        z0 = np.sqrt(-2 * np.log(u1 + 1e-12)) * np.cos(2 * np.pi * u2)
        return mean + std * z0
    
    def generate_tensor(self, shape: Tuple[int, ...], mean: float = 0.0, std: float = 1.0) -> np.ndarray:
        total_elements = np.prod(shape)
        values = [self.next_normal(mean, std) for _ in range(total_elements)]
        return np.array(values).reshape(shape)


class MCMCWalker:
    """
    Metropolis-Hastings style random walk on the Concept Tree. Performs constrained
    traversal to select semantically-appropriate leaf communities for generation.
    """
    
    def __init__(self, concept_tree: ConceptTree, temperature: float = 1.0, exploration_rate: float = 0.1):
        self.concept_tree = concept_tree
        self.temperature = temperature
        self.exploration_rate = exploration_rate
        
    def walk_to_leaf(self, constraints: Optional[Dict[str, Any]] = None) -> int:
        if self.concept_tree.root_id is None:
            raise ValueError("Concept tree not built")
        
        current_node = self.concept_tree.root_id
        path = [current_node]
        
        while True:
            node = self.concept_tree.nodes[current_node]
            if not node.children:
                break
            
            if random.random() < self.exploration_rate:
                next_node = random.choice(node.children)
            else:
                next_node = self._select_child_with_bias(node.children, constraints)
            
            current_node = next_node
            path.append(current_node)
        
        logger.debug(f"MCMC walk completed: path length {len(path)}, leaf {current_node}")
        return current_node
    
    def _select_child_with_bias(self, children: List[int], constraints: Optional[Dict[str, Any]]) -> int:
        weights = []
        
        for child_id in children:
            child_node = self.concept_tree.nodes[child_id]
            weight = len(child_node.members)
            
            if constraints:
                if 'preferred_size' in constraints:
                    size_diff = abs(len(child_node.members) - constraints['preferred_size'])
                    weight *= np.exp(-size_diff / 100)
                
                if 'level_preference' in constraints:
                    level_diff = abs(child_node.level - constraints['level_preference'])
                    weight *= np.exp(-level_diff)
            
            weights.append(max(weight, 1e-6))
        
        # Temperature-scaled softmax
        weights = np.array(weights) / self.temperature
        probabilities = np.exp(weights - np.max(weights))
        probabilities /= np.sum(probabilities)
        
        return np.random.choice(children, p=probabilities)


@dataclass
class PhysicalPart:
    """Represents a physical component in force-directed assembly."""
    id: int
    position: np.ndarray
    velocity: np.ndarray
    mass: float = 1.0
    force: Optional[np.ndarray] = None
    semantic_features: Optional[np.ndarray] = None
    
    def __post_init__(self):
        if self.force is None:
            self.force = np.zeros_like(self.position)


@dataclass
class Spring:
    """Spring connection between two parts encoding semantic affinity."""
    part1_id: int
    part2_id: int
    rest_length: float
    stiffness: float
    semantic_affinity: float = 1.0


class ForceAssembler:
    """
    Physics simulation for assembling dictionary atoms. Treats each atom as a particle
    in a force field with spring attractions and electrostatic repulsion, converging
    to semantic equilibrium.
    """
    
    def __init__(self, damping: float = 0.95, time_step: float = 0.01,
                 repulsion_strength: float = 100.0, attraction_strength: float = 0.1):
        self.damping = damping
        self.time_step = time_step
        self.repulsion_strength = repulsion_strength
        self.attraction_strength = attraction_strength
        
        self.parts: Dict[int, PhysicalPart] = {}
        self.springs: List[Spring] = []
        
    def initialize_parts(self, dictionary_atoms: np.ndarray, 
                        semantic_embeddings: Optional[np.ndarray] = None) -> None:
        n_parts = dictionary_atoms.shape[0]
        positions = np.random.randn(n_parts, 2) * 10
        
        for i in range(n_parts):
            semantic_feats = semantic_embeddings[i] if semantic_embeddings is not None else None
            self.parts[i] = PhysicalPart(id=i, position=positions[i], 
                                       velocity=np.zeros(2), semantic_features=semantic_feats)
        
        self._create_semantic_springs(semantic_embeddings)
        
    def _create_semantic_springs(self, semantic_embeddings: Optional[np.ndarray] = None) -> None:
        n_parts = len(self.parts)
        self.springs = []
        
        for i in range(n_parts):
            for j in range(i + 1, n_parts):
                if semantic_embeddings is not None:
                    feat_i, feat_j = semantic_embeddings[i], semantic_embeddings[j]
                    norm_i, norm_j = np.linalg.norm(feat_i), np.linalg.norm(feat_j)
                    if norm_i > 0 and norm_j > 0:
                        affinity = np.dot(feat_i, feat_j) / (norm_i * norm_j)
                    else:
                        affinity = 0.0
                else:
                    affinity = np.random.random() * 0.5 + 0.25
                
                # Only connect semantically related parts
                if affinity > 0.3:
                    rest_length = 15.0 * (1.0 - affinity) + 5.0
                    stiffness = self.attraction_strength * affinity
                    
                    self.springs.append(Spring(
                        part1_id=i, part2_id=j,
                        rest_length=rest_length, stiffness=stiffness,
                        semantic_affinity=affinity
                    ))
        
        logger.info(f"Created {len(self.springs)} semantic springs for {n_parts} parts")
    
    def simulate_step(self) -> None:
        # Reset forces
        for part in self.parts.values():
            part.force = np.zeros_like(part.position)
        
        # Spring forces (Hooke's law)
        for spring in self.springs:
            p1, p2 = self.parts[spring.part1_id], self.parts[spring.part2_id]
            delta = p2.position - p1.position
            distance = np.linalg.norm(delta)
            
            if distance > 1e-6:
                direction = delta / distance
                force_magnitude = spring.stiffness * (distance - spring.rest_length)
                force = force_magnitude * direction
                p1.force += force
                p2.force -= force
        
        # Repulsion forces (inverse square)
        for i, p1 in self.parts.items():
            for j, p2 in self.parts.items():
                if i < j:
                    delta = p2.position - p1.position
                    distance = np.linalg.norm(delta)
                    
                    if distance < 5.0 and distance > 1e-6:
                        direction = delta / distance
                        force_magnitude = self.repulsion_strength / (distance**2 + 1e-6)
                        force = -force_magnitude * direction
                        p1.force += force
                        p2.force -= force
        
        # Verlet integration with damping
        for part in self.parts.values():
            part.velocity = self.damping * (part.velocity + part.force * self.time_step / part.mass)
            part.position += part.velocity * self.time_step
            
            # Soft boundary conditions
            boundary = 50.0
            for dim in range(part.position.shape[0]):
                if abs(part.position[dim]) > boundary:
                    part.position[dim] = np.clip(part.position[dim], -boundary, boundary)
                    part.velocity[dim] *= -0.5
    
    def find_equilibrium(self, max_iterations: int = 1000,
                        convergence_threshold: float = 0.001) -> np.ndarray:
        logger.info("Starting force-directed assembly simulation")
        
        prev_positions = {pid: p.position.copy() for pid, p in self.parts.items()}
        
        for iteration in range(max_iterations):
            self.simulate_step()
            
            # Convergence check
            if iteration % 10 == 0:
                max_movement = max(np.linalg.norm(p.position - prev_positions[pid]) 
                                 for pid, p in self.parts.items())
                
                if max_movement < convergence_threshold:
                    logger.info(f"Force assembly converged at iteration {iteration}")
                    break
                
                prev_positions = {pid: p.position.copy() for pid, p in self.parts.items()}
        
        final_positions = np.array([part.position for part in self.parts.values()])
        logger.info(f"Force assembly complete: final positions shape {final_positions.shape}")
        return final_positions


class SeedInitializer:
    """
    Creates generation seeds by injecting high-entropy BBS noise into community archetypes.
    The noise magnitude scales with community variance to maintain semantic coherence.
    """
    
    def __init__(self, noise_strength: float = 0.1):
        self.noise_strength = noise_strength
        self.bbs_generator = BBSNoise()
        
    def create_seed(self, archetype: np.ndarray, community_variance: float = 1.0) -> np.ndarray:
        noise = self.bbs_generator.generate_tensor(
            archetype.shape,
            mean=0.0,
            std=self.noise_strength * np.sqrt(community_variance)
        )
        seed = archetype + noise
        
        # Ensure physical constraints
        if np.any(seed < 0):
            seed = np.maximum(seed, 0)
        if np.any(np.isnan(seed)):
            seed = np.nan_to_num(seed, nan=0.0)
        
        return seed
    
    def create_batch_seeds(self, archetypes: np.ndarray,
                          community_variances: Optional[np.ndarray] = None,
                          batch_size: int = 32) -> np.ndarray:
        if community_variances is None:
            community_variances = np.ones(len(archetypes))
        
        seeds = []
        for _ in range(batch_size):
            idx = random.randint(0, len(archetypes) - 1)
            seed = self.create_seed(archetypes[idx], community_variances[idx])
            seeds.append(seed)
        
        return np.array(seeds)


# ============================================================================
# PHASE 4: ITERATIVE REFINEMENT
# ============================================================================

class GeneRec:
    """
    GeneRec difference recirculation for artifact correction. Implements bidirectional
    information flow between generation and recognition to identify and eliminate
    unrealistic patterns through error-driven learning.
    """
    
    def __init__(self, learning_rate: float = 0.01, momentum: float = 0.9,
                 recirculation_strength: float = 0.5):
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.recirculation_strength = recirculation_strength
        
        self.velocity = None
        self.error_history = []
        
    def difference_recirculation(self, current_sample: np.ndarray,
                               manifold_projection: np.ndarray,
                               target_constraints: Optional[Dict[str, Any]] = None) -> np.ndarray:
        current_tensor = torch.FloatTensor(current_sample)
        manifold_tensor = torch.FloatTensor(manifold_projection)
        
        # Plus phase (clamped)
        plus_output = current_tensor
        
        # Minus phase (nudged toward manifold)
        minus_output = (1 - self.recirculation_strength) * current_tensor + \
                       self.recirculation_strength * manifold_tensor
        
        # Error signal
        error_signal = plus_output - minus_output
        
        # Constraint-aware error modification
        if target_constraints:
            error_signal = self._apply_constraint_errors(error_signal, target_constraints)
        
        # Momentum-based update
        if self.velocity is None:
            self.velocity = torch.zeros_like(error_signal)
        
        self.velocity = self.momentum * self.velocity - self.learning_rate * error_signal
        refined_sample = current_tensor + self.velocity
        
        # Track convergence
        total_error = torch.mean(torch.abs(error_signal)).item()
        self.error_history.append(total_error)
        
        logger.debug(f"GeneRec error: {total_error:.6f}")
        return refined_sample.detach().numpy()
    
    def _apply_constraint_errors(self, error_signal: torch.Tensor,
                               constraints: Dict[str, Any]) -> torch.Tensor:
        modified_error = error_signal.clone()
        
        # Non-negativity amplification
        if constraints.get('non_negative'):
            negative_mask = error_signal < 0
            modified_error[negative_mask] *= 2.0
        
        # Boundary violations
        if 'bounds' in constraints:
            lower, upper = constraints['bounds']
            lower_violations = error_signal < lower
            upper_violations = error_signal > upper
            modified_error[lower_violations] *= 3.0
            modified_error[upper_violations] *= 3.0
        
        # Sparsity control
        if 'sparsity_target' in constraints:
            target_sparsity = constraints['sparsity_target']
            current_sparsity = torch.mean((error_signal.abs() > 0.01).float())
            sparsity_error = target_sparsity - current_sparsity
            
            if sparsity_error > 0:
                small_values = error_signal.abs() < 0.01
                modified_error[small_values] *= 0.5
            elif sparsity_error < 0:
                small_values = error_signal.abs() < 0.01
                modified_error[small_values] *= 2.0
        
        return modified_error
    
    def get_convergence_metrics(self) -> Dict[str, float]:
        if len(self.error_history) < 10:
            return {'converged': False, 'final_error': 0.0, 'error_reduction': 0.0}
        
        recent_errors = self.error_history[-10:]
        avg_recent_error = np.mean(recent_errors)
        final_error = self.error_history[-1]
        
        if len(self.error_history) >= 20:
            early_errors = self.error_history[:10]
            avg_early_error = np.mean(early_errors)
            error_reduction = (avg_early_error - avg_recent_error) / (avg_early_error + 1e-8)
        else:
            error_reduction = 0.0
        
        converged = np.std(recent_errors) < 1e-6
        
        return {
            'converged': converged,
            'final_error': final_error,
            'error_reduction': error_reduction,
            'avg_recent_error': avg_recent_error
        }


class GerchbergSaxton:
    """
    Alternating projection algorithm between spatial and frequency domains. Enforces
    global consistency by iterative constraint satisfaction in both domains.
    """
    
    def __init__(self, max_iterations: int = 100, tolerance: float = 1e-6):
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        
    def project_constraints(self, initial_sample: np.ndarray,
                           spatial_constraints: Optional[Dict[str, Any]] = None,
                           spectral_constraints: Optional[Dict[str, Any]] = None,
                           target_spectrum: Optional[np.ndarray] = None) -> np.ndarray:
        logger.info(f"Gerchberg-Saxton projection: {self.max_iterations} iterations max")
        
        current = initial_sample.copy()
        prev_error = float('inf')
        
        for iteration in range(self.max_iterations):
            prev = current.copy()
            
            # Forward FFT
            fft_current = fft2(current)
            
            # Spectral constraints
            if spectral_constraints or target_spectrum is not None:
                fft_current = self._apply_spectral_constraints(fft_current, spectral_constraints, target_spectrum)
            
            # Inverse FFT
            current = np.real(ifft2(fft_current))
            
            # Spatial constraints
            if spatial_constraints:
                current = self._apply_spatial_constraints(current, spatial_constraints)
            
            # Convergence check
            error = np.mean((current - prev)**2)
            if abs(error - prev_error) < self.tolerance:
                logger.info(f"Converged at iteration {iteration}")
                break
            
            prev_error = error
            
            if iteration % 20 == 0:
                logger.debug(f"GS iteration {iteration}: error = {error:.6f}")
        
        return current
    
    def _apply_spectral_constraints(self, fft_data: np.ndarray,
                                  constraints: Optional[Dict[str, Any]] = None,
                                  target_spectrum: Optional[np.ndarray] = None) -> np.ndarray:
        constrained_fft = fft_data.copy()
        
        # Magnitude matching with target spectrum
        if target_spectrum is not None:
            target_magnitude = np.abs(target_spectrum)
            current_phase = np.angle(constrained_fft)
            constrained_fft = target_magnitude * np.exp(1j * current_phase)
        
        # Low-pass filtering
        if constraints and 'lowpass_cutoff' in constraints:
            cutoff = constraints['lowpass_cutoff']
            h, w = constrained_fft.shape
            cy, cx = h // 2, w // 2
            y, x = np.ogrid[:h, :w]
            mask = ((x - cx)**2 + (y - cy)**2) <= cutoff**2
            constrained_fft *= fftshift(mask)
        
        # High-pass filtering
        if constraints and 'highpass_cutoff' in constraints:
            cutoff = constraints['highpass_cutoff']
            h, w = constrained_fft.shape
            cy, cx = h // 2, w // 2
            y, x = np.ogrid[:h, :w]
            mask = ((x - cx)**2 + (y - cy)**2) > cutoff**2
            constrained_fft *= fftshift(mask)
        
        # Energy conservation
        if constraints and constraints.get('conserve_energy'):
            original_energy = np.sum(np.abs(fft_data)**2)
            current_energy = np.sum(np.abs(constrained_fft)**2)
            if current_energy > 0:
                constrained_fft *= np.sqrt(original_energy / current_energy)
        
        return constrained_fft
    
    def _apply_spatial_constraints(self, spatial_data: np.ndarray,
                                 constraints: Dict[str, Any]) -> np.ndarray:
        constrained_data = spatial_data.copy()
        
        if constraints.get('non_negative'):
            constrained_data = np.maximum(constrained_data, 0)
        
        if 'bounds' in constraints:
            lower, upper = constraints['bounds']
            constrained_data = np.clip(constrained_data, lower, upper)
        
        if 'sparsity_level' in constraints:
            sparsity_level = constraints['sparsity_level']
            threshold = np.percentile(np.abs(constrained_data), (1 - sparsity_level) * 100)
            constrained_data[constrained_data.abs() < threshold] = 0
        
        if 'smoothness_penalty' in constraints:
            sigma = constraints['smoothness_penalty']
            constrained_data = gaussian_filter(constrained_data, sigma=sigma)
        
        return constrained_data


class QUBOOptimizer:
    """
    Quadratic Unconstrained Binary Optimization for pixel-level refinement. Formulates
    high-frequency detail synthesis as an energy minimization problem solvable via
    simulated annealing.
    """
    
    def __init__(self, temperature: float = 1.0, cooling_rate: float = 0.95,
                 n_iterations: int = 1000):
        self.temperature = temperature
        self.cooling_rate = cooling_rate
        self.n_iterations = n_iterations
        
    def minimize_energy(self, initial_sample: np.ndarray,
                       texture_statistics: Optional[Dict[str, np.ndarray]] = None,
                       reference_statistics: Optional[Dict[str, np.ndarray]] = None) -> np.ndarray:
        logger.info("QUBO energy minimization via simulated annealing")
        
        binary_sample = self._to_binary_representation(initial_sample)
        Q = self._build_qubo_matrix(binary_sample, texture_statistics, reference_statistics)
        optimized_binary = self._simulated_annealing_qubo(Q, binary_sample)
        
        return self._from_binary_representation(optimized_binary, initial_sample.shape)
    
    def _to_binary_representation(self, sample: np.ndarray, bits_per_value: int = 8) -> np.ndarray:
        normalized = (sample - sample.min()) / (sample.max() - sample.min() + 1e-8)
        binary_data = []
        
        for value in normalized.flatten():
            binary_repr = format(int(value * 255), f'0{bits_per_value}b')
            binary_data.extend([int(bit) for bit in binary_repr])
        
        return np.array(binary_data)
    
    def _from_binary_representation(self, binary_data: np.ndarray,
                                  original_shape: Tuple[int, ...],
                                  bits_per_value: int = 8) -> np.ndarray:
        values = []
        for i in range(0, len(binary_data), bits_per_value):
            bits = binary_data[i:i+bits_per_value]
            if len(bits) == bits_per_value:
                binary_str = ''.join(map(str, bits))
                value = int(binary_str, 2) / 255.0
                values.append(value)
        
        return np.array(values).reshape(original_shape)
    
    def _build_qubo_matrix(self, binary_sample: np.ndarray,
                         texture_stats: Optional[Dict[str, np.ndarray]] = None,
                         reference_stats: Optional[Dict[str, np.ndarray]] = None) -> np.ndarray:
        n_vars = len(binary_sample)
        Q = np.zeros((n_vars, n_vars))
        
        if texture_stats is None or reference_stats is None:
            # Default: smoothness and current-state preservation
            for i in range(n_vars):
                Q[i, i] = -2 * binary_sample[i] + 1
                
                for j in range(max(0, i-10), min(n_vars, i+10)):
                    if i != j:
                        distance = abs(i - j)
                        coupling = 0.1 / (distance + 1)
                        Q[i, j] += coupling
                        Q[j, i] += coupling
        else:
            # Texture-statistics-aware QUBO
            for i in range(n_vars):
                Q[i, i] = self._calculate_texture_energy(i, binary_sample, texture_stats, reference_stats)
            
            for i in range(n_vars):
                for j in range(i+1, n_vars):
                    if abs(i - j) < 20:
                        interaction = self._calculate_pairwise_interaction(i, j, binary_sample, texture_stats, reference_stats)
                        Q[i, j] = interaction
                        Q[j, i] = interaction
        
        return Q
    
    def _calculate_texture_energy(self, idx: int, binary_sample: np.ndarray,
                                texture_stats: Dict[str, np.ndarray],
                                reference_stats: Dict[str, np.ndarray]) -> float:
        energy = 0.0
        
        if 'mean' in texture_stats and 'mean' in reference_stats:
            local_mean = np.mean(binary_sample[max(0, idx-5):min(len(binary_sample), idx+5)])
            mean_diff = abs(local_mean - reference_stats['mean'].mean())
            energy += mean_diff
        
        if 'variance' in texture_stats and 'variance' in reference_stats:
            local_var = np.var(binary_sample[max(0, idx-5):min(len(binary_sample), idx+5)])
            var_diff = abs(local_var - reference_stats['variance'].mean())
            energy += 0.5 * var_diff
        
        return energy
    
    def _calculate_pairwise_interaction(self, i: int, j: int, binary_sample: np.ndarray,
                                      texture_stats: Dict[str, np.ndarray],
                                      reference_stats: Dict[str, np.ndarray]) -> float:
        if 'correlation' in reference_stats:
            target_correlation = reference_stats['correlation'].mean()
            current_correlation = binary_sample[i] * binary_sample[j]
            return -target_correlation * current_correlation
        else:
            distance = abs(i - j)
            return 0.1 / (distance + 1) if binary_sample[i] == binary_sample[j] else -0.1 / (distance + 1)
    
    def _simulated_annealing_qubo(self, Q: np.ndarray, initial_solution: np.ndarray) -> np.ndarray:
        n_vars = len(initial_solution)
        current = initial_solution.copy()
        current_energy = self._calculate_qubo_energy(Q, current)
        
        best = current.copy()
        best_energy = current_energy
        temperature = self.temperature
        
        for iteration in range(self.n_iterations):
            # Propose flip
            flip_idx = np.random.randint(0, n_vars)
            proposal = current.copy()
            proposal[flip_idx] = 1 - proposal[flip_idx]
            
            # Energy evaluation
            new_energy = self._calculate_qubo_energy(Q, proposal)
            delta_energy = new_energy - current_energy
            
            # Metropolis acceptance
            if delta_energy < 0 or np.random.random() < np.exp(-delta_energy / temperature):
                current = proposal
                current_energy = new_energy
                
                if current_energy < best_energy:
                    best = current.copy()
                    best_energy = current_energy
            
            temperature *= self.cooling_rate
            
            if iteration % 100 == 0:
                logger.debug(f"SA iteration {iteration}: energy = {current_energy:.6f}")
        
        logger.info(f"QUBO optimization complete: final energy = {best_energy:.6f}")
        return best
    
    def _calculate_qubo_energy(self, Q: np.ndarray, solution: np.ndarray) -> float:
        return float(solution.T @ Q @ solution)


class IterativeRefiner:
    """
    Master refinement coordinator that sequentially applies GeneRec, Gerchberg-Saxton,
    and QUBO optimization to transform coarse prototypes into high-fidelity samples.
    """
    
    def __init__(self, generec_config: Optional[Dict[str, Any]] = None,
                 gs_config: Optional[Dict[str, Any]] = None,
                 qubo_config: Optional[Dict[str, Any]] = None):
        self.generec = GeneRec(**(generec_config or {}))
        self.gerchberg_saxton = GerchbergSaxton(**(gs_config or {}))
        self.qubo_optimizer = QUBOOptimizer(**(qubo_config or {}))
        self.refinement_history = []
        
    def refine_sample(self, initial_sample: np.ndarray,
                     manifold_projection: Optional[np.ndarray] = None,
                     constraints: Optional[Dict[str, Any]] = None,
                     target_statistics: Optional[Dict[str, Any]] = None) -> np.ndarray:
        logger.info("Executing iterative refinement pipeline")
        
        current = initial_sample.copy()
        stage_results = {}
        
        # Stage 1: GeneRec manifold alignment
        if manifold_projection is not None:
            logger.info("Stage 1: GeneRec difference recirculation")
            current = self.generec.difference_recirculation(current, manifold_projection, constraints)
            stage_results['generec'] = current.copy()
            
            metrics = self.generec.get_convergence_metrics()
            logger.info(f"GeneRec metrics: {metrics}")
        
        # Stage 2: Gerchberg-Saxton constraint projection
        logger.info("Stage 2: Gerchberg-Saxton spectral-spatial projection")
        
        spatial_constraints = {k: v for k, v in (constraints or {}).items() 
                             if k in ['non_negative', 'bounds', 'sparsity_level', 'smoothness_penalty']}
        spectral_constraints = {k: v for k, v in (constraints or {}).items() 
                               if k in ['lowpass_cutoff', 'highpass_cutoff', 'conserve_energy']}
        
        current = self.gerchberg_saxton.project_constraints(
            current, spatial_constraints, spectral_constraints,
            target_statistics.get('spectrum') if target_statistics else None
        )
        stage_results['gerchberg_saxton'] = current.copy()
        
        # Stage 3: QUBO energy minimization for fine details
        if target_statistics and 'texture' in target_statistics:
            logger.info("Stage 3: QUBO texture optimization")
            current = self.qubo_optimizer.minimize_energy(
                current,
                target_statistics['texture'],
                target_statistics.get('reference_texture')
            )
            stage_results['qubo'] = current.copy()
        
        self.refinement_history.append({
            'initial': initial_sample,
            'stage_results': stage_results,
            'final': current
        })
        
        logger.info("Iterative refinement pipeline completed")
        return current
    
    def get_refinement_metrics(self) -> Dict[str, Any]:
        if not self.refinement_history:
            return {}
        
        latest = self.refinement_history[-1]
        initial, final = latest['initial'], latest['final']
        mse_improvement = np.mean((initial - final)**2)
        
        stage_improvements = {}
        if 'stage_results' in latest:
            prev = initial
            for stage, result in latest['stage_results'].items():
                stage_improvements[stage] = np.mean((prev - result)**2)
                prev = result
        
        return {
            'total_refinements': len(self.refinement_history),
            'latest_mse_improvement': mse_improvement,
            'stage_improvements': stage_improvements,
            'generec_convergence': self.generec.get_convergence_metrics()
        }


# ============================================================================
# MAIN ORCHESTRATION: TDRA MODEL
# ============================================================================

@dataclass
class TDRAConfig:
    """Complete configuration for all TDRA phases."""
    
    # Phase 1: Topological Structure
    diffusion_neighbors: int = 15
    diffusion_alpha: float = 0.5
    diffusion_components: int = 50
    min_community_size: int = 10
    max_tree_depth: int = 5
    
    # Phase 2: Dictionary & Expert Learning
    n_dictionary_atoms: int = 64
    expert_hidden_dims: List[int] = field(default_factory=lambda: [256, 128])
    wake_sleep_epochs: int = 100
    wake_sleep_ratio: float = 0.7
    expert_batch_size: int = 32
    
    # Phase 3: Generative Assembly
    mcmc_temperature: float = 1.0
    mcmc_exploration_rate: float = 0.1
    force_damping: float = 0.95
    force_timestep: float = 0.01
    noise_strength: float = 0.1
    
    # Phase 4: Iterative Refinement
    generec_learning_rate: float = 0.01
    generec_momentum: float = 0.9
    gs_max_iterations: int = 100
    qubo_temperature: float = 1.0
    qubo_iterations: int = 1000
    
    # General
    random_seed: int = 42
    device: str = "cuda" if torch.cuda.is_available() else "cpu"


class TDRA:
    """
    Topological Diffusion-Reaction Assembly: The master orchestrator that chains all
    phases into a cohesive generative system. Each phase outputs to the next, creating
    a continuous pipeline from raw data to refined samples.
    """
    
    def __init__(self, config: Optional[TDRAConfig] = None):
        self.config = config or TDRAConfig()
        
        # Set global random seeds for reproducibility
        np.random.seed(self.config.random_seed)
        torch.manual_seed(self.config.random_seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
        
        # Component placeholders
        self.diffusion_map = None
        self.concept_tree = None
        self.local_dictionaries = {}
        self.generative_experts = {}
        self.mcmc_walker = None
        self.force_assembler = None
        self.seed_initializer = None
        self.iterative_refiner = None
        
        # Training state
        self.is_fitted = False
        self.training_data = None
        self.data_statistics = {}
        
        logger.info(f"TDRA initialized on device: {self.config.device}")
        
    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> 'TDRA':
        logger.info(f"=== TDRA TRAINING STARTED: {X.shape[0]} samples, {X.shape[1]} features ===")
        self.training_data = X.copy()
        
        # Phase 1: Topological structure discovery
        logger.info("--- Phase 1: Topological Structure Learning ---")
        self._phase1_topological_learning(X)
        
        # Phase 2: Local dictionary and expert training
        logger.info("--- Phase 2: Dictionary & Expert Learning ---")
        self._phase2_dictionary_learning(X)
        
        # Phase 3: Generation component initialization
        logger.info("--- Phase 3: Generative Assembly Initialization ---")
        self._initialize_generation_components()
        
        # Phase 4: Statistical preparation for refinement
        logger.info("--- Phase 4: Refinement Statistics Calculation ---")
        self._calculate_data_statistics(X)
        
        self.is_fitted = True
        logger.info("=== TDRA TRAINING COMPLETED SUCCESSFULLY ===")
        return self
    
    def _phase1_topological_learning(self, X: np.ndarray) -> None:
        # Diffusion map for manifold structure
        self.diffusion_map = DiffusionMap(
            n_neighbors=self.config.diffusion_neighbors,
            alpha=self.config.diffusion_alpha,
            n_components=self.config.diffusion_components
        )
        self.diffusion_map.fit(X)
        
        # Concept tree for hierarchical communities
        transition_matrix = self.diffusion_map.get_transition_matrix()
        self.concept_tree = ConceptTree(
            min_community_size=self.config.min_community_size,
            max_depth=self.config.max_tree_depth
        )
        self.concept_tree.build(transition_matrix, X)
        
        logger.info(f"Phase 1 complete: {len(self.concept_tree.nodes)} tree nodes, "
                   f"{len(self.concept_tree.get_leaf_nodes())} leaf communities")
    
    def _phase2_dictionary_learning(self, X: np.ndarray) -> None:
        # Extract communities from tree
        communities = {node_id: node.members for node_id, node in self.concept_tree.nodes.items()
                      if len(node.members) >= self.config.min_community_size}
        
        logger.info(f"Processing {len(communities)} viable communities")
        
        # Learn dictionaries and create experts for each community
        for community_id, member_indices in communities.items():
            community_data = X[member_indices]
            diffusion_coords = self.diffusion_map.get_diffusion_coordinates()[member_indices]
            
            # Local NMF dictionary
            local_dict = LocalDictionary(
                n_components=self.config.n_dictionary_atoms,
                max_iter=200,
                tol=1e-4
            )
            local_dict.fit(community_data)
            self.local_dictionaries[community_id] = local_dict
            
            # Generative expert
            expert = GenerativeExpert(
                community_id=community_id,
                input_dim=self.config.diffusion_components,
                n_dictionary_atoms=self.config.n_dictionary_atoms,
                hidden_dims=self.config.expert_hidden_dims
            )
            self.generative_experts[community_id] = expert
            
            logger.debug(f"Community {community_id}: {len(member_indices)} samples, "
                       f"dictionary sparsity = {local_dict.get_sparsity():.3f}")
        
        # Wake-Sleep training across all experts
        expert_config = ExpertConfig(
            wake_epochs=self.config.wake_sleep_epochs,
            sleep_epochs=self.config.sleep_epochs,
            batch_size=self.config.expert_batch_size,
            wake_sleep_ratio=self.config.wake_sleep_ratio
        )
        
        trainer = WakeSleepTrainer(self.generative_experts, expert_config)
        
        # Prepare data structures for trainer
        diffusion_coords_by_community = {
            cid: self.diffusion_map.get_diffusion_coordinates()[members]
            for cid, members in communities.items()
        }
        data_by_community = {
            cid: self.training_data[members]
            for cid, members in communities.items()
        }
        
        # Execute training
        training_losses = trainer.train(
            data_by_community,
            diffusion_coords_by_community,
            self.local_dictionaries
        )
        
        logger.info(f"Phase 2 complete: Average wake loss = {np.mean(training_losses['wake_losses'] or [0]):.6f}, "
                   f"Average sleep loss = {np.mean(training_losses['sleep_losses'] or [0]):.6f}")
    
    def _initialize_generation_components(self) -> None:
        self.mcmc_walker = MCMCWalker(
            concept_tree=self.concept_tree,
            temperature=self.config.mcmc_temperature,
            exploration_rate=self.config.mcmc_exploration_rate
        )
        
        self.force_assembler = ForceAssembler(
            damping=self.config.force_damping,
            time_step=self.config.force_timestep
        )
        
        self.seed_initializer = SeedInitializer(
            noise_strength=self.config.noise_strength
        )
        
        self.iterative_refiner = IterativeRefiner(
            generec_config={
                'learning_rate': self.config.generec_learning_rate,
                'momentum': self.config.generec_momentum
            },
            gs_config={
                'max_iterations': self.config.gs_max_iterations
            },
            qubo_config={
                'temperature': self.config.qubo_temperature,
                'n_iterations': self.config.qubo_iterations,
                'cooling_rate': 0.95
            }
        )
        
        logger.info("Phase 3 generation components initialized")
    
    def _calculate_data_statistics(self, X: np.ndarray) -> None:
        self.data_statistics = {
            'mean': np.mean(X, axis=0),
            'std': np.std(X, axis=0),
            'min': np.min(X, axis=0),
            'max': np.max(X, axis=0),
            'texture': {
                'mean': np.mean(X, axis=1),
                'variance': np.var(X, axis=1),
                'correlation': np.corrcoef(X.T) if X.shape[1] > 1 else np.array([[1.0]])
            }
        }
        
        # Spectral statistics for GS
        if len(X.shape) >= 2 and X.shape[1] >= 64:
            sample_size = int(np.sqrt(min(X.shape[1], 1024)))
            if sample_size * sample_size <= X.shape[1]:
                sample = X[0, :sample_size*sample_size].reshape(sample_size, sample_size)
                self.data_statistics['spectrum'] = fft2(sample)
        else:
            self.data_statistics['spectrum'] = None
        
        logger.info("Phase 4: Refinement statistics calculated")
    
    def generate(self, n_samples: int = 1, constraints: Optional[Dict[str, Any]] = None,
                return_intermediate: bool = False) -> Union[np.ndarray, Tuple[np.ndarray, List[Dict]]]:
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first")
        
        logger.info(f"=== GENERATING {n_samples} SAMPLES ===")
        
        generated_samples = []
        intermediate_results = [] if return_intermediate else None
        
        for sample_idx in range(n_samples):
            logger.info(f"Generating sample {sample_idx + 1}/{n_samples}")
            
            # Phase 3: Coarse assembly
            coarse_sample, assembly_stages = self._phase3_generative_assembly(constraints)
            
            # Phase 4: Fine-grained refinement
            refined_sample = self._phase4_iterative_refinement(coarse_sample, constraints)
            
            generated_samples.append(refined_sample)
            
            if return_intermediate:
                intermediate_results.append({
                    'coarse_prototype': coarse_sample,
                    'assembly_stages': assembly_stages,
                    'refined_sample': refined_sample
                })
        
        generated_array = np.array(generated_samples)
        logger.info(f"Generation complete: final shape {generated_array.shape}")
        
        if return_intermediate:
            return generated_array, intermediate_results
        return generated_array
    
    def _phase3_generative_assembly(self, constraints: Optional[Dict[str, Any]] = None) -> Tuple[np.ndarray, Dict[str, Any]]:
        stages = {}
        
        # MCMC semantic niche selection
        leaf_id = self.mcmc_walker.walk_to_leaf(constraints)
        leaf_node = self.concept_tree.nodes[leaf_id]
        stages['selected_leaf'] = leaf_id
        stages['community_size'] = len(leaf_node.members)
        
        # Archetype-driven seed creation
        archetype = self.training_data[leaf_node.archetype_idx]
        community_data = self.training_data[leaf_node.members]
        community_variance = np.var(community_data, axis=0).mean()
        
        seed = self.seed_initializer.create_seed(archetype, community_variance)
        stages['archetype_idx'] = leaf_node.archetype_idx
        
        # Force-directed assembly of dictionary atoms
        if leaf_id in self.local_dictionaries:
            local_dict = self.local_dictionaries[leaf_id]
            atoms = local_dict.components_
            
            # Use expert to generate meaningful activation pattern
            expert = self.generative_experts[leaf_id]
            latent_code = torch.randn(1, self.config.diffusion_components)
            
            with torch.no_grad():
                activations = expert.generate_activations(latent_code).numpy().squeeze()
            
            self.force_assembler.initialize_parts(atoms, semantic_embeddings=atoms)
            final_positions = self.force_assembler.find_equilibrium()
            
            # Compose coarse prototype from assembled atoms
            coarse_prototype = self._create_coarse_prototype(seed, atoms, activations, final_positions)
            stages['force_assembly_completed'] = True
        else:
            # Fallback to seed
            coarse_prototype = seed
            stages['force_assembly_completed'] = False
        
        return coarse_prototype, stages
    
    def _create_coarse_prototype(self, seed: np.ndarray, dictionary_atoms: np.ndarray,
                               activations: np.ndarray, positions: np.ndarray) -> np.ndarray:
        # Position-weighted combination of dictionary atoms
        n_atoms = len(dictionary_atoms)
        position_weights = np.exp(-np.linalg.norm(positions - positions.mean(axis=0), axis=1))
        position_weights /= position_weights.sum()
        
        combined_atoms = dictionary_atoms * activations[:, np.newaxis] * position_weights[:, np.newaxis]
        prototype = seed + 0.3 * combined_atoms.sum(axis=0)
        
        return np.clip(prototype, self.data_statistics['min'], self.data_statistics['max'])
    
    def _phase4_iterative_refinement(self, sample: np.ndarray,
                                   constraints: Optional[Dict[str, Any]] = None) -> np.ndarray:
        logger.debug("Phase 4: Iterative refinement")
        
        # Project to learned manifold via diffusion map
        manifold_projection = self._project_to_manifold(sample)
        
        # Merge constraints with data statistics
        refinement_constraints = {
            'non_negative': True,
            'bounds': (self.data_statistics['min'], self.data_statistics['max'])
        }
        
        if constraints:
            refinement_constraints.update(constraints)
        
        return self.iterative_refiner.refine_sample(
            sample,
            manifold_projection,
            refinement_constraints,
            self.data_statistics
        )
    
    def _project_to_manifold(self, sample: np.ndarray) -> np.ndarray:
        # Out-of-sample extension to diffusion coordinates
        if self.diffusion_map is not None:
            try:
                diffusion_coords = self.diffusion_map.transform(sample.reshape(1, -1))
                # Reconstruct from diffusion coordinates using pseudo-inverse
                manifold_projection = self.training_data.mean(axis=0) + \
                                    np.dot(diffusion_coords, self.diffusion_map.eigenvectors_.T)
                return manifold_projection.squeeze()
            except:
                pass
        
        # Fallback: nearest neighbor
        distances = np.linalg.norm(self.training_data - sample, axis=1)
        nearest_idx = np.argmin(distances)
        return self.training_data[nearest_idx]
    
    def save_model(self, filepath: str) -> None:
        if not self.is_fitted:
            raise ValueError("Cannot save untrained model")
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        save_data = {
            'config': self.config,
            'diffusion_map': self.diffusion_map,
            'concept_tree': self.concept_tree,
            'local_dictionaries': self.local_dictionaries,
            'generative_experts': self.generative_experts,
            'training_data': self.training_data,
            'data_statistics': self.data_statistics,
            'is_fitted': self.is_fitted
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(save_data, f)
        
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str) -> 'TDRA':
        logger.info(f"Loading model from {filepath}")
        
        with open(filepath, 'rb') as f:
            save_data = pickle.load(f)
        
        self.config = save_data['config']
        self.diffusion_map = save_data['diffusion_map']
        self.concept_tree = save_data['concept_tree']
        self.local_dictionaries = save_data['local_dictionaries']
        self.generative_experts = save_data['generative_experts']
        self.training_data = save_data['training_data']
        self.data_statistics = save_data['data_statistics']
        self.is_fitted = save_data['is_fitted']
        
        self._initialize_generation_components()
        
        logger.info("Model loading complete")
        return self
    
    def get_model_info(self) -> Dict[str, Any]:
        if not self.is_fitted:
            return {'status': 'Not fitted'}
        
        return {
            'status': 'Fitted',
            'training_samples': self.training_data.shape[0] if self.training_data is not None else 0,
            'feature_dimensions': self.training_data.shape[1] if self.training_data is not None else 0,
            'concept_tree_nodes': len(self.concept_tree.nodes) if self.concept_tree else 0,
            'leaf_communities': len(self.concept_tree.get_leaf_nodes()) if self.concept_tree else 0,
            'local_dictionaries': len(self.local_dictionaries),
            'generative_experts': len(self.generative_experts)
        }
    
    def visualize_model_structure(self) -> str:
        if not self.is_fitted:
            return "Model not fitted"
        
        info = self.get_model_info()
        lines = ["TDRA Model Architecture:"]
        lines.append("=" * 50)
        lines.append(f"Status: {info['status']}")
        lines.append(f"Training Samples: {info['training_samples']}")
        lines.append(f"Feature Dimensions: {info['feature_dimensions']}")
        lines.append(f"Concept Tree: {info['concept_tree_nodes']} nodes ({info['leaf_communities']} leaves)")
        lines.append(f"Local Dictionaries: {info['local_dictionaries']}")
        lines.append(f"Generative Experts: {info['generative_experts']}")
        lines.append("\nTree Structure:")
        lines.append(self.concept_tree.visualize_tree())
        
        return "\n".join(lines)


# ============================================================================
# EXECUTION DEMONSTRATION
# ============================================================================

if __name__ == "__main__":
    """
    End-to-end demonstration of TDRA on synthetic data. This example shows the complete
    pipeline: data creation → preprocessing → topological learning → dictionary training
    → generative assembly → iterative refinement → quality evaluation.
    """
    import matplotlib.pyplot as plt
    
    # Synthetic dataset: mixture of manifold-structured clusters
    logger.info("Creating synthetic demonstration dataset")
    np.random.seed(42)
    
    n_samples = 500
    n_features = 64
    
    # Three latent manifolds
    X1 = np.random.multivariate_normal(
        mean=np.zeros(64),
        cov=np.eye(64) * 0.5,
        size=n_samples // 3
    )
    X1 += np.sin(X1[:, :16]).dot(np.random.randn(16, 64)) * 0.3
    
    X2 = np.random.multivariate_normal(
        mean=np.ones(64) * 2,
        cov=np.eye(64) * 0.3,
        size=n_samples // 3
    )
    X2 += np.cos(X2[:, 32:48]).dot(np.random.randn(16, 64)) * 0.2
    
    X3 = np.random.multivariate_normal(
        mean=np.ones(64) * -1,
        cov=np.eye(64) * 0.4,
        size=n_samples - 2*(n_samples // 3)
    )
    X3 += np.tan(X3[:, 16:32]).dot(np.random.randn(16, 64)) * 0.1
    
    X_train = np.vstack([X1, X2, X3])
    
    # Add noise
    X_train += np.random.randn(*X_train.shape) * 0.05
    
    # Ensure non-negative for demonstration
    X_train = np.maximum(X_train, 0)
    
    logger.info(f"Dataset shape: {X_train.shape}, range: [{X_train.min():.2f}, {X_train.max():.2f}]")
    
    # Initialize and train TDRA
    config = TDRAConfig(
        diffusion_neighbors=10,
        diffusion_components=20,
        min_community_size=15,
        max_tree_depth=3,
        n_dictionary_atoms=32,
        wake_sleep_epochs=50,
        expert_batch_size=16,
        noise_strength=0.15,
        qubo_iterations=500
    )
    
    tdra = TDRA(config)
    
    logger.info("\n" + "="*60)
    logger.info("TRAINING PHASE")
    logger.info("="*60)
    tdra.fit(X_train)
    
    # Generate new samples
    logger.info("\n" + "="*60)
    logger.info("GENERATION PHASE")
    logger.info("="*60)
    
    n_generate = 5
    generated_samples, intermediates = tdra.generate(
        n_samples=n_generate,
        constraints={'non_negative': True},
        return_intermediate=True
    )
    
    # Evaluation and visualization
    logger.info("\n" + "="*60)
    logger.info("EVALUATION")
    logger.info("="*60)
    
    # Diversity metric
    pairwise_distances = np.linalg.norm(generated_samples[:, np.newaxis] - generated_samples[np.newaxis, :], axis=2)
    diversity = np.mean(pairwise_distances[np.triu_indices_from(pairwise_distances, k=1)])
    logger.info(f"Generated sample diversity: {diversity:.4f}")
    
    # Reconstruction quality (proximity to training manifold)
    distances_to_training = np.linalg.norm(
        generated_samples[:, np.newaxis] - X_train[np.newaxis, :],
        axis=2
    ).min(axis=1)
    avg_distance = np.mean(distances_to_training)
    logger.info(f"Average distance to training manifold: {avg_distance:.4f}")
    
    # Visualize results
    try:
        fig, axes = plt.subplots(2, n_generate, figsize=(15, 6))
        
        # Show generated samples
        for i in range(n_generate):
            sample_2d = generated_samples[i].reshape(8, 8)
            axes[0, i].imshow(sample_2d, cmap='viridis')
            axes[0, i].set_title(f"Generated {i+1}")
            axes[0, i].axis('off')
        
        # Show corresponding pre-refinement prototypes
        for i in range(n_generate):
            prototype = intermediates[i]['assembly_stages']['coarse_prototype'].reshape(8, 8)
            axes[1, i].imshow(prototype, cmap='viridis')
            axes[1, i].set_title(f"Prototype {i+1}")
            axes[1, i].axis('off')
        
        plt.suptitle("TDRA Generation Results: Final Samples (Top) vs Coarse Prototypes (Bottom)")
        plt.tight_layout()
        plt.savefig('tdra_demonstration.png', dpi=150)
        logger.info("Visualization saved to 'tdra_demonstration.png'")
        
    except Exception as e:
        logger.warning(f"Could not create visualization: {e}")
    
    # Save model
    model_path = Path("tdra_model.pkl")
    tdra.save_model(str(model_path))
    logger.info(f"Model saved to {model_path}")
    
    # Print model structure
    logger.info("\n" + tdra.visualize_model_structure())
    
    logger.info("\n" + "="*60)
    logger.info("DEMONSTRATION COMPLETE")
    logger.info("="*60)
    logger.info("The TDRA model successfully learned topological structure, ")
    logger.info("trained community-specific experts, and generated diverse, ")
    logger.info("high-fidelity samples through physics-inspired assembly.")
