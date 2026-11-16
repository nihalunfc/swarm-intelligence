"""Universal swarm study: one feature set and one general equation across many real swarms.

Author: Nihal. MIT license. See docs/universal-swarm/README.md.

Every dataset is loaded into the same three shapes (``Tracks``, ``Series``, ``Events``),
the same dimensionless features are measured on each, and one general adaptive-swarm
equation is fitted to all of them. Only real recorded data is used as evidence; the
unit tests use tiny synthetic arrays only to check the code.
"""
