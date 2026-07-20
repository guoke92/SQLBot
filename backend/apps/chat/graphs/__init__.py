"""Chat conversation graphs (analysis, predict, recommend, nlq).

Builders register into conversation.registry on import of this package.
Product code launches them only via ``conversation.runtime.submit_graph``.
"""

from apps.chat.graphs import analysis as _analysis  # noqa: F401
from apps.chat.graphs import nlq as _nlq  # noqa: F401
from apps.chat.graphs import predict as _predict  # noqa: F401
from apps.chat.graphs import recommend as _recommend  # noqa: F401

__all__ = ["analysis", "nlq", "predict", "recommend"]
