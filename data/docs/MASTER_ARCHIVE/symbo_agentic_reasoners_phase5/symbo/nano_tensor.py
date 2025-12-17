# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
NanoTensor and Symbolic Trainer for SYMBO_AGENTIC_REASONERS
=========================================

Core symbolic tensor operations with:
- Gröbner basis solving for exact polynomial solutions
- Perturbation methods for approximate solutions
- Taylor polynomial generation
- Hybrid symbolic-numeric training

Adapted for SYMBO_AGENTIC_REASONERS Phase 5 integration.
"""

import sympy as sp
import numpy as np
from functools import lru_cache
from typing import Tuple, Dict, Any, List, Optional, Union
import warnings
warnings.filterwarnings('ignore')

# Optional imports with graceful fallback
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False

try:
    from kanren import Relation, facts, run, var as kvar
    KANREN_AVAILABLE = True
except ImportError:
    KANREN_AVAILABLE = False

try:
    from skopt import gp_minimize
    SKOPT_AVAILABLE = True
except ImportError:
    SKOPT_AVAILABLE = False

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend for file export
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# Sympy imports
from sympy import (
    symbols, Symbol, Poly, groebner, resultant, solve, Eq, nsolve, lambdify
)
from sympy.matrices import Matrix


class NanoTensor:
    """
    True nD symbolic tensor with vectorized operations, Gröbner basis solving,
    and full perturbation capabilities. Represents mathematical objects exactly.
    """

    def __init__(self, shape: Tuple[int, ...], max_order: int = 2,
                 base_vars: List[str] = None, name: str = "nt"):
        self.shape = shape
        self.max_order = max_order
        self.name = name
        self.base_vars = [sp.Symbol(v) for v in (base_vars or ['k', 'a', 'eps', 'sig'])]
        self.coeff_vars: List[sp.Symbol] = []
        self.data: np.ndarray = np.empty(shape, dtype=object)
        self._init_data()
        self._symvars_cache = None
        self._lambdify_cache: Dict = {}
        self.fitted_coeffs: Dict[str, float] = {}

    def _init_data(self):
        """Initialize tensor with symbolic zeros"""
        self.data = np.zeros(self.shape, dtype=object)
        self.data.flat[:] = sp.S(0)

    @property
    def symvars(self) -> List[sp.Symbol]:
        """Cache all free symbols in the tensor"""
        if self._symvars_cache is None:
            vars_set = set()
            for elem in self.data.flat:
                if elem != 0 and hasattr(elem, 'free_symbols'):
                    vars_set.update(elem.free_symbols)
            self._symvars_cache = list(vars_set)
        return self._symvars_cache

    @lru_cache(maxsize=128)
    def diff_cached(self, wrt_name: str, order: int = 1) -> 'NanoTensor':
        """Cached differentiation for performance"""
        wrt_candidates = [v for v in self.symvars if v.name == wrt_name]
        if not wrt_candidates:
            wrt_candidates = [v for v in self.base_vars if v.name == wrt_name]
        if not wrt_candidates:
            raise ValueError(f"Variable {wrt_name} not found")
        return self.diff(wrt_candidates[0], order)

    def diff(self, wrt: sp.Symbol, order: int = 1) -> 'NanoTensor':
        """Symbolic differentiation of entire tensor"""
        new_nt = NanoTensor(self.shape, self.max_order, [v.name for v in self.base_vars])
        new_nt.data = np.vectorize(lambda e: sp.diff(e, wrt, order))(self.data)
        return new_nt

    def subs(self, sub_dict: Dict[sp.Symbol, Any]) -> 'NanoTensor':
        """Symbolic substitution across tensor"""
        new_nt = NanoTensor(self.shape, self.max_order, [v.name for v in self.base_vars])
        clean_dict = {k: (sp.nsimplify(v) if isinstance(v, (int, float)) else v)
                     for k, v in sub_dict.items()}
        new_nt.data = np.vectorize(lambda e: e.subs(clean_dict))(self.data)
        return new_nt

    @lru_cache(maxsize=128)
    def subs_cached(self, sub_tuple: Tuple) -> 'NanoTensor':
        """Cached substitution for repeated calls"""
        sub_dict = dict(sub_tuple)
        return self.subs(sub_dict)

    def eval_numeric(self, point: Dict[str, float], use_lambdify: bool = True) -> np.ndarray:
        """Evaluate tensor numerically at a given point with caching."""
        vars_in_point = [v for v in self.symvars if v.name in point]
        key = tuple(sorted([v.name for v in vars_in_point])) + tuple(sorted(point.keys()))
        if key not in self._lambdify_cache:
            self._lambdify_cache[key] = [
                lambdify(vars_in_point, e, modules='numpy') for e in self.data.flat
            ]
        funcs = self._lambdify_cache[key]
        args = [point.get(v.name, 0.0) for v in vars_in_point]
        result_flat = [f(*args) for f in funcs]
        return np.array(result_flat).reshape(self.shape)

    def solve_poly(self, target_eq: sp.Expr, var: sp.Symbol) -> List[float]:
        """Solve polynomial equation exactly and return real roots only."""
        try:
            poly = Poly(sp.simplify(target_eq), var)
            roots = poly.nroots()
            real_roots = []
            for r in roots:
                if abs(r.imag) < 1e-8:
                    real_roots.append(float(r.real))
            return real_roots
        except Exception as e:
            return []

    def groebner_solve(self, poly_system: List[sp.Expr],
                   vars_to_solve: List[sp.Symbol] = None) -> List[Dict[str, sp.Expr]]:
        """Solve polynomial system with Groebner basis, filter for real solutions."""
        if vars_to_solve is None:
            vars_to_solve = self.symvars[:len(poly_system)]
        try:
            G = groebner(poly_system, *vars_to_solve, order='lex')
            solutions = solve(poly_system, *vars_to_solve, dict=True)
            real_solutions = []
            for sol in solutions:
                if all(abs(v.as_real_imag()[1]) < 1e-8 for v in sol.values()):
                    real_solutions.append({str(k): v for k, v in sol.items()})
            return real_solutions
        except Exception as e:
            return []

    def resultant(self, f: sp.Expr, g: sp.Expr, var: sp.Symbol) -> sp.Expr:
        """Compute resultant of two polynomials with respect to variable"""
        return resultant(f, g, var)

    def parametrize_curve(self, implicit_poly: sp.Expr,
                          t: sp.Symbol = None) -> Tuple[sp.Expr, sp.Expr]:
        """Parametrize algebraic curve via line intersection + resultant."""
        if t is None:
            t = sp.Symbol('t')
        x, y = sp.symbols('x y')
        implicit_poly = sp.sympify(implicit_poly)
        l = y - t * x
        res_y = resultant(implicit_poly, l, y)
        x_sols = sp.solve(res_y, x)
        non_trivial = [sol for sol in x_sols if sol != 0]

        if non_trivial:
            x_param = sp.simplify(non_trivial[-1])
            y_param = sp.simplify(t * x_param)
            return x_param, y_param
        else:
            return x, y

    def generate_taylor(self, center: Dict[str, float], ss_value: sp.Expr = None):
        """Generate Taylor polynomial up to max_order, including cross terms."""
        self.coeff_vars.clear()
        if ss_value is None:
            ss_value = sum([v for v in self.base_vars])

        devs = [sp.Symbol(v.name) - center.get(v.name, 0) for v in self.base_vars]
        taylor_expr = ss_value

        self.coeff_vars.clear()

        # Linear terms
        for v, dev in zip(self.base_vars, devs):
            c = sp.Symbol(f'g_{v.name}')
            self.coeff_vars.append(c)
            taylor_expr += c * dev

        # Quadratic and interaction terms
        if self.max_order >= 2:
            for i, v1 in enumerate(self.base_vars):
                c = sp.Symbol(f'g_{v1.name}_{v1.name}')
                self.coeff_vars.append(c)
                taylor_expr += 0.5 * c * devs[i]**2
                for j in range(i+1, len(self.base_vars)):
                    v2 = self.base_vars[j]
                    c_cross = sp.Symbol(f'g_{v1.name}_{v2.name}')
                    self.coeff_vars.append(c_cross)
                    taylor_expr += c_cross * devs[i] * devs[j]

        self.data.flat[:] = sp.simplify(taylor_expr)

    def compute_steady_state(self, model_eqs: List[sp.Expr],
                            params: Dict[str, float],
                            ss_guess: Dict[str, float] = None) -> Dict[str, float]:
        """Compute steady state by solving model equations."""
        if ss_guess is None:
            ss_guess = {str(v): 1.0 for v in self.base_vars}

        subs_params = {sp.Symbol(k): v for k, v in params.items()}
        eqs_ss = [eq.subs(subs_params) for eq in model_eqs]
        vars_ss = [sp.Symbol(k) for k in ss_guess.keys()]

        try:
            sols = solve(eqs_ss, vars_ss, dict=True)
            if sols:
                sol = sols[0]
                return {str(k): float(v.evalf()) for k, v in sol.items()}
        except:
            pass

        # Numeric fallback
        try:
            sol_dict = {}
            for var in vars_ss:
                sol = nsolve(eqs_ss[0], var, ss_guess[str(var)])
                sol_dict[str(var)] = float(sol)
            return sol_dict
        except Exception as e:
            return ss_guess

    def full_perturbation(self, model_R: sp.Expr, params: Dict[str, Any],
                         var_order: List[str] = ['k', 'a', 'eps', 'sig'],
                         eps_var: float = 1.0):
        """Full 2nd-order perturbation solver."""
        ss = self.compute_steady_state([model_R], params)
        self.coeff_vars.clear()
        self.generate_taylor(ss)
        self.fitted_coeffs = {}

        sym_vars = {v.name: v for v in self.base_vars}
        subs_ss = {**{sp.Symbol(k): v for k, v in ss.items()},
                  **{sp.Symbol(k): v for k, v in params.items()}}

        # First-order conditions
        for vname in var_order:
            if vname not in sym_vars:
                continue
            wrt = sym_vars[vname]
            R_v = sp.simplify(sp.diff(model_R, wrt))
            R_v_ss = R_v.subs({**subs_ss, **{sp.Symbol(k): v for k, v in self.fitted_coeffs.items()}})

            coeff_name = f'g_{vname}'
            coeff_sym = sp.Symbol(coeff_name)

            try:
                poly_eq = sp.expand(R_v_ss.subs(coeff_sym, sp.Symbol('_c')))
                poly_eq = poly_eq.subs(sp.Symbol('_c'), coeff_sym)
                roots = self.solve_poly(poly_eq, coeff_sym)
                if roots:
                    stable_root = min([r for r in roots if abs(r) < 10], key=abs, default=roots[0])
                    self.fitted_coeffs[coeff_name] = stable_root
            except Exception:
                pass

        # Second-order conditions
        if self.max_order >= 2:
            for i, v1 in enumerate(var_order):
                if v1 not in sym_vars:
                    continue
                wrt1 = sym_vars[v1]

                R_vv = sp.diff(model_R, wrt1, 2)
                R_vv_ss = R_vv.subs({**subs_ss, **{sp.Symbol(k): v for k, v in self.fitted_coeffs.items()}})
                coeff_name = f'g_{v1}_{v1}'
                coeff_sym = sp.Symbol(coeff_name)

                try:
                    roots = self.solve_poly(R_vv_ss.subs(coeff_sym, sp.Symbol('_c')).subs(sp.Symbol('_c'), coeff_sym), coeff_sym)
                    if roots:
                        self.fitted_coeffs[coeff_name] = roots[0]
                except:
                    self.fitted_coeffs[coeff_name] = 0.0

                # Cross terms
                for j in range(i+1, len(var_order)):
                    v2 = var_order[j]
                    if v2 not in sym_vars:
                        continue
                    wrt2 = sym_vars[v2]

                    R_v1v2 = sp.diff(sp.diff(model_R, wrt1), wrt2)
                    R_v1v2_ss = R_v1v2.subs({**subs_ss, **{sp.Symbol(k): v for k, v in self.fitted_coeffs.items()}})
                    coeff_name = f'g_{v1}_{v2}'
                    coeff_sym = sp.Symbol(coeff_name)

                    try:
                        roots = self.solve_poly(R_v1v2_ss.subs(coeff_sym, sp.Symbol('_c')).subs(sp.Symbol('_c'), coeff_sym), coeff_sym)
                        if roots:
                            self.fitted_coeffs[coeff_name] = roots[0]
                    except:
                        self.fitted_coeffs[coeff_name] = 0.0

        # Apply solution to tensor
        apply_dict = {sp.Symbol(k): v for k, v in self.fitted_coeffs.items()}
        self.data.flat[:] = self.subs(apply_dict).data.flat[0]

    def simplify(self):
        """Simplify all expressions in tensor"""
        self.data = np.vectorize(sp.simplify)(self.data)
        self._symvars_cache = None

    def deriv_tree(self, wrt_vars: List[str]) -> Dict[str, sp.Expr]:
        """Explainability: Show derivative structure"""
        tree = {}
        for var_name in wrt_vars:
            try:
                deriv = self.diff_cached(var_name, 1).data.flat[0]
                tree[var_name] = sp.simplify(deriv)
            except:
                tree[var_name] = sp.Symbol('NA')
        return tree

    def plot_contour(
        self,
        var1: str,
        var2: str,
        fixed_values: Dict[str, float] = None,
        output_path: str = None,
        n_points: int = 50,
        levels: int = 20,
        title: str = None,
        colormap: str = 'viridis'
    ) -> Optional[str]:
        """
        Export contour plot of tensor expression to file.

        Args:
            var1: Name of first variable (x-axis)
            var2: Name of second variable (y-axis)
            fixed_values: Dict of fixed values for other variables
            output_path: Path to save the plot (default: auto-generated)
            n_points: Number of points per axis
            levels: Number of contour levels
            title: Plot title (default: auto-generated)
            colormap: Matplotlib colormap name

        Returns:
            Path to saved file, or None if matplotlib unavailable
        """
        if not MATPLOTLIB_AVAILABLE:
            warnings.warn("matplotlib not available - cannot generate contour plot")
            return None

        fixed_values = fixed_values or {}

        # Find the variables
        var1_sym = None
        var2_sym = None
        for v in self.base_vars + self.symvars:
            if v.name == var1:
                var1_sym = v
            if v.name == var2:
                var2_sym = v

        if var1_sym is None or var2_sym is None:
            raise ValueError(f"Variables {var1} or {var2} not found in tensor")

        # Get the expression (first element for scalar tensor)
        expr = self.data.flat[0]

        # Substitute fixed values
        for k, v in fixed_values.items():
            expr = expr.subs(sp.Symbol(k), v)

        # Create lambdified function
        f = lambdify([var1_sym, var2_sym], expr, modules='numpy')

        # Create grid
        x1_range = np.linspace(-2, 2, n_points)
        x2_range = np.linspace(-2, 2, n_points)
        X1, X2 = np.meshgrid(x1_range, x2_range)

        # Evaluate
        try:
            Z = f(X1, X2)
            if not isinstance(Z, np.ndarray):
                Z = np.full_like(X1, float(Z))
        except Exception as e:
            warnings.warn(f"Could not evaluate expression: {e}")
            return None

        # Create plot
        fig, ax = plt.subplots(figsize=(10, 8))
        contour = ax.contourf(X1, X2, Z, levels=levels, cmap=colormap)
        ax.contour(X1, X2, Z, levels=levels, colors='black', linewidths=0.5, alpha=0.3)
        plt.colorbar(contour, ax=ax, label='Value')
        ax.set_xlabel(var1)
        ax.set_ylabel(var2)
        ax.set_title(title or f'Contour Plot: {self.name}({var1}, {var2})')

        # Generate output path if not provided
        if output_path is None:
            import tempfile
            output_path = tempfile.mktemp(suffix='_contour.png', prefix=f'{self.name}_')

        # Save
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close(fig)

        return output_path

    def plot_surface(
        self,
        var1: str,
        var2: str,
        fixed_values: Dict[str, float] = None,
        output_path: str = None,
        n_points: int = 50,
        title: str = None,
        colormap: str = 'viridis',
        elevation: float = 30,
        azimuth: float = 45
    ) -> Optional[str]:
        """
        Export 3D surface plot of tensor expression to file.

        Args:
            var1: Name of first variable (x-axis)
            var2: Name of second variable (y-axis)
            fixed_values: Dict of fixed values for other variables
            output_path: Path to save the plot (default: auto-generated)
            n_points: Number of points per axis
            title: Plot title (default: auto-generated)
            colormap: Matplotlib colormap name
            elevation: Camera elevation angle
            azimuth: Camera azimuth angle

        Returns:
            Path to saved file, or None if matplotlib unavailable
        """
        if not MATPLOTLIB_AVAILABLE:
            warnings.warn("matplotlib not available - cannot generate surface plot")
            return None

        fixed_values = fixed_values or {}

        # Find the variables
        var1_sym = None
        var2_sym = None
        for v in self.base_vars + self.symvars:
            if v.name == var1:
                var1_sym = v
            if v.name == var2:
                var2_sym = v

        if var1_sym is None or var2_sym is None:
            raise ValueError(f"Variables {var1} or {var2} not found in tensor")

        # Get the expression (first element for scalar tensor)
        expr = self.data.flat[0]

        # Substitute fixed values
        for k, v in fixed_values.items():
            expr = expr.subs(sp.Symbol(k), v)

        # Create lambdified function
        f = lambdify([var1_sym, var2_sym], expr, modules='numpy')

        # Create grid
        x1_range = np.linspace(-2, 2, n_points)
        x2_range = np.linspace(-2, 2, n_points)
        X1, X2 = np.meshgrid(x1_range, x2_range)

        # Evaluate
        try:
            Z = f(X1, X2)
            if not isinstance(Z, np.ndarray):
                Z = np.full_like(X1, float(Z))
        except Exception as e:
            warnings.warn(f"Could not evaluate expression: {e}")
            return None

        # Create 3D plot
        fig = plt.figure(figsize=(12, 9))
        ax = fig.add_subplot(111, projection='3d')

        surf = ax.plot_surface(X1, X2, Z, cmap=colormap, edgecolor='none', alpha=0.9)
        ax.set_xlabel(var1)
        ax.set_ylabel(var2)
        ax.set_zlabel('Value')
        ax.set_title(title or f'Surface Plot: {self.name}({var1}, {var2})')
        ax.view_init(elev=elevation, azim=azimuth)
        fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10, label='Value')

        # Generate output path if not provided
        if output_path is None:
            import tempfile
            output_path = tempfile.mktemp(suffix='_surface.png', prefix=f'{self.name}_')

        # Save
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close(fig)

        return output_path

    def export_expression_latex(self, output_path: str = None) -> str:
        """
        Export tensor expressions to LaTeX file for debugging.

        Args:
            output_path: Path to save LaTeX (default: auto-generated)

        Returns:
            LaTeX string representation
        """
        latex_parts = []
        latex_parts.append(f"% NanoTensor: {self.name}")
        latex_parts.append(f"% Shape: {self.shape}")
        latex_parts.append(f"% Base variables: {[str(v) for v in self.base_vars]}")
        latex_parts.append("")

        for idx, elem in enumerate(self.data.flat):
            latex_expr = sp.latex(elem)
            latex_parts.append(f"% Element [{idx}]:")
            latex_parts.append(f"$$ {latex_expr} $$")
            latex_parts.append("")

        if self.fitted_coeffs:
            latex_parts.append("% Fitted coefficients:")
            for k, v in self.fitted_coeffs.items():
                latex_parts.append(f"% {k} = {v:.6f}")

        latex_content = "\n".join(latex_parts)

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(latex_content)

        return latex_content


class SymbolicTrainer:
    """
    Trainer for symbolic tensors with multiple fitting algorithms:
    - 'symbolic': Gröbner basis exact solving
    - 'perturbation': 2nd-order perturbation method
    - 'lsq': Least squares numeric
    """

    def __init__(self, nano_tensor: NanoTensor, tolerance: float = 1e-8):
        self.nt = nano_tensor
        self.tolerance = tolerance
        self.fitted_coeffs: Dict[str, float] = {}
        self.kb = KnowledgeBase()

    def fit(self, data: List[Any], method: str = 'symbolic') -> bool:
        """
        Fit tensor to data using specified method.
        For perturbation: data = [(model_R, params_dict)]
        For symbolic/lsq: data = [(state_dict, target_value), ...]
        """
        if method == 'symbolic':
            return self._fit_symbolic(data)
        elif method == 'perturbation':
            if len(data) >= 2:
                model_R, params = data[0], data[1]
                self.nt.full_perturbation(model_R, params)
                self.fitted_coeffs = getattr(self.nt, 'fitted_coeffs', {})
                return len(self.fitted_coeffs) > 0
        elif method == 'lsq':
            return self._fit_lsq(data)

        return False

    def _fit_symbolic(self, data: List[Tuple[Dict[str, float], float]]) -> bool:
        """Exact fitting via Groebner bases"""
        equations = []
        coeffs_sym = self.nt.coeff_vars

        if not coeffs_sym:
            return False

        for state_point, target in data:
            subs_d = {self.nt.base_vars[i]: state_point.get(str(v), 0)
                     for i, v in enumerate(self.nt.base_vars)}
            nt_val = sum(self.nt.subs(subs_d).data.flat)
            equations.append(sp.Eq(nt_val, target))

        sols = self.nt.groebner_solve(equations, coeffs_sym)
        if sols:
            sol_dict = {k: float(v.evalf()) for k, v in sols[0].items()}
            self._apply_solution(sol_dict)
            return True
        return False

    def _fit_lsq(self, data: List[Tuple[Dict[str, float], float]]) -> bool:
        """Least squares numeric fitting"""
        A, b = [], []
        coeffs_sym = self.nt.coeff_vars

        for state_point, target in data:
            row = []
            for coeff in coeffs_sym:
                basis = sp.zeros(1)
                for i, v in enumerate(self.nt.base_vars):
                    if f'g_{v.name}' == coeff.name:
                        basis += state_point.get(str(v), 0)
                row.append(float(basis.evalf()))
            A.append(row)
            b.append(float(target))

        coeffs_num = np.linalg.lstsq(np.array(A), np.array(b), rcond=None)[0]
        sol_dict = {c.name: coeffs_num[i] for i, c in enumerate(coeffs_sym)}
        self._apply_solution(sol_dict)
        return True

    def _apply_solution(self, sol_dict: Dict[str, float]):
        """Apply fitted coefficients to tensor and knowledge base"""
        subs_d = {sp.Symbol(k): v for k, v in sol_dict.items()}
        self.nt = self.nt.subs(subs_d)
        self.fitted_coeffs = sol_dict

        for k, v in sol_dict.items():
            self.kb.add_fact('policy_coefficient', k, v)

    def predict(self, state_point: Dict[str, float]) -> np.ndarray:
        """Make prediction at given state"""
        return self.nt.eval_numeric(state_point)


class HybridTrainer(SymbolicTrainer):
    """Hybrid trainer combining symbolic and numeric methods"""

    def symbolic_regression(self, X: np.ndarray, y: np.ndarray,
                           max_deg: int = 5) -> NanoTensor:
        """Symbolic regression via GP optimization."""
        if not SKOPT_AVAILABLE:
            # Fallback without optimization
            return NanoTensor((1,), max_order=2,
                             base_vars=[f'x{i}' for i in range(X.shape[1])])

        def objective(deg):
            nt_try = NanoTensor((1,), max_order=int(deg[0]),
                               base_vars=[f'x{i}' for i in range(X.shape[1])])
            nt_try.generate_taylor({f'x{i}': 0 for i in range(X.shape[1])})
            trainer_try = HybridTrainer(nt_try)

            data = []
            for j in range(len(y)):
                state = {f'x{i}': X[j,i] for i in range(X.shape[1])}
                data.append((state, y[j]))

            trainer_try.fit(data, method='lsq')
            pred = trainer_try.predict_batch(X)
            return np.mean((pred - y)**2)

        res = gp_minimize(objective, [(-2, max_deg)], n_calls=30, random_state=42)
        best_nt = NanoTensor((1,), max_order=int(res.x[0]),
                            base_vars=[f'x{i}' for i in range(X.shape[1])])
        best_nt.generate_taylor({f'x{i}': 0 for i in range(X.shape[1])})

        return best_nt

    def predict_batch(self, X: np.ndarray) -> np.ndarray:
        """Batch prediction for numeric data"""
        return np.array([self.predict({f'x{i}': X[j,i] for i in range(X.shape[1])}).flat[0]
                        for j in range(len(X))])

    def multi_obj_fit(self, sparse_data: List, dense_data: np.ndarray,
                     alpha_exact: float = 0.7):
        """Pareto optimization: combine symbolic (sparse) and numeric (dense)."""
        if dense_data.shape[0] > 0:
            X, y = dense_data[:, :-1], dense_data[:, -1]
            nt_dense = self.symbolic_regression(X, y)
            trainer_dense = HybridTrainer(nt_dense)
            trainer_dense.fit([({f'x{i}': X[j,i] for i in range(X.shape[1])}, y[j])
                              for j in range(len(y))], 'lsq')
        else:
            trainer_dense = self

        trainer_sparse = HybridTrainer(self.nt)
        trainer_sparse.fit(sparse_data, 'symbolic')

        all_keys = set(list(trainer_sparse.fitted_coeffs.keys()) +
                      list(trainer_dense.fitted_coeffs.keys()))

        for k in all_keys:
            val_sparse = trainer_sparse.fitted_coeffs.get(k, 0)
            val_dense = trainer_dense.fitted_coeffs.get(k, 0)
            self.fitted_coeffs[k] = alpha_exact * val_sparse + (1 - alpha_exact) * val_dense

        self._apply_solution(self.fitted_coeffs)

    def torch_fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        epochs: int = 100,
        learning_rate: float = 0.01,
        batch_size: int = 32,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Fit tensor coefficients using PyTorch gradient descent.

        This provides neural network-style optimization for cases where
        symbolic or least-squares methods are insufficient.

        Args:
            X: Input features array of shape (n_samples, n_features)
            y: Target values array of shape (n_samples,)
            epochs: Number of training epochs
            learning_rate: Learning rate for optimizer
            batch_size: Mini-batch size
            verbose: Print training progress

        Returns:
            Dictionary with training history and final coefficients

        Raises:
            ImportError: If PyTorch is not available
        """
        if not TORCH_AVAILABLE:
            raise ImportError(
                "PyTorch is required for torch_fit. "
                "Install with: pip install torch"
            )

        import torch
        import torch.nn as nn
        import torch.optim as optim

        # Convert to torch tensors
        X_tensor = torch.tensor(X, dtype=torch.float32)
        y_tensor = torch.tensor(y, dtype=torch.float32).unsqueeze(1)

        n_features = X.shape[1]
        n_coeffs = len(self.nt.coeff_vars)

        if n_coeffs == 0:
            # Generate Taylor expansion if not already done
            center = {f'x{i}': 0.0 for i in range(n_features)}
            self.nt.generate_taylor(center)
            n_coeffs = len(self.nt.coeff_vars)

        # Create a simple linear model for coefficient learning
        class CoeffModel(nn.Module):
            def __init__(self, n_features, n_coeffs):
                super().__init__()
                # Map from input features to coefficient contributions
                self.linear = nn.Linear(n_features, 1, bias=True)
                # Learnable coefficients
                self.coeffs = nn.Parameter(torch.zeros(n_coeffs))

            def forward(self, x):
                # Simple linear combination
                base = self.linear(x)
                # Add polynomial terms based on coefficients
                poly_terms = torch.zeros_like(base)
                for i, coeff in enumerate(self.coeffs):
                    if i < x.shape[1]:
                        poly_terms += coeff * x[:, i:i+1]
                    elif i < 2 * x.shape[1]:
                        idx = i - x.shape[1]
                        poly_terms += coeff * (x[:, idx:idx+1] ** 2)
                return base + poly_terms

        model = CoeffModel(n_features, n_coeffs)
        optimizer = optim.Adam(model.parameters(), lr=learning_rate)
        criterion = nn.MSELoss()

        # Training history
        history = {'loss': [], 'epochs': epochs}

        # Training loop
        n_samples = X_tensor.shape[0]
        for epoch in range(epochs):
            model.train()

            # Mini-batch training
            indices = torch.randperm(n_samples)
            epoch_loss = 0.0
            n_batches = 0

            for i in range(0, n_samples, batch_size):
                batch_idx = indices[i:i+batch_size]
                X_batch = X_tensor[batch_idx]
                y_batch = y_tensor[batch_idx]

                optimizer.zero_grad()
                predictions = model(X_batch)
                loss = criterion(predictions, y_batch)
                loss.backward()
                optimizer.step()

                epoch_loss += loss.item()
                n_batches += 1

            avg_loss = epoch_loss / max(n_batches, 1)
            history['loss'].append(avg_loss)

            if verbose and (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch+1}/{epochs} - Loss: {avg_loss:.6f}")

        # Extract fitted coefficients
        model.eval()
        with torch.no_grad():
            learned_coeffs = model.coeffs.numpy()

        # Map back to symbolic coefficients
        for i, coeff_var in enumerate(self.nt.coeff_vars):
            if i < len(learned_coeffs):
                self.fitted_coeffs[coeff_var.name] = float(learned_coeffs[i])

        # Apply to tensor
        self._apply_solution(self.fitted_coeffs)

        history['final_loss'] = history['loss'][-1] if history['loss'] else 0.0
        history['coefficients'] = self.fitted_coeffs.copy()

        return history


class KnowledgeBase:
    """Symbolic knowledge base using graph and logic programming"""

    def __init__(self):
        if NETWORKX_AVAILABLE:
            self.graph = nx.DiGraph()
        else:
            self.graph = None
            self._facts = {}

        if KANREN_AVAILABLE:
            self.rules = Relation('policy')
        else:
            self.rules = None

    def add_fact(self, entity: str, prop: str, value: Any):
        """Add fact to KB"""
        if self.graph is not None:
            self.graph.add_edge(entity, prop, value=float(value))
        else:
            key = (entity, prop)
            self._facts[key] = value

        if KANREN_AVAILABLE and self.rules is not None:
            facts(self.rules, (entity, prop, value))

    def query(self, entity: str, prop: str = None) -> List[Any]:
        """Query KB for entity/property"""
        if KANREN_AVAILABLE and self.rules is not None and prop:
            q = kvar()
            results = run(5, q, self.rules(entity, prop, q))
            return [float(r) for r in results]
        elif self.graph is not None:
            if prop:
                if self.graph.has_edge(entity, prop):
                    return [self.graph.edges[entity, prop].get('value')]
            else:
                if self.graph.has_node(entity):
                    return list(self.graph.out_edges(entity, data=True))
        else:
            # Fallback to simple dict
            if prop:
                key = (entity, prop)
                if key in self._facts:
                    return [self._facts[key]]
            else:
                return [(e, p, v) for (e, p), v in self._facts.items() if e == entity]
        return []
