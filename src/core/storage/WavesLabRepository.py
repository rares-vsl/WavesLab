from typing import Dict, List, Optional
import logging
import json
from pathlib import Path

from core.model.NodeStatus import NodeStatus
from core.model.VirtualUser import VirtualUser
from core.model.WaveNode import WaveNode
import os
from threading import Lock

logger = logging.getLogger(__name__)

class WavesLabRepository:
    """Repository for WaveNodes and VirtualUsers with JSON persistence."""

    def __init__(self, data_dir: str = "core/storage/"):
        self._data_dir = Path(data_dir)
        # Use .json files as requested
        self._nodes_file = self._data_dir / "nodes.json"
        self._users_file = self._data_dir / "users.json"

        # Do NOT create directories or seed data. Only use existing data.
        # Validate presence early to avoid surprising behavior later.
        if not self._users_file.exists():
            raise FileNotFoundError(f"Users file not found: {self._users_file}")
        if not self._nodes_file.exists():
            raise FileNotFoundError(f"Nodes file not found: {self._nodes_file}")

        # Single lock for all operations
        self._lock = Lock()

    # ---------------------------
    # Low-level JSON I/O helpers
    # ---------------------------

    def _read_json(self, path: Path):
        with open(path, "r", encoding="utf-8") as fp:
            return json.load(fp)

    def _write_json_atomic(self, path: Path, data):
        """
        Atomic write: write to a temp file in the same dir,
        fsync it, then os.replace to ensure atomic swap.
        """
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        with open(tmp_path, "w", encoding="utf-8") as tf:
            json.dump(data, tf, indent=2)
            tf.flush()
            os.fsync(tf.fileno())
        # Atomic replace
        os.replace(tmp_path, path)

    # ---------------------------
    # Load/Save domain objects
    # ---------------------------

    def _load_users(self) -> Dict[str, VirtualUser]:
        """Load users from users.json."""
        try:
            users_data = self._read_json(self._users_file)
            users: Dict[str, VirtualUser] = {}
            for user_dict in users_data:
                user = VirtualUser(**user_dict)
                users[user.username] = user
            logger.debug("Loaded %d users from %s", len(users), self._users_file)
            return users
        except Exception as e:
            logger.error("Error loading users: %s", e)
            return {}

    def _load_nodes(self) -> Dict[str, WaveNode]:
        """Load nodes from nodes.json."""
        try:
            nodes_data = self._read_json(self._nodes_file)
            nodes: Dict[str, WaveNode] = {}
            for node_dict in nodes_data:
                # Normalize nullable endpoint_url
                if node_dict.get("endpoint_url") is None:
                    node_dict["endpoint_url"] = ""

                # Normalize enums to lowercase strings if present
                if isinstance(node_dict.get("status"), str):
                    node_dict["status"] = node_dict["status"].lower()
                if isinstance(node_dict.get("node_type"), str):
                    node_dict["node_type"] = node_dict["node_type"].lower()

                node = WaveNode(**node_dict)
                nodes[node.id] = node
            logger.debug("Loaded %d nodes from %s", len(nodes), self._nodes_file)
            return nodes
        except Exception as e:
            logger.error("Error loading nodes: %s", e)
            return {}

    def _save_users(self, users: Dict[str, VirtualUser]):
        """Save users to users.json atomically."""
        try:
            users_data = [{"username": user.username} for user in users.values()]
            self._write_json_atomic(self._users_file, users_data)
            logger.debug("Saved %d users to %s", len(users_data), self._users_file)
        except Exception as e:
            logger.error("Error saving users: %s", e)

    def _save_nodes(self, nodes: Dict[str, WaveNode]):
        """Save nodes to nodes.json atomically."""
        try:
            nodes_data = []
            for node in nodes.values():
                nodes_data.append(
                    {
                        'name': node.name,
                        'id': node.id,
                        'node_type': node.node_type.name,
                        'status': node.status.name,
                        'provision_rate': node.provision_rate,
                        'endpoint_url': node.endpoint_url,
                        'assigned_user': node.assigned_user
                    }
                )
            self._write_json_atomic(self._nodes_file, nodes_data)
            logger.debug("Saved %d nodes to %s", len(nodes_data), self._nodes_file)
        except Exception as e:
            logger.error("Error saving nodes: %s", e)

    # ---------------------------
    # Node operations
    # ---------------------------

    def get_all_nodes(self) -> List[WaveNode]:
        """Get all WaveNodes."""
        with self._lock:
            nodes = self._load_nodes()
            return list(nodes.values())

    def get_node_by_id(self, node_id: str) -> Optional[WaveNode]:
        """Get a WaveNode by its ID."""
        with self._lock:
            nodes = self._load_nodes()
            return nodes.get(node_id)

    def get_node_by_name(self, node_name: str) -> Optional[WaveNode]:
        """Get a WaveNode by its name."""
        with self._lock:
            nodes = self._load_nodes()
            for node in nodes.values():
                if node.name == node_name:
                    return node
            return None

    def update_node_endpoint(self, node_id: str, endpoint_url: str) -> Optional[WaveNode]:
        """Update a node's endpoint URL."""
        with self._lock:
            nodes = self._load_nodes()
            node = nodes.get(node_id)
            if not node:
                return None
            node.endpoint_url = endpoint_url
            nodes[node_id] = node
            self._save_nodes(nodes)
            logger.info("Updated endpoint for node %s to %s", node_id, endpoint_url)
            return node

    def start_node(self, node_id: str, user_name: Optional[str] = None) -> tuple[bool, str]:
        """
        Start a WaveNode by ID.

        Returns:
            Tuple of (success: bool, message: str)
        """
        with self._lock:
            nodes = self._load_nodes()
            node = nodes.get(node_id)

            if not node:
                return False, f"Node '{node_id}' not found"

            if node.status == NodeStatus.ON:
                return True, "already running"

            # Validate user if specified
            if user_name:
                users = self._load_users()
                if user_name not in users:
                    return False, f"User '{user_name}' not found"
                node.assigned_user = user_name

            node.status = NodeStatus.ON
            nodes[node_id] = node
            self._save_nodes(nodes)
            logger.info("Started node '%s'%s", node_id, f" with user '{user_name}'" if user_name else "")
            return True, f"Node '{node_id}' started successfully"

    def stop_node(self, node_id: str) -> tuple[bool, str]:
        """
        Stop a WaveNode by ID.

        Returns:
            Tuple of (success: bool, message: str)
        """
        with self._lock:
            nodes = self._load_nodes()
            node = nodes.get(node_id)

            if not node:
                return False, f"Node '{node_id}' not found"

            if node.status == NodeStatus.OFF:
                return True, "already stopped"

            node.status = NodeStatus.OFF
            node.assigned_user = None
            nodes[node_id] = node
            self._save_nodes(nodes)
            logger.info("Stopped node '%s'", node_id)
            return True, f"Node '{node_id}' stopped successfully"

    def get_active_nodes(self) -> List[WaveNode]:
        """Get all active (status=on) WaveNodes."""
        with self._lock:
            nodes = self._load_nodes()
            return [node for node in nodes.values() if node.status == NodeStatus.ON]

    # ---------------------------
    # User operations
    # ---------------------------

    def get_all_users(self) -> List[VirtualUser]:
        """Get all VirtualUsers."""
        with self._lock:
            users = self._load_users()
            return list(users.values())

    def get_user_by_username(self, username: str) -> Optional[VirtualUser]:
        """Get a VirtualUser by username."""
        with self._lock:
            users = self._load_users()
            return users.get(username)

repository = WavesLabRepository()