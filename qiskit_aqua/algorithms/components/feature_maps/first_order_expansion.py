# -*- coding: utf-8 -*-

# Copyright 2018 IBM.
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
# =============================================================================
"""
This module contains the definition of a base class for
feature map. Several types of commonly used approaches.
"""


import numpy as np
from qiskit import CompositeGate, QuantumCircuit, QuantumRegister
from qiskit.extensions.standard.u1 import U1Gate
from qiskit.extensions.standard.u2 import U2Gate

from qiskit_aqua.algorithms.components.feature_maps import FeatureMap


class FirstOrderExpansion(FeatureMap):
    """
    Mapping data with the first order expansion without entangling gates.
    Refer to https://arxiv.org/pdf/1804.11326.pdf for details.
    """

    FIRST_ORDER_EXPANSION_CONFIGURATION = {
        'name': 'FirstOrderExpansion',
        'description': 'First order expansion for feature map',
        'input_schema': {
            '$schema': 'http://json-schema.org/schema#',
            'id': 'First_Order_Expansion_schema',
            'type': 'object',
            'properties': {
                'depth': {
                    'type': 'integer',
                    'default': 2,
                    'minimum': 1
                }
            },
            'additionalProperties': False
        }
    }

    def __init__(self, configuration=None):
        super().__init__(configuration or self.FIRST_ORDER_EXPANSION_CONFIGURATION.copy())
        self._ret = {}

    def init_args(self, num_qubits, depth, entangler_map=None, entanglement='full'):
        self._num_qubits = num_qubits
        self._depth = depth

    def _build_composite_gate(self, x, qr):
        composite_gate = CompositeGate("first_order_expansion",
                                       [], [qr[i] for i in range(self._num_qubits)])

        for _ in range(self._depth):
            for i in range(x.shape[0]):
                composite_gate._attach(U2Gate(0, np.pi, qr[i]))
                composite_gate._attach(U1Gate(2 * x[i], qr[i]))

        return composite_gate

    def construct_circuit(self, x, qr=None, inverse=False):
        """
        Construct the first order expansion based on given data.

        Args:
            x (numpy.ndarray): 1-D to-be-transformed data.
            qr (QauntumRegister): the QuantumRegister object for the circuit, if None,
                                  generate new registers with name q.
            inverse (bool): whether or not inverse the circuit

        Returns:
            QuantumCircuit: a quantum circuit transform data x.
        """
        if not isinstance(x, np.ndarray):
            raise TypeError("x should be numpy array.")
        if x.ndim != 1:
            raise ValueError("x should be 1-D array.")
        if x.shape[0] != self._num_qubits:
            raise ValueError("number of qubits and data dimension must be the same.")

        if qr is None:
            QuantumRegister(self._num_qubits, 'q')
        qc = QuantumCircuit(qr)
        composite_gate = self._build_composite_gate(x, qr)
        qc._attach(composite_gate if not inverse else composite_gate.inverse())

        return qc
